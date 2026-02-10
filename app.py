from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import requests
import os
import asyncio

from dotenv import load_dotenv

from parlant_engine import init_parlant, server, agent
from sessions import get_session

# ==================================================
# ENV + CONFIG
# ==================================================
load_dotenv()

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

GRAPH_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

# ==================================================
# FASTAPI APP
# ==================================================
app = FastAPI(title="WhatsApp + Parlant SDK")

# ==================================================
# START PARLANT SERVER ON APP START
# ==================================================
@app.on_event("startup")
async def startup():
    await init_parlant()
    print("✅ Parlant engine initialized")

# ==================================================
# META WEBHOOK VERIFICATION
# ==================================================
@app.get("/")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge, status_code=200)

    return PlainTextResponse("Verification failed", status_code=403)

# ==================================================
# START CONVERSATION (SEND FIRST TEMPLATE)
# ==================================================
@app.post("/start")
def start(phone: str = Query(..., description="Phone number with country code")):
    send_initial_template(phone)
    return {"status": "template_sent"}

# ==================================================
# RECEIVE WHATSAPP MESSAGES
# ==================================================
@app.post("/")
async def webhook(request: Request):
    payload = await request.json()
    value = payload["entry"][0]["changes"][0]["value"]

    # Ignore delivery receipts, status updates, etc.
    if "messages" not in value:
        return {"status": "ignored"}

    msg = value["messages"][0]
    phone = msg["from"]
    text = msg["text"]["body"]

    # --------------------------------------------------
    # GET PARLANT SESSION (SESSION ID = whatsapp:<phone>)
    # --------------------------------------------------
    session = get_session(server, agent, phone)

    # --------------------------------------------------
    # SEND MESSAGE INTO PARLANT JOURNEY
    # --------------------------------------------------
    response = await session.send_user_message(text)

    # --------------------------------------------------
    # SEND WHATSAPP REPLY
    # --------------------------------------------------
    send_text(phone, response.text)

    return {"status": "ok"}

# ==================================================
# SEND INITIAL WHATSAPP TEMPLATE
# ==================================================
def send_initial_template(phone: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "lad_telephony",
            "language": {"code": "en"}
        }
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    resp = requests.post(GRAPH_API_URL, headers=headers, json=payload)
    print("TEMPLATE STATUS:", resp.status_code)
    print("TEMPLATE BODY:", resp.text)

# ==================================================
# SEND NORMAL WHATSAPP TEXT
# ==================================================
def send_text(to: str, text: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    resp = requests.post(GRAPH_API_URL, headers=headers, json=payload)
    print("TEXT STATUS:", resp.status_code)
    print("TEXT BODY:", resp.text)
