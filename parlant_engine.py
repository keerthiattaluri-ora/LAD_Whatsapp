import parlant.sdk as p
from journeys.discovery import discovery_journey
from nlp.groq_service import GroqNLPService

server = None
agent = None
journey = None

async def init_parlant():
    global server, agent, journey

    server = await p.Server(
        nlp_service=lambda container: GroqNLPService(container),
    ).__aenter__()

    agent = await server.create_agent(
        name="Oracle WhatsApp Agent",
        description="WhatsApp assistant using Parlant SDK",
    )

    journey = await discovery_journey(server, agent)
