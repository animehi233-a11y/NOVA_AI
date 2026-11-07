import os
import time
from collections import defaultdict, deque
from typing import Literal

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from google import genai

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")

app = FastAPI(title="NOVA AI")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Simple per-process rate limit for a small demo. It resets when the free host restarts.
requests_by_ip = defaultdict(deque)
RATE_LIMIT = 8
RATE_WINDOW_SECONDS = 60

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(min_length=1, max_length=3000)

class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=12)

@app.get("/")
def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
def health():
    return {"ok": True, "app": "NOVA AI"}

@app.post("/api/chat")
def chat(body: ChatRequest, request: Request):
    now = time.time()
    client_ip = request.client.host if request.client else "unknown"
    recent = requests_by_ip[client_ip]

    while recent and now - recent[0] > RATE_WINDOW_SECONDS:
        recent.popleft()

    if len(recent) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Please wait a minute before sending more messages.")
    recent.append(now)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="The AI service is not configured yet.")

    # Build a short conversation transcript. The API key remains on the server.
    transcript = (
        "You are NOVA AI, a helpful, clear, friendly assistant. "
        "Give safe, age-appropriate answers. Do not claim to create files or videos "
        "unless a connected tool actually did so.\n\n"
    )
    for item in body.messages:
        label = "User" if item.role == "user" else "NOVA AI"
        transcript += f"{label}: {item.text}\n"
    transcript += "\nNOVA AI:"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=transcript,
        )
        answer = (response.text or "").strip()
        if not answer:
            raise RuntimeError("The model returned an empty answer.")
        return {"reply": answer}
    except Exception:
        # Do not send secrets or raw provider error details to the browser.
        raise HTTPException(
            status_code=502,
            detail="NOVA could not reach the AI service. Check the server logs and API settings."
        )
