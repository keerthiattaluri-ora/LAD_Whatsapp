PARLANT_SESSIONS = {}

def get_session(server, agent, phone: str):
    if phone not in PARLANT_SESSIONS:
        PARLANT_SESSIONS[phone] = server.create_session(
            agent=agent,
            metadata={"channel": "whatsapp", "phone": phone}
        )
    return PARLANT_SESSIONS[phone]
