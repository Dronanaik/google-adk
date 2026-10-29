"""Customer Service Management (CSM) Voice Agent on Google ADK — FastAPI + WebSocket backend.

Built on the exact architecture of `live-dj/adk_tools/server.py`:
  - `LiveRequestQueue` (up) + `runner.run_live()` (down) for full-duplex BIDI audio
  - Plain Python `async def` tools in `csm_agent/tools.py`
  - `csm_policy_gate` (`before_tool_callback`) in `csm_agent/policy.py`
  - `policy_feed()` streams every tool verdict (`ok` or `blocked`) and live CSM state
    snapshot to the browser dashboard immediately.
"""
import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import StreamingMode
from google.adk.runners import RunConfig, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from csm_agent.agent import root_agent
from csm_agent.policy import action_events
from csm_agent.tools import get_store_snapshot, reset_store, to_ui_command

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("csm-voice-agent")

VOICE = os.getenv("LIVE_VOICE", "Aoede")
APP_NAME = "csm-voice-agent"

session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)

RUN_CONFIG = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
        )
    ),
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
)

app = FastAPI(title="csm-voice-agent · NovaMart Support")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
FRONTEND = Path(__file__).resolve().parent / "frontend"
ASSETS = Path(__file__).resolve().parents[1] / "assets"


@app.get("/api/state")
async def api_state():
    """Return the current customer/order store snapshot and active policy settings."""
    return {
        "snapshot": get_store_snapshot(),
        "policy": {
            "max_auto_refund": float(os.getenv("MAX_AUTO_REFUND", "100.0")),
            "strict_refund_window": os.getenv("STRICT_REFUND_WINDOW", "1"),
            "require_pin": os.getenv("REQUIRE_PIN", "0"),
        },
    }


@app.post("/api/reset")
async def api_reset():
    """Reset the in-memory store to initial demo data."""
    reset_store()
    return {"status": "ok", "snapshot": get_store_snapshot()}


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    log.info("ws connected; opening ADK live session (model=%s, voice=%s)", root_agent.model, VOICE)
    session = await session_service.create_session(app_name=APP_NAME, user_id="customer")
    live_request_queue = LiveRequestQueue()

    # Send initial store snapshot on connect so the UI populates immediately
    await websocket.send_text(
        json.dumps({"type": "csm_state", "action": "init", "snapshot": get_store_snapshot()})
    )

    async def upstream():
        # Browser mic (16k PCM) or text prompt -> LiveRequestQueue -> Gemini Live
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                log.info("upstream: browser disconnected")
                return
            raw = msg.get("bytes")
            if raw:
                live_request_queue.send_realtime(
                    types.Blob(data=raw, mime_type="audio/pcm;rate=16000")
                )
            text_data = msg.get("text")
            if text_data:
                try:
                    payload = json.loads(text_data)
                    if payload.get("type") == "text" and payload.get("text"):
                        user_text = payload["text"].strip()
                        await websocket.send_text(
                            json.dumps({"type": "transcript", "role": "user", "text": user_text})
                        )
                        live_request_queue.send_content(
                            types.Content(
                                role="user", parts=[types.Part.from_text(text=user_text)]
                            )
                        )
                except Exception as exc:
                    log.warning("invalid text frame from client: %r", exc)

    async def handle(event):
        it = getattr(event, "input_transcription", None)
        ot = getattr(event, "output_transcription", None)
        if it and getattr(it, "text", None):
            await websocket.send_text(
                json.dumps({"type": "transcript", "role": "user", "text": it.text})
            )
        if ot and getattr(ot, "text", None):
            await websocket.send_text(
                json.dumps({"type": "transcript", "role": "aria", "text": ot.text})
            )
        content = getattr(event, "content", None)
        if content and getattr(content, "parts", None):
            for part in content.parts:
                idata = getattr(part, "inline_data", None)
                if idata and getattr(idata, "data", None):
                    await websocket.send_bytes(idata.data)  # 24 kHz voice
        if getattr(event, "interrupted", None):
            await websocket.send_text(json.dumps({"type": "interrupted"}))

    async def downstream():
        async for event in runner.run_live(
            user_id=session.user_id,
            session_id=session.id,
            live_request_queue=live_request_queue,
            run_config=RUN_CONFIG,
        ):
            await handle(event)

    async def policy_feed():
        # Policy verdicts (from before_tool_callback) -> browser action log + UI state panel
        while True:
            verdict = await action_events.get()
            # Yield briefly so the synchronous tool body completes updating STORE before we snapshot
            await asyncio.sleep(0.01)
            await websocket.send_text(json.dumps({"type": "action", **verdict}))
            if verdict.get("status") == "ok":
                cmd = to_ui_command(verdict["tool"], verdict.get("args") or {})
                if cmd:
                    await websocket.send_text(json.dumps({"type": "csm_state", **cmd}))
            else:
                # Even on a blocked call, sync the active order/customer card in the inspector
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "csm_state",
                            "action": "blocked",
                            "tool": verdict["tool"],
                            "reason": verdict.get("reason", ""),
                            "snapshot": get_store_snapshot(),
                        }
                    )
                )

    while not action_events.empty():
        action_events.get_nowait()

    up = asyncio.create_task(upstream(), name="upstream")
    down = asyncio.create_task(downstream(), name="downstream")
    feed = asyncio.create_task(policy_feed(), name="policy_feed")
    try:
        done, pending = await asyncio.wait({up, down}, return_when=asyncio.FIRST_COMPLETED)
        live_request_queue.close()
        for t in done:
            exc = t.exception()
            if exc:
                log.exception("%s task FAILED: %r", t.get_name(), exc, exc_info=exc)
                try:
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
                    )
                except Exception:
                    pass
        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    except WebSocketDisconnect:
        log.info("ws disconnected")
    finally:
        feed.cancel()
        await asyncio.gather(feed, return_exceptions=True)
        live_request_queue.close()
        log.info("ws closed")


if ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS)), name="assets")
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")

