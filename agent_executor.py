from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel


class GreetingAgent(BaseModel):
    """Greeting agent that returns a greeting"""

    async def invoke(self) -> str:
        return "Hello there! Kumar here! I'm trying to understand how a2a works here"


class GreetingAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = GreetingAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")


class MathAgent(BaseModel):
    """Simple math agent"""

    async def invoke(self) -> str:
        return "I am the Math Agent! I can tell you that 1 + 1 = 2."


class MathAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = MathAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")