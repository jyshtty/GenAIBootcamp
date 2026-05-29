"""Booking agent.

Validates the request, reserves a room, simulates payment authorization, and
emits a structured booking record. Returns a partial-state update that
LangGraph merges back into the shared HotelState.
"""

import logging
import random
import uuid
from datetime import datetime
from typing import Any, Dict

from src.utils.mocks import ROOM_RATES, reserve_room

logger = logging.getLogger(__name__)


def _simulate_payment(amount: int, customer: str) -> Dict[str, Any]:
    """Mock a payment authorisation - always succeeds in the demo."""
    return {
        "transaction_id": f"TX{uuid.uuid4().hex[:10].upper()}",
        "amount": amount,
        "currency": "USD",
        "status": "Authorised",
        "method": "credit_card",
        "customer": customer,
        "timestamp": datetime.now().isoformat(),
    }


def booking_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Process a reservation request and return the booking update."""
    print("🏨 Booking Agent: Processing reservation request...")
    logger.info("Booking agent received request: %s", state.get("request"))

    request = state.get("request", {}) or {}
    customer = request.get("customer", "")
    room_type = request.get("room_type", "Standard")
    nights = request.get("nights", 1)
    check_in = request.get("check_in", datetime.now().strftime("%Y-%m-%d"))
    special_requests = request.get("special_requests") or []

    errors = list(state.get("errors", []) or [])

    def fail(reason: str) -> Dict[str, Any]:
        errors.append(reason)
        logger.warning("Booking failed: %s", reason)
        print(f"❌ Booking failed: {reason}")
        return {
            "booking": {"status": "Failed", "reason": reason},
            "errors": errors,
            "workflow_step": 1,
        }

    # Input validation: surface clear errors for each invalid field.
    if not customer:
        return fail("Customer name is required")

    if room_type not in ROOM_RATES:
        return fail(
            f"Invalid room type: {room_type}. "
            f"Allowed: {', '.join(ROOM_RATES.keys())}"
        )

    if not isinstance(nights, int) or nights < 1:
        return fail(f"Invalid number of nights: {nights}. Must be a positive integer.")

    room_number = reserve_room(room_type)
    if not room_number:
        return fail(f"No {room_type} rooms available")

    booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
    rate = ROOM_RATES[room_type]
    total_cost = rate * nights

    payment = _simulate_payment(total_cost, customer)
    confirmation_number = f"HC{random.randint(100000, 999999)}"

    booking = {
        "booking_id": booking_id,
        "confirmation_number": confirmation_number,
        "customer": customer,
        "room_type": room_type,
        "room_number": room_number,
        "check_in": check_in,
        "nights": nights,
        "rate_per_night": rate,
        "total_cost": total_cost,
        "currency": "USD",
        "special_requests": list(special_requests),
        "status": "Confirmed",
        "payment": payment,
        "created_at": datetime.now().isoformat(),
    }

    logger.info(
        "Booking %s confirmed for %s (%s #%s, %d night(s), $%d).",
        booking_id, customer, room_type, room_number, nights, total_cost,
    )
    print(
        f"✅ Booking confirmed {booking_id} | {customer} | "
        f"{room_type} #{room_number} | {nights} night(s) | ${total_cost}"
    )

    return {"booking": booking, "workflow_step": 1}
