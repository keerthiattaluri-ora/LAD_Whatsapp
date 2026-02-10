import parlant.sdk as p

async def discovery_journey(server: p.Server, agent: p.Agent) -> p.Journey:
    journey = await agent.create_journey(
        title="WhatsApp Discovery – Oracle Simphony",
        description="Consent → discovery → callback scheduling",
        conditions=["Conversation started"],
    )

    intro = await journey.initial_state.transition_to(
        chat_state=(
            "Hi, I’m Rachel from Oracle. We help restaurants with inventory "
            "and operations. Is it okay if we message you?"
        )
    )

    authorized = await intro.target.transition_to(
        condition="User gives consent",
        chat_state="Great! How are you currently managing inventory at your restaurant?"
    )

    busy = await intro.target.transition_to(
        condition="User says busy or later",
        chat_state="I understand. When would be a better time to reach you?"
    )

    reject = await intro.target.transition_to(
        condition="User rejects",
        chat_state="I understand. Thank you for your time."
    )

    await reject.target.end()

    return journey
