import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import GreetingAgentExecutor, MathAgentExecutor


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle tenant-based routing/filtering.
    Example: 
    - If tenant is 'redhat', they can't access the 'math' agent.
    - If tenant is 'ibm', they can access everything.
    """
    async def dispatch(self, request, call_next):
        tenant = request.headers.get("x-tenant-id", "guest")
        path = request.url.path
        
        print(f"Incoming request from Tenant: {tenant} for Path: {path}")

        # Example logic for ibm vs redhat
        if tenant == "redhat" and "/math" in path:
            return JSONResponse(
                {"error": "Forbidden: redhat tenant does not have access to Math Agent"}, 
                status_code=403
            )
            
        return await call_next(request)


def create_greeting_app():
    skill = AgentSkill(
        id="hello_world",
        name="Greet",
        description="Return a greeting",
        tags=["greeting", "hello", "world"],
        examples=["Hey", "Hello", "Hi"],
    )
    agent_card = AgentCard(
        name="Greeting Agent",
        description="A simple agent that returns a greeting",
        url="http://localhost:8000/greeting/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )
    request_handler = DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(http_handler=request_handler, agent_card=agent_card)


def create_math_app():
    skill = AgentSkill(
        id="math_skill",
        name="Math",
        description="Perform simple math",
        tags=["math", "addition"],
        examples=["What is 1+1?"],
    )
    agent_card = AgentCard(
        name="Math Agent",
        description="A simple agent that does math",
        url="http://localhost:8000/math/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )
    request_handler = DefaultRequestHandler(
        agent_executor=MathAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(http_handler=request_handler, agent_card=agent_card)


# Combine everything into a single Starlette Hub
middleware = [Middleware(TenantMiddleware)]
app = Starlette(
    routes=[
        Mount("/greeting", app=create_greeting_app().build()),
        Mount("/math", app=create_math_app().build()),
    ],
    middleware=middleware,
)

if __name__ == "__main__":
    print("Starting Agent Hub on http://localhost:8000")
    print("Greeting Agent at /greeting")
    print("Math Agent at /math")
    uvicorn.run(app, host="0.0.0.0", port=8000)