from multiprocessing import Process

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import GreetingAgentExecutor, MathAgentExecutor


def run_greeting_agent(port: int = 9999):
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
        url=f"http://localhost:{port}/",
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

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print(f"Starting Greeting Agent on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)


def run_math_agent(port: int = 9998):
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
        url=f"http://localhost:{port}/",
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

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    print(f"Starting Math Agent on port {port}")
    uvicorn.run(server.build(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    p1 = Process(target=run_greeting_agent, args=(9999,))
    p2 = Process(target=run_math_agent, args=(9998,))

    p1.start()
    p2.start()

    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()