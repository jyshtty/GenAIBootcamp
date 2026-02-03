# does the room reservation stuff

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from src.models.state import HotelState
from src.utils.mocks import (
    ROOM_RATES,
    get_available_rooms,
    mock_payment_confirm,
    reserve_room,
)

logger = logging.getLogger(__name__)


def booking_agent(state: HotelState) -> Dict[str, Any]:
    # check room free, fake pay, then confirm. return just what we changed
    logger.info("Booking Agent: Processing reservation request")
    print("Booking Agent: Processing reservation request...")

    request = state.get("request") or {}
    errors = list(state.get("errors") or [])

    try:
        customer = request.get("customer")
        room_type = request.get("room_type", "Standard")
        check_in = request.get("check_in", datetime.now().strftime("%Y-%m-%d"))
        nights = request.get("nights", 1)

        # need customer name
        if not customer:
            return {
                "booking": {"status": "Failed", "reason": "Customer name is required"},
                "errors": errors + ["Validation: customer name required"],
                "workflow_step": 1,
            }

        if not room_type or room_type not in ROOM_RATES:
            return {
                "booking": {"status": "Failed", "reason": f"Invalid room type: {room_type}"},
                "errors": errors + [f"Validation: invalid room type {room_type}"],
                "workflow_step": 1,
            }

        if not isinstance(nights, int) or nights < 1:
            return {
                "booking": {"status": "Failed", "reason": "Nights must be a positive integer"},
                "errors": errors + ["Validation: nights must be >= 1"],
                "workflow_step": 1,
            }

        # get room from mocks
        room_number = reserve_room(room_type)
        available = get_available_rooms(room_type)

        if not available or not room_number:
            return {
                "booking": {"status": "Failed", "reason": f"No {room_type} rooms available"},
                "errors": errors + [f"Room unavailable: {room_type}"],
                "workflow_step": 1,
            }

        # make the booking
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
        rate = ROOM_RATES.get(room_type, 150)
        total_cost = rate * nights

        # fake payment - if it fail we dont confirm
        payment_ok = mock_payment_confirm(booking_id, total_cost)
        if not payment_ok:
            return {
                "booking": {"status": "Failed", "reason": "Payment declined"},
                "errors": errors + ["Payment processing failed"],
                "workflow_step": 1,
            }

        booking = {
            "booking_id": booking_id,
            "customer": customer,
            "room_type": room_type,
            "room_number": room_number,
            "check_in": check_in,
            "nights": nights,
            "status": "Confirmed",
            "total_cost": total_cost,
            "created_at": datetime.now().isoformat(),
        }

        print(f"Booking confirmed: {booking_id} for {customer}")
        print(f"   Room: {room_type} #{room_number}, {nights} night(s)")
        logger.info("Booking confirmed: %s for %s", booking_id, customer)

        return {"booking": booking, "workflow_step": 1}

    except Exception as e:
        logger.exception("Booking Agent error")
        print(f"Booking Agent error: {e}")
        return {
            "booking": {"status": "Failed", "reason": str(e)},
            "errors": errors + [f"Booking error: {str(e)}"],
            "workflow_step": 1,
        }
