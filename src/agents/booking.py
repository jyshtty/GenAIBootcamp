"""Booking agent: validates the request and reserves a room."""

import uuid
from datetime import datetime
from typing import Any, Dict

from src.utils.mocks import ROOM_RATES, reserve_room


def booking_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Process a reservation request and return the booking update."""
    print("🏨 Booking Agent: Processing reservation request...")

    request = state.get("request", {}) or {}
    customer = request.get("customer", "")
    room_type = request.get("room_type", "Standard")
    nights = request.get("nights", 1)
    check_in = request.get("check_in", datetime.now().strftime("%Y-%m-%d"))

    errors = list(state.get("errors", []) or [])

    def fail(reason: str) -> Dict[str, Any]:
        errors.append(reason)
        print(f"❌ Booking failed: {reason}")
        return {
            "booking": {"status": "Failed", "reason": reason},
            "errors": errors,
            "workflow_step": 1,
        }

    if not customer:
        return fail("Customer name is required")

    if room_type not in ROOM_RATES:
        return fail(f"Invalid room type: {room_type}")

    if not isinstance(nights, int) or nights < 1:
        return fail(f"Invalid number of nights: {nights}")

    room_number = reserve_room(room_type)
    if not room_number:
        return fail(f"No {room_type} rooms available")

    booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
    rate = ROOM_RATES[room_type]
    total_cost = rate * nights

    booking = {
        "booking_id": booking_id,
        "customer": customer,
        "room_type": room_type,
        "room_number": room_number,
        "check_in": check_in,
        "nights": nights,
        "rate_per_night": rate,
        "total_cost": total_cost,
        "status": "Confirmed",
        "created_at": datetime.now().isoformat(),
    }

    print(f"✅ Booking confirmed {booking_id} | {customer} | {room_type} #{room_number} | {nights} night(s) | ${total_cost}")

    return {"booking": booking, "workflow_step": 1}
