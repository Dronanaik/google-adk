# csm-voice-agent — Customer Service Management Voice Agent on Google ADK

Talk to **Aria**, a live E-Commerce Customer Service Management (CSM) specialist at **NovaMart**. Ask her to look up your customer account or orders, check delivery tracking, reroute a processing shipment, or issue a refund — and interrupt her mid-sentence (barge-in) anytime.

Built on the **Google Agent Development Kit (ADK)** + **Gemini Live API** (`LiveRequestQueue` + `runner.run_live()` + `before_tool_callback` policy gate), modeled directly after `live-dj/adk_tools/`.

---

## Architecture & What's Inside

| File | Responsibility |
|---|---|
| [`csm_agent/agent.py`](csm_agent/agent.py) | Defines `root_agent = Agent(name="aria", ...)` with `Gemini(speech_config=...)` and `before_tool_callback=csm_policy_gate`. |
| [`csm_agent/tools.py`](csm_agent/tools.py) | Plain `async def` ADK tools (`lookup_customer`, `lookup_order`, `verify_customer_pin`, `issue_refund`, `update_shipping_address`, `create_support_ticket`, `escalate_to_human`) + `to_ui_command()` bridge. |
| [`csm_agent/policy.py`](csm_agent/policy.py) | **The CSM Policy Gate** (`before_tool_callback`): observes or blocks tool calls in code before execution and pushes every verdict to `action_events` for the live UI action log. |
| [`csm_agent/server.py`](csm_agent/server.py) | FastAPI + WebSocket (`/ws`) server bridging 16 kHz mic audio and text prompts up (`LiveRequestQueue`) and 24 kHz voice + transcriptions + policy verdicts down (`runner.run_live()` + `policy_feed()`). |
| [`csm_agent/persona.py`](csm_agent/persona.py) | Loads Aria's persona from `assets/aria_persona.txt` and builds `CSM_INSTRUCTION`. |
| [`csm_agent/frontend/`](csm_agent/frontend/) | Live CSM Console: animated Voice Orb, **Customer & Order Inspector** panel, **Policy Gate Action Log**, live transcript, 16 kHz AudioWorklet + client-side barge-in, and one-click sample prompts. |
| [`assets/store_data.json`](assets/store_data.json) | Sample customers (`CUST-101` to `CUST-103`), orders (`ORD-1001` to `ORD-1004`), and support tickets. |
| [`csm_agent/smoke_live.py`](csm_agent/smoke_live.py) | Pre-flight smoke test (`--unit` for instant offline verification, or default for live Gemini model verification). |

---

## Quick Start

```bash
cd csm-voice-agent
uv sync
cp .env.example .env          # paste your GOOGLE_API_KEY (or use the copied .env)

# 1. Run the custom CSM Live Voice Console + Policy Dashboard
uv run uvicorn csm_agent.server:app --port 8000

# 2. Or run with PIN verification required for all order mutations
REQUIRE_PIN=1 uv run uvicorn csm_agent.server:app --port 8000

# 3. Or run inside Google ADK's built-in Dev UI
uv run adk web . --port 8000
```

Open <http://localhost:8000>, put **headphones on**, and tap **🎙 talk** (or click any of the sample prompt chips on the left panel).

---

## Sample Data & Demo Beats

| Scenario | Customer / Order | Try Saying | What Happens |
|---|---|---|---|
| **1. Customer & Order Lookup** | **Alex Rivera** (`CUST-101`, PIN `4210`) · `ORD-1001` | *"Hi Aria, I'm Alex Rivera. Can you check my account and order ORD-1001?"* | `lookup_customer` & `lookup_order` run (`✓ allowed`) → Inspector panel loads Alex's Gold profile and `ORD-1001`. |
| **2. Allowed Auto-Refund ($\le \$100$)** | `ORD-1001` — Ceramic Pour-Over Set (**$48.00**, `delivered` 3 days ago) | *"The coffee carafe in ORD-1001 arrived cracked. Can I get a $48 refund?"* | `issue_refund` passes `csm_policy_gate` (`✓ allowed`) → Order status updates live to **`refunded`**. |
| **3. Policy-Blocked High-Value Refund ($> \$100$)** | `ORD-1002` — Espresso Grinder (**$249.00**, `in_transit`) | *"Can you refund order ORD-1002 for $249?"* | `csm_policy_gate` **BLOCKS** `issue_refund` (`⛔ blocked · exceeds $100 auto-refund limit`) → Aria explains the policy and offers a support ticket or supervisor escalation. |
| **4. Allowed vs. Blocked Address Change** | **Maya Lin** (`CUST-102`) · `ORD-1003` (`processing`) vs. `ORD-1002` (`in_transit`) | *"Update the shipping address on ORD-1003 to 500 Howard St, San Francisco"* | `update_shipping_address` succeeds on `ORD-1003` (`processing`), but is **blocked** by policy on `ORD-1002` (`already in_transit`). |
| **5. Policy-Blocked Expired Return Window** | **Sam Patel** (`CUST-103`) · `ORD-1004` (`delivered` **45 days ago**) | *"Can I get a refund on order ORD-1004?"* | `csm_policy_gate` **BLOCKS** `issue_refund` (`⛔ blocked · past 30-day return window (45d)`). |

---

## Testing

```bash
# Instant offline unit + policy gate check (<50ms)
uv run python csm_agent/smoke_live.py --unit

# Full end-to-end live Gemini model smoke test (no mic needed)
uv run python csm_agent/smoke_live.py
```

