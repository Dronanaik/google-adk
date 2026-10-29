"""Customer Service Management (CSM) policy gate — `before_tool_callback`.

Directly inspired by `live-dj/adk_tools/policy.py`:
ONE function (`csm_policy_gate`) stands at the door of EVERY tool call:

  - OBSERVE — log the call (`status: "ok"`) to `action_events` and return `None` (the tool runs).
  - BLOCK   — log the call (`status: "blocked"`) to `action_events` and return a `dict`.
              ADK skips the tool and hands that dict to Gemini as the tool result, so Aria
              explains the refusal warmly in character and offers an escalation or ticket.

Environment controls (configurable at runtime or in `.env`):
  - `MAX_AUTO_REFUND`      (default `100.0`): auto-refund ceiling in USD. Refunds above this
                           (e.g. ORD-1002 at $249.00) are blocked by policy.
  - `STRICT_REFUND_WINDOW` (default `1`): blocks refunds on orders delivered > 30 days ago
                           (e.g. ORD-1004 at 45 days).
  - `REQUIRE_PIN`          (default `0`): when `1`, blocks `issue_refund` and
                           `update_shipping_address` until `verify_customer_pin` succeeds.
"""
from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from google.adk.tools.base_tool import BaseTool
    from google.adk.tools.tool_context import ToolContext

from csm_agent.tools import ACTIVE_CONTEXT, find_customer, find_order

# Policy verdicts -> browser action log & UI state bridge (drained by server.py's policy_feed)
action_events: asyncio.Queue = asyncio.Queue()

_MUTATION_TOOLS = {"issue_refund", "update_shipping_address"}


def _max_auto_refund() -> float:
    try:
        return float(os.getenv("MAX_AUTO_REFUND", "100.0"))
    except ValueError:
        return 100.0


def _strict_refund_window() -> bool:
    mode = os.getenv("STRICT_REFUND_WINDOW", "1").strip().lower()
    return mode in {"1", "true", "on", "yes"}


def _require_pin_active() -> bool:
    mode = os.getenv("REQUIRE_PIN", "0").strip().lower()
    return mode in {"1", "true", "on", "yes"}


def _block(tool_name: str, args: dict[str, Any], short_reason: str, model_reason: str) -> dict:
    action_events.put_nowait(
        {
            "tool": tool_name,
            "args": dict(args),
            "status": "blocked",
            "reason": short_reason,
        }
    )
    return {
        "result": "blocked",
        "reason": model_reason,
    }


async def csm_policy_gate(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    name = tool.name
    order = find_order(args.get("order_id")) if "order_id" in args else None
    cust = (
        find_customer(order["customer_id"])
        if order
        else find_customer(args.get("customer_id") or ACTIVE_CONTEXT.get("customer_id"))
    )

    # Keep active context synced even if a mutation is blocked so the UI displays the relevant card
    if order:
        ACTIVE_CONTEXT["order_id"] = order["order_id"]
        ACTIVE_CONTEXT["customer_id"] = order["customer_id"]
    elif cust:
        ACTIVE_CONTEXT["customer_id"] = cust["customer_id"]

    # 1. PIN Verification Gate (when REQUIRE_PIN=1)
    if _require_pin_active() and name in _MUTATION_TOOLS:
        if not (cust and cust.get("verified")):
            return _block(
                name,
                args,
                "customer PIN not verified",
                (
                    "Security policy requires customer PIN verification before modifying an order "
                    "or issuing a refund. Ask the customer for their 4-digit security PIN and "
                    "call verify_customer_pin first."
                ),
            )

    # 2. Refund Policy Gate (amount ceiling + 30-day return window)
    if name == "issue_refund":
        req_amount = float(args.get("amount") or 0.0)
        if req_amount <= 0 and order:
            req_amount = float(order["total"])

        # 2a. 30-day delivery window check
        if _strict_refund_window() and order:
            days = order.get("days_since_delivery")
            if days is not None and days > 30:
                return _block(
                    name,
                    args,
                    f"past 30-day return window ({days}d)",
                    (
                        f"Order {order['order_id']} was delivered {days} days ago, which is outside "
                        "NovaMart's 30-day return window. Politely explain this policy to the customer "
                        "and offer to create a support ticket for an exception review."
                    ),
                )

        # 2b. High-value refund ceiling check
        limit = _max_auto_refund()
        if req_amount > limit:
            return _block(
                name,
                args,
                f"exceeds ${limit:.0f} auto-refund limit (${req_amount:.2f})",
                (
                    f"Refund of ${req_amount:.2f} exceeds the ${limit:.2f} automatic voice-agent "
                    "approval limit. Explain this gently to the customer and offer to either "
                    "create a high-priority support ticket or escalate to a human supervisor."
                ),
            )

    # 3. Shipping Address Update Gate (only allowed while order is 'processing')
    if name == "update_shipping_address" and order:
        if order["status"] != "processing":
            return _block(
                name,
                args,
                f"order already {order['status']}",
                (
                    f"Cannot update the shipping address for {order['order_id']} because its status "
                    f"is '{order['status']}'. Address changes are only permitted while an order is "
                    "'processing'. Explain this clearly and offer to create a carrier intercept ticket."
                ),
            )

    # Allowed: observe & let ADK execute the tool
    action_events.put_nowait({"tool": name, "args": dict(args), "status": "ok"})
    return None
