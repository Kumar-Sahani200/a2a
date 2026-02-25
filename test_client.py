import uuid

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
BASE_URL = "http://localhost:9999"


async def call_agent(base_url: str, message_text: str):
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        print(f"\n--- Interacting with agent at {base_url} ---")
        try:
            agent_card = await resolver.get_agent_card()
            print(f"Fetched card for: {agent_card.name}")
        except Exception as e:
            print(f"Error fetching agent card from {base_url}: {e}")
            return

        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
        
        message_payload = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text=message_text))],
        )
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=message_payload,
            ),
        )
        
        print(f"Sending message: '{message_text}'")
        response = await client.send_message(request)
        print("Response:")
        print(response.model_dump_json(indent=2))


async def main() -> None:
    # Use different messages for different agents to see their unique responses
    await call_agent("http://localhost:9999", "Hello!")
    await call_agent("http://localhost:9998", "What is 1+1?")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())