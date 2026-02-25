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
BASE_URL = "http://localhost:8000"


async def discover_agents(tenant_id: str):
    """
    Calls the central Hub to find out which agents this tenant is allowed to use.
    """
    async with httpx.AsyncClient(headers={"x-tenant-id": tenant_id}) as httpx_client:
        print(f"\n>>> DISCOVERING AGENTS FOR TENANT: {tenant_id} <<<")
        try:
            resp = await httpx_client.get(f"{BASE_URL}/discovery")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Available agents for {data['tenant']}:")
                for agent in data['available_agents']:
                    print(f"- {agent['name']} (Path: {agent['path']})")
                return data['available_agents']
            else:
                print(f"Discovery failed: {resp.status_code}")
        except Exception as e:
            print(f"Error during discovery: {e}")
    return []


async def call_agent(base_url: str, message_text: str, tenant_id: str = "ibm"):
    """
    Generic function to call an agent at a specific URL.
    """
    async with httpx.AsyncClient(headers={"x-tenant-id": tenant_id}) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        print(f"\n--- Interacting with agent at {base_url} (Tenant: {tenant_id}) ---")
        try:
            agent_card = await resolver.get_agent_card()
            print(f"Fetched card for: {agent_card.name}")
        except Exception as e:
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
        response = await client.send_message(request)
        print("Response:")
        print(response.model_dump_json(indent=2))


async def main() -> None:
    # 1. Discovery phase
    await discover_agents("ibm")
    await discover_agents("redhat")

    # 2. Interaction phase - ibm tenant can access everything
    print("\n--- IBM INTERACTIONS ---")
    await call_agent(f"{BASE_URL}/greeting", "Hello from ibm!", tenant_id="ibm")
    await call_agent(f"{BASE_URL}/math", "1+1 please", tenant_id="ibm")

    # 3. Interaction phase - redhat tenant is restricted from Math
    print("\n--- REDHAT INTERACTIONS ---")
    await call_agent(f"{BASE_URL}/greeting", "Hello from redhat!", tenant_id="redhat")
    await call_agent(f"{BASE_URL}/math", "I want math", tenant_id="redhat")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())