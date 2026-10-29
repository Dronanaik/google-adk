"""Aria as an ADK Customer Service Management (CSM) Voice Agent: tools + ONE policy door.

Built on the exact architecture of `live-dj/adk_tools/agent.py`:
- `Agent` with plain-function async tools (`lookup_customer`, `lookup_order`,
  `verify_customer_pin`, `issue_refund`, `update_shipping_address`,
  `create_support_ticket`, `escalate_to_human`).
- `Gemini(...)` model carrying `speech_config` so both the custom FastAPI/WebSocket
  UI and `adk web` speak with Aria's voice.
- `before_tool_callback=csm_policy_gate` so every tool call passes through a single
  deterministic policy gate.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from csm_agent.persona import CSM_INSTRUCTION
from csm_agent.policy import csm_policy_gate
from csm_agent.tools import (
    create_support_ticket,
    escalate_to_human,
    issue_refund,
    lookup_customer,
    lookup_order,
    update_shipping_address,
    verify_customer_pin,
)

# Policy lives in CODE (`csm_policy_gate`), not in the persona — so Aria must always
# ATTEMPT the requested tool and let the policy gate decide whether to allow or block.
_POLICY_NOTE = (
    "\n\nIMPORTANT POLICY RULE: Policy enforcement lives in the system's policy gate, "
    "NOT in your persona. Whenever a customer asks to look up an account/order, issue a "
    "refund (of ANY dollar amount or age), or update a shipping address, ALWAYS call the "
    "corresponding tool (`lookup_customer`, `lookup_order`, `issue_refund`, "
    "`update_shipping_address`) first. Never pre-refuse a refund or address change on "
    "your own — call the tool so the policy gate can evaluate and log the verdict. If a "
    "tool call comes back with `result: 'blocked'`, explain the reason warmly in your own "
    "words and offer to create a support ticket or escalate to a human specialist."
)

root_agent = Agent(
    model=Gemini(
        model=os.getenv("LIVE_MODEL", "gemini-3.1-flash-live-preview"),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=os.getenv("LIVE_VOICE", "Aoede")
                )
            )
        ),
    ),
    name="Soumya",
    instruction=CSM_INSTRUCTION + _POLICY_NOTE,
    tools=[
        lookup_customer,
        lookup_order,
        verify_customer_pin,
        issue_refund,
        update_shipping_address,
        create_support_ticket,
        escalate_to_human,
    ],
    before_tool_callback=csm_policy_gate,
)

