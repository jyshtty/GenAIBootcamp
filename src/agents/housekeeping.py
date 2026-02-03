# gets room ready for check in

import logging
from datetime import datetime
from typing import Dict, Any

from src.models.state import HotelState
from src.utils.mocks import (
    CLEANING_SCHEDULE,
    MAINTENANCE_REQUESTS,
    get_staff_for_room,
    mock_housekeeping_api,
)

logger = logging.getLogger(__name__)


def housekeeping_agent(state: HotelState) -> Dict[str, Any]:
    # only runs when booking was ok. prepare room, checklist, staff from mocks
    logger.info("Housekeeping Agent: Preparing room for check-in")
    print("Housekeeping Agent: Preparing room for check-in...")

    booking = state.get("booking") or {}
    errors = list(state.get("errors") or [])

    try:
        if booking.get("status") != "Confirmed":
            return {
                "housekeeping": {"status": "Skipped", "reason": "No confirmed booking"},
                "workflow_step": 2,
            }

        room_number = booking.get("room_number")
        if not room_number:
            return {
                "housekeeping": {"status": "Failed", "reason": "No room number"},
                "errors": errors + ["Housekeeping: no room number in booking"],
                "workflow_step": 2,
            }

        check_in = booking.get("check_in", "")
        room_type = booking.get("room_type", "")

        api_result = mock_housekeeping_api(room_number, "prepare")
        schedule_slot = CLEANING_SCHEDULE.get(room_number, "Ready by check-in")
        staff = get_staff_for_room(room_number)

        # we mark everything done in mock
        checklist = [
            {"item": "cleaned", "done": True},
            {"item": "stocked", "done": True},
            {"item": "inspected", "done": True},
        ]

        maintenance_for_room = [
            m for m in MAINTENANCE_REQUESTS if m.get("room_id") == room_number
        ]

        housekeeping = {
            "room_id": room_number,
            "room_type": room_type,
            "status": "Ready",
            "task": "prepare for check-in",
            "schedule": schedule_slot,
            "checklist": checklist,
            "staff": staff,
            "maintenance_scheduled": maintenance_for_room,
            "updated_at": datetime.now().isoformat(),
        }

        print(f"   Room #{room_number} ready. Schedule: {schedule_slot}")
        logger.info("Housekeeping: room %s ready", room_number)

        return {"housekeeping": housekeeping, "workflow_step": 2}

    except Exception as e:
        logger.exception("Housekeeping Agent error")
        print(f"Housekeeping Agent error: {e}")
        room_number = (state.get("booking") or {}).get("room_number")
        housekeeping = (
            {"room_id": room_number, "status": "Partial", "error": str(e)}
            if room_number
            else {"status": "Failed", "reason": str(e)}
        )
        return {
            "housekeeping": housekeeping,
            "errors": errors + [f"Housekeeping error: {str(e)}"],
            "workflow_step": 2,
        }
