"""Live + Offline smoke test for the CSM Voice Agent — no mic needed.

Mirrors `live-dj/adk_tools/smoke_live.py`:
Drives Aria through three CSM turns and checks the policy verdicts and UI commands:
  1. Customer & Order Lookup: "Hi Aria, I'm Alex Rivera, can you check my order ORD-1001?"
     -> lookup_customer / lookup_order runs (allowed)
  2. Allowed Refund (<= $100): "Please issue a $48 refund for order ORD-1001, the carafe arrived cracked."
     -> issue_refund runs (allowed, status updated to 'refunded')
  3. Blocked Refund (> $100 policy gate): "Please issue a $249 refund for order ORD-1002."
     -> csm_policy_gate BLOCKS issue_refund (exceeds $100 auto-refund limit)

Run from the repo root:
  uv run python csm_agent/smoke_live.py          # full live Gemini test
  uv run python csm_agent/smoke_live.py --unit   # instant local unit/policy gate verification
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from csm_agent.policy import action_events, csm_policy_gate
from csm_agent.tools import (
    find_order,
    issue_refund,
    lookup_customer,
    lookup_order,
    reset_store,
    to_ui_command,
    update_shipping_address,
    verify_customer_pin,
)


class _DummyTool:
    def __init__(self, name: str):
        self.name = name


async def run_unit_checks() -> int:
    """Deterministic unit verification of tools + policy gate (runs offline in <50ms)."""
    print("=== Running deterministic CSM unit & policy gate checks ===")
    reset_store()
    os.environ["MAX_AUTO_REFUND"] = "100.0"
    os.environ["STRICT_REFUND_WINDOW"] = "1"
    os.environ["REQUIRE_PIN"] = "0"

    while not action_events.empty():
        action_events.get_nowait()

    # 1. Customer & Order Lookup
    v1 = await csm_policy_gate(_DummyTool("lookup_customer"), {"query": "Alex Rivera"}, None)
    res1 = await lookup_customer("Alex Rivera")
    v2 = await csm_policy_gate(_DummyTool("lookup_order"), {"order_id": "ORD-1001"}, None)
    res2 = await lookup_order("ORD-1001")
    cmd1 = to_ui_command("lookup_order", {"order_id": "ORD-1001"})
    ok1 = (
        v1 is None
        and res1["result"] == "ok"
        and v2 is None
        and res2["result"] == "ok"
        and cmd1 is not None
        and cmd1["snapshot"]["active_order"]["order_id"] == "ORD-1001"
    )

    # 2. Allowed refund ($48.00 <= $100.00 on ORD-1001)
    v3 = await csm_policy_gate(
        _DummyTool("issue_refund"),
        {"order_id": "ORD-1001", "amount": 48.0, "reason": "Cracked carafe"},
        None,
    )
    res3 = await issue_refund("ORD-1001", 48.0, "Cracked carafe") if v3 is None else v3
    ok2 = v3 is None and res3["result"] == "ok" and find_order("ORD-1001")["status"] == "refunded"

    # 3. Blocked high-value refund ($249.00 > $100.00 on ORD-1002)
    v4 = await csm_policy_gate(
        _DummyTool("issue_refund"),
        {"order_id": "ORD-1002", "amount": 249.0, "reason": "Changed mind"},
        None,
    )
    ok3 = (
        isinstance(v4, dict)
        and v4.get("result") == "blocked"
        and find_order("ORD-1002")["status"] == "in_transit"
    )

    # 4. Blocked shipping address change on already-shipped order (ORD-1002) vs allowed on processing (ORD-1003)
    v5 = await csm_policy_gate(
        _DummyTool("update_shipping_address"),
        {"order_id": "ORD-1002", "new_address": "999 Main St"},
        None,
    )
    v6 = await csm_policy_gate(
        _DummyTool("update_shipping_address"),
        {"order_id": "ORD-1003", "new_address": "500 Howard St, San Francisco, CA"},
        None,
    )
    res6 = (
        await update_shipping_address("ORD-1003", "500 Howard St, San Francisco, CA")
        if v6 is None
        else v6
    )
    ok4 = (
        isinstance(v5, dict)
        and v5.get("result") == "blocked"
        and v6 is None
        and res6["result"] == "ok"
    )

    # 5. PIN verification gate when REQUIRE_PIN=1
    os.environ["REQUIRE_PIN"] = "1"
    v7 = await csm_policy_gate(
        _DummyTool("update_shipping_address"),
        {"order_id": "ORD-1003", "new_address": "100 First St"},
        None,
    )
    await verify_customer_pin("CUST-102", "9821")
    v8 = await csm_policy_gate(
        _DummyTool("update_shipping_address"),
        {"order_id": "ORD-1003", "new_address": "100 First St"},
        None,
    )
    os.environ["REQUIRE_PIN"] = "0"
    ok5 = isinstance(v7, dict) and v7.get("result") == "blocked" and v8 is None

    print("  1 customer & order lookup:         ", "PASS" if ok1 else "FAIL")
    print("  2 allowed refund (ORD-1001 $48):   ", "PASS" if ok2 else "FAIL")
    print("  3 blocked high refund (ORD-1002):  ", "PASS" if ok3 else "FAIL")
    print("  4 shipping address policy gate:    ", "PASS" if ok4 else "FAIL")
    print("  5 customer PIN security gate:      ", "PASS" if ok5 else "FAIL")
    reset_store()
    return 0 if (ok1 and ok2 and ok3 and ok4 and ok5) else 1


async def main():
    if "--unit" in sys.argv:
        return await run_unit_checks()

    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    from google.adk.agents import LiveRequestQueue
    from google.adk.agents.run_config import StreamingMode
    from google.adk.runners import RunConfig, Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from csm_agent.agent import root_agent

    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"],
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )
    session_service = InMemorySessionService()
    runner = Runner(app_name="smoke-csm", agent=root_agent, session_service=session_service)

    async def one_turn(label: str, text: str, seconds: float = 22.0, attempts: int = 2):
        for attempt in range(1, attempts + 1):
            session = await session_service.create_session(app_name="smoke-csm", user_id="tester")
            queue = LiveRequestQueue()
            calls, responses, transcript, errors = [], [], [], []

            async def consume():
                try:
                    async for event in runner.run_live(
                        user_id=session.user_id,
                        session_id=session.id,
                        live_request_queue=queue,
                        run_config=run_config,
                    ):
                        ot = getattr(event, "output_transcription", None)
                        if ot and getattr(ot, "text", None):
                            transcript.append(ot.text)
                        content = getattr(event, "content", None)
                        for part in getattr(content, "parts", None) or []:
                            fc = getattr(part, "function_call", None)
                            if fc:
                                calls.append((fc.name, dict(getattr(fc, "args", None) or {})))
                            fr = getattr(part, "function_response", None)
                            if fr:
                                responses.append((fr.name, dict(getattr(fr, "response", None) or {})))
                except Exception as e:
                    errors.append(f"{type(e).__name__}: {e}")

            task = asyncio.create_task(consume())
            queue.send_content(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
            waited = 0.0
            while waited < seconds and not task.done():
                await asyncio.sleep(0.5)
                waited += 0.5
            queue.close()
            try:
                await asyncio.wait_for(task, timeout=10)
            except asyncio.TimeoutError:
                task.cancel()

            verdicts = []
            while not action_events.empty():
                verdicts.append(action_events.get_nowait())

            if errors and not (calls or verdicts) and attempt < attempts:
                print(f"\n=== {label} === attempt {attempt} hit a live-service error, retrying: {errors[0]}")
                await asyncio.sleep(3)
                continue

            print(f"\n=== {label} ===")
            print("  customer said:", text)
            print("  tool calls:   ", calls or "(none)")
            print("  tool results: ", responses or "(none)")
            print("  policy log:   ", verdicts or "(none)")
            print("  aria said:    ", ("".join(transcript)).strip() or "(no transcript)")
            if errors:
                print("  errors:       ", errors)
            return calls, responses, verdicts

    reset_store()
    os.environ["MAX_AUTO_REFUND"] = "100.0"
    os.environ["STRICT_REFUND_WINDOW"] = "1"
    os.environ["REQUIRE_PIN"] = "0"

    def bridged(verdicts):
        return [
            to_ui_command(v["tool"], v.get("args") or {})
            for v in verdicts
            if v.get("status") == "ok"
        ]

    _, _, verdicts1 = await one_turn(
        "1 · Customer & Order Lookup",
        "Hi Aria, I am Alex Rivera. Can you look up my order ORD-1001?",
    )
    cmds1 = bridged(verdicts1)
    ok1 = any(
        v["tool"] in ("lookup_customer", "lookup_order") and v["status"] == "ok"
        for v in verdicts1
    ) and bool(cmds1)

    _, _, verdicts2 = await one_turn(
        "2 · Allowed Refund (<= $100)",
        "Can you issue a $48 refund for order ORD-1001? The ceramic coffee carafe arrived cracked.",
    )
    ok2 = any(v["tool"] == "issue_refund" and v["status"] == "ok" for v in verdicts2)

    _, _, verdicts3 = await one_turn(
        "3 · Blocked High-Value Refund (> $100 policy gate)",
        "Please issue a $249 refund for order ORD-1002 right now.",
    )
    ok3 = any(v["tool"] == "issue_refund" and v.get("status") == "blocked" for v in verdicts3)

    print("\n--- verdict ---")
    print("  1 lookup customer/order:     ", "PASS" if ok1 else "FAIL")
    print("  2 allowed refund ($48):      ", "PASS" if ok2 else "FAIL")
    print("  3 policy-blocked refund:     ", "PASS" if ok3 else "FAIL")
    return 0 if (ok1 and ok2 and ok3) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
