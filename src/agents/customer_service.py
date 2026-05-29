"""Customer service agent: composes the guest-facing response and logs the interaction."""

from datetime import datetime
from typing import Any, Dict


def customer_service_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Build the customer response and an interaction log entry."""
    print("🎧 Customer Service Agent: Handling customer interaction...")

    request = state.get("request", {}) or {}
    booking = state.get("booking", {}) or {}
    housekeeping = state.get("housekeeping", {}) or {}
    errors = state.get("errors", []) or []

    customer = request.get("customer") or "Guest"
    booking_status = booking.get("status", "Unknown")

    if booking_status == "Confirmed":
        room_type = booking.get("room_type", "room")
        room_number = booking.get("room_number", "TBD")
        nights = booking.get("nights", 1)
        total_cost = booking.get("total_cost", 0)
        hk_status = housekeeping.get("status", "in progress")
        response = (
            f"Welcome, {customer}! Your {room_type} reservation is confirmed. "
            f"Room {room_number} for {nights} night(s), total ${total_cost}. "
            f"Housekeeping status: {hk_status}. We look forward to your stay!"
        )
    elif booking_status == "Failed":
        reason = booking.get("reason", "an unexpected issue")
        response = (
            f"We're sorry, {customer}. We could not complete your booking ({reason}). "
            f"Please review your request or contact our support team for assistance."
        )
    else:
        response = (
            f"Hello {customer}, thank you for reaching out. "
            f"How may we help you today?"
        )

    interaction_log = {
        "timestamp": datetime.now().isoformat(),
        "customer": customer,
        "booking_status": booking_status,
        "housekeeping_status": housekeeping.get("status", "Unknown"),
        "errors": list(errors),
        "channel": "automated_agent",
    }

    print(f"💬 Response prepared for {customer}")

    return {
        "customer_service": {
            "response": response,
            "interaction_log": interaction_log,
        },
        "workflow_step": 3,
    }
