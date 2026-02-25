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


async def call_agent(base_url: str, message_text: str, tenant_id: str = "ibm"):
    # Industry Standard: Pass headers to the base HTTP client
    async with httpx.AsyncClient(headers={"x-tenant-id": tenant_id}) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        print(f"\n--- Interacting with agent at {base_url} (Tenant: {tenant_id}) ---")
        try:
            # All requests via this httpx_client now include the 'x-tenant-id' header
            agent_card = await resolver.get_agent_card()
            print(f"Fetched card for: {agent_card.name}")
        except Exception as e:
            # If the middleware blocks the call, we'll hit this exception
            print(f"Access Denied or Error: {e}")
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
        # send_message will now use the underlying httpx_client which has the headers
        response = await client.send_message(request)
        print("Response:")
        print(response.model_dump_json(indent=2))



async def main() -> None:
    # 1. ibm tenant can access everything
    await call_agent("http://localhost:8000/greeting", "Hello from ibm!", tenant_id="ibm")
    await call_agent("http://localhost:8000/math", "1+1 please", tenant_id="ibm")

    # 2. redhat tenant is restricted from Math
    print("\n\n>>> TESTING RESTRICTED ACCESS FOR redhat <<<")
    await call_agent("http://localhost:8000/math", "I want math", tenant_id="redhat")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())