"""Customer Service Management (CSM) function tools for Aria (Google ADK).

Mirrors `live-dj/adk_tools/tools.py`:
- Plain `async def` functions whose signatures and docstrings become ADK tool schemas.
- Every tool executes in-memory and returns INSTANTLY so synchronous live function calls
  never stall the voice stream.
- A tool returns its dict to the MODEL, while `to_ui_command(name, args)` bridges allowed
  tool calls to the browser's live CSM dashboard via `policy_feed()` in `server.py`.
"""
import copy
import json
import re
from pathlib import Path
from typing import Any, Optional

_DATA_PATH = Path(__file__).resolve().parents[1] / "assets" / "store_data.json"
_INITIAL_STORE: dict[str, Any] = json.loads(_DATA_PATH.read_text())

# Live in-memory store for the active process
STORE: dict[str, Any] = copy.deepcopy(_INITIAL_STORE)
ACTIVE_CONTEXT: dict[str, Any] = {
    "customer_id": None,
    "order_id": None,
    "last_ticket": None,
    "escalation": None,
}

_WORD_DIGITS = {
    "zero": "0", "oh": "0", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}


def reset_store() -> dict[str, Any]:
    """Reset the in-memory store to its initial state from assets/store_data.json."""
    global STORE
    STORE = copy.deepcopy(_INITIAL_STORE)
    ACTIVE_CONTEXT.update({"customer_id": None, "order_id": None, "last_ticket": None, "escalation": None})
    return STORE


def get_store_snapshot() -> dict[str, Any]:
    """Return a snapshot of the store and currently active customer/order context."""
    cust = find_customer(ACTIVE_CONTEXT["customer_id"]) if ACTIVE_CONTEXT.get("customer_id") else None
    order = find_order(ACTIVE_CONTEXT["order_id"]) if ACTIVE_CONTEXT.get("order_id") else None
    cust_orders = []
    if cust:
        cust_orders = [o for o in STORE["orders"] if o["customer_id"] == cust["customer_id"]]
    return {
        "active_customer": cust,
        "active_order": order,
        "customer_orders": cust_orders,
        "tickets": STORE["tickets"],
        "last_ticket": ACTIVE_CONTEXT.get("last_ticket"),
        "escalation": ACTIVE_CONTEXT.get("escalation"),
        "all_customers": STORE["customers"],
        "all_orders": STORE["orders"],
    }


def _normalize_digits(text: str) -> str:
    tokens = re.split(r"[\s\-]+", (text or "").lower().strip())
    converted = [_WORD_DIGITS.get(t, t) for t in tokens]
    joined = "".join(converted)
    return "".join(re.findall(r"\d+", joined))


def find_customer(query: Optional[str]) -> Optional[dict[str, Any]]:
    """Fuzzy-match a customer by customer_id, name, email, or phone."""
    if not query:
        return None
    q = str(query).strip().lower()
    digits = _normalize_digits(q)
    for c in STORE["customers"]:
        if c["customer_id"].lower() == q:
            return c
        if digits and digits in c["customer_id"].lower():
            return c
        if q in c["name"].lower() or c["name"].lower() in q:
            return c
        if q in c["email"].lower():
            return c
        if digits and len(digits) >= 3 and digits in re.sub(r"\D", "", c["phone"]):
            return c
    return None


def find_order(order_id: Optional[str]) -> Optional[dict[str, Any]]:
    """Fuzzy-match an order by order_id or numeric digits (e.g. 'ORD-1001' or '1001')."""
    if not order_id:
        return None
    q = str(order_id).strip().lower()
    digits = _normalize_digits(q)
    for o in STORE["orders"]:
        if o["order_id"].lower() == q:
            return o
        if digits and o["order_id"].lower().endswith(digits):
            return o
    return None


# ---------- ADK Function Tools ----------

async def lookup_customer(query: str) -> dict:
    """Look up a customer profile and their recent orders by name, email, phone, or customer ID.

    Args:
        query: Customer name (e.g. 'Alex Rivera', 'Maya Lin'), email, phone, or ID (e.g. 'CUST-101').
    """
    cust = find_customer(query)
    if not cust:
        return {
            "result": "not_found",
            "message": f"No customer found matching '{query}'. Available sample customers: Alex Rivera (CUST-101), Maya Lin (CUST-102), Sam Patel (CUST-103).",
        }
    ACTIVE_CONTEXT["customer_id"] = cust["customer_id"]
    orders = [
        {
            "order_id": o["order_id"],
            "status": o["status"],
            "total": o["total"],
            "eta": o["eta"],
            "items": [i["name"] for i in o["items"]],
        }
        for o in STORE["orders"]
        if o["customer_id"] == cust["customer_id"]
    ]
    if orders and not ACTIVE_CONTEXT.get("order_id"):
        ACTIVE_CONTEXT["order_id"] = orders[0]["order_id"]
    tickets = [t for t in STORE["tickets"] if t["customer_id"] == cust["customer_id"]]
    return {
        "result": "ok",
        "customer": {
            "customer_id": cust["customer_id"],
            "name": cust["name"],
            "email": cust["email"],
            "phone": cust["phone"],
            "tier": cust["tier"],
            "account_status": cust["account_status"],
            "verified": cust["verified"],
        },
        "orders": orders,
        "open_tickets": tickets,
    }


async def lookup_order(order_id: str) -> dict:
    """Look up an order's status, items, tracking number, delivery ETA, and shipping address.

    Args:
        order_id: The order identifier (e.g. 'ORD-1001', 'ORD-1002', 'ORD-1003', 'ORD-1004', or '1001').
    """
    order = find_order(order_id)
    if not order:
        return {
            "result": "not_found",
            "message": f"Order '{order_id}' was not found. Valid sample order IDs are ORD-1001, ORD-1002, ORD-1003, and ORD-1004.",
        }
    ACTIVE_CONTEXT["order_id"] = order["order_id"]
    ACTIVE_CONTEXT["customer_id"] = order["customer_id"]
    return {
        "result": "ok",
        "order": order,
    }


async def verify_customer_pin(customer_id: str, pin: str) -> dict:
    """Verify the customer's 4-digit security PIN to authorize sensitive account/order changes.

    Args:
        customer_id: The customer ID or name (e.g. 'CUST-101' or 'Alex Rivera').
        pin: The 4-digit security PIN provided by the customer (e.g. '4210').
    """
    cust = find_customer(customer_id) or (
        find_customer(ACTIVE_CONTEXT["customer_id"]) if ACTIVE_CONTEXT.get("customer_id") else None
    )
    if not cust:
        return {"result": "not_found", "message": f"Customer '{customer_id}' not found."}
    clean_pin = _normalize_digits(pin)
    if clean_pin == cust["pin"]:
        cust["verified"] = True
        ACTIVE_CONTEXT["customer_id"] = cust["customer_id"]
        return {
            "result": "ok",
            "verified": True,
            "customer_id": cust["customer_id"],
            "customer_name": cust["name"],
            "message": "Customer identity verified with security PIN.",
        }
    return {
        "result": "invalid_pin",
        "verified": False,
        "customer_id": cust["customer_id"],
        "message": "The provided PIN did not match our records.",
    }


async def issue_refund(order_id: str, amount: float, reason: str) -> dict:
    """Issue a refund for an order (subject to CSM policy gate rules).

    Args:
        order_id: The order ID to refund (e.g. 'ORD-1001').
        amount: The dollar amount to refund in USD (e.g. 48.0).
        reason: Brief explanation for the refund (e.g. 'Damaged item on arrival').
    """
    order = find_order(order_id)
    if not order:
        return {"result": "not_found", "message": f"Order '{order_id}' not found."}
    refund_amt = float(amount) if amount and float(amount) > 0 else float(order["total"])
    order["status"] = "refunded"
    order["refund_amount"] = round(refund_amt, 2)
    order["refund_reason"] = reason
    order["eta"] = f"Refunded ${refund_amt:.2f}"
    ACTIVE_CONTEXT["order_id"] = order["order_id"]
    ACTIVE_CONTEXT["customer_id"] = order["customer_id"]
    return {
        "result": "ok",
        "order_id": order["order_id"],
        "refund_amount": round(refund_amt, 2),
        "status": "refunded",
        "reason": reason,
        "message": f"Refund of ${refund_amt:.2f} processed for {order['order_id']}.",
    }


async def update_shipping_address(order_id: str, new_address: str) -> dict:
    """Update the shipping address for an order that is still processing.

    Args:
        order_id: The order ID to update (e.g. 'ORD-1003').
        new_address: The new street address, city, state, and zip code.
    """
    order = find_order(order_id)
    if not order:
        return {"result": "not_found", "message": f"Order '{order_id}' not found."}
    old_address = order["shipping_address"]
    order["shipping_address"] = new_address
    ACTIVE_CONTEXT["order_id"] = order["order_id"]
    ACTIVE_CONTEXT["customer_id"] = order["customer_id"]
    return {
        "result": "ok",
        "order_id": order["order_id"],
        "previous_address": old_address,
        "new_address": new_address,
        "status": order["status"],
    }


async def create_support_ticket(
    customer_id: str, order_id: str, subject: str, priority: str, summary: str
) -> dict:
    """Create a support or exception ticket for follow-up or supervisor review.

    Args:
        customer_id: Customer ID or name (e.g. 'CUST-101' or 'Alex Rivera').
        order_id: Associated order ID (e.g. 'ORD-1002').
        subject: Short ticket title.
        priority: Priority level ('low', 'medium', 'high', or 'urgent').
        summary: Detailed summary of the customer's issue or exception request.
    """
    cust = find_customer(customer_id)
    order = find_order(order_id)
    cid = cust["customer_id"] if cust else (order["customer_id"] if order else customer_id)
    oid = order["order_id"] if order else order_id
    ticket_num = 501 + len(STORE["tickets"])
    ticket = {
        "ticket_id": f"TKT-{ticket_num}",
        "customer_id": cid,
        "order_id": oid,
        "subject": subject,
        "priority": (priority or "medium").lower(),
        "status": "open",
        "summary": summary,
    }
    STORE["tickets"].append(ticket)
    ACTIVE_CONTEXT["last_ticket"] = ticket
    if cid:
        ACTIVE_CONTEXT["customer_id"] = cid
    if oid:
        ACTIVE_CONTEXT["order_id"] = oid
    return {
        "result": "ok",
        "ticket": ticket,
    }


async def escalate_to_human(order_id: str, department: str, summary: str) -> dict:
    """Escalate the conversation to a human specialist or supervisor with full context.

    Args:
        order_id: Relevant order ID (e.g. 'ORD-1002').
        department: Target team (e.g. 'billing_supervisor', 'shipping_specialist', 'trust_and_safety').
        summary: Brief handoff summary for the human specialist.
    """
    order = find_order(order_id)
    oid = order["order_id"] if order else order_id
    if order:
        ACTIVE_CONTEXT["order_id"] = order["order_id"]
        ACTIVE_CONTEXT["customer_id"] = order["customer_id"]
    escalation = {
        "escalation_id": f"ESC-{200 + len(STORE['tickets'])}",
        "order_id": oid,
        "department": department or "supervisor",
        "summary": summary,
        "status": "queued_for_specialist",
    }
    ACTIVE_CONTEXT["escalation"] = escalation
    return {
        "result": "ok",
        "escalation": escalation,
    }


def to_ui_command(name: str, args: dict) -> Optional[dict[str, Any]]:
    """Map an allowed tool call (name + args) to a browser UI update command.

    Called by `server.py`'s `policy_feed()` loop (and `smoke_live.py`), mirroring
    `to_play_command` in `live-dj/adk_tools/tools.py`.
    """
    # Ensure context is updated even if called before/after the tool body
    if name == "lookup_customer":
        cust = find_customer(args.get("query"))
        if cust:
            ACTIVE_CONTEXT["customer_id"] = cust["customer_id"]
            cust_orders = [o for o in STORE["orders"] if o["customer_id"] == cust["customer_id"]]
            if cust_orders and not ACTIVE_CONTEXT.get("order_id"):
                ACTIVE_CONTEXT["order_id"] = cust_orders[0]["order_id"]
        return {"action": "lookup_customer", "query": args.get("query", ""), "snapshot": get_store_snapshot()}

    if name == "lookup_order":
        order = find_order(args.get("order_id"))
        if order:
            ACTIVE_CONTEXT["order_id"] = order["order_id"]
            ACTIVE_CONTEXT["customer_id"] = order["customer_id"]
        return {"action": "lookup_order", "order_id": args.get("order_id", ""), "snapshot": get_store_snapshot()}

    if name == "verify_customer_pin":
        return {"action": "verify_customer_pin", "customer_id": args.get("customer_id", ""), "snapshot": get_store_snapshot()}

    if name == "issue_refund":
        return {
            "action": "issue_refund",
            "order_id": args.get("order_id", ""),
            "amount": args.get("amount", 0),
            "snapshot": get_store_snapshot(),
        }

    if name == "update_shipping_address":
        return {
            "action": "update_shipping_address",
            "order_id": args.get("order_id", ""),
            "new_address": args.get("new_address", ""),
            "snapshot": get_store_snapshot(),
        }

    if name == "create_support_ticket":
        return {
            "action": "create_support_ticket",
            "subject": args.get("subject", ""),
            "priority": args.get("priority", "medium"),
            "snapshot": get_store_snapshot(),
        }

    if name == "escalate_to_human":
        return {
            "action": "escalate_to_human",
            "department": args.get("department", "supervisor"),
            "snapshot": get_store_snapshot(),
        }

    return None

