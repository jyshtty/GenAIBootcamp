"""Housekeeping agent.

Generates a per-room preparation plan once a booking is confirmed: a tailored
checklist, an assigned cleaning team, and an estimated completion window. Skips
work cleanly when the upstream booking did not succeed.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


BASE_CHECKLIST: List[str] = [
    "Change bed linens",
    "Clean and sanitize bathroom",
    "Vacuum and mop floors",
    "Dust all surfaces",
    "Restock toiletries",
    "Replace towels",
    "Empty trash bins",
]

ROOM_TYPE_EXTRAS: Dict[str, List[str]] = {
    "Standard": ["Wipe down windows"],
    "Deluxe": [
        "Restock minibar",
        "Polish wooden furniture",
        "Arrange in-room coffee station",
    ],
    "Suite": [
        "Restock minibar",
        "Polish marble surfaces",
        "Stock premium toiletries",
        "Arrange welcome amenities",
        "Schedule turn-down service",
    ],
}

# Maps a room category to the team most experienced with it.
TEAM_ASSIGNMENTS: Dict[str, str] = {
    "Standard": "Housekeeping Team A",
    "Deluxe": "Housekeeping Team B",
    "Suite": "VIP Housekeeping Team",
}

PREP_DURATION_HOURS: Dict[str, int] = {
    "Standard": 1,
    "Deluxe": 1,
    "Suite": 2,
}


def _build_checklist(room_type: str, special_requests: List[str]) -> List[str]:
    """Combine the base checklist with room-tier extras and special requests."""
    checklist = list(BASE_CHECKLIST)
    checklist.extend(ROOM_TYPE_EXTRAS.get(room_type, []))

    request_to_task = {
        "extra_towels": "Place 4 extra towel sets in the bathroom",
        "late_checkout": "Notify front desk about late checkout",
        "early_checkin": "Prepare room for early arrival",
        "hypoallergenic": "Use hypoallergenic linens and toiletries",
        "high_floor": "Confirm room assignment is on a high floor",
    }
    for req in special_requests:
        task = request_to_task.get(req)
        if task:
            checklist.append(task)
    return checklist


def housekeeping_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare the assigned room or skip cleanly if booking did not confirm."""
    print("🧹 Housekeeping Agent: Preparing room...")
    logger.info("Housekeeping agent invoked.")

    booking = state.get("booking", {}) or {}
    request = state.get("request", {}) or {}

    if booking.get("status") != "Confirmed":
        logger.info("Skipping housekeeping: booking is not confirmed.")
        print("⏭️  Housekeeping skipped: no confirmed booking")
        return {
            "housekeeping": {
                "status": "Skipped",
                "reason": "No confirmed booking; housekeeping is not required.",
            },
            "workflow_step": 2,
        }

    room_id = booking.get("room_number")
    room_type = booking.get("room_type", "Standard")
    special_requests = request.get("special_requests") or []

    checklist = _build_checklist(room_type, special_requests)
    assigned_team = TEAM_ASSIGNMENTS.get(room_type, "Housekeeping Team A")
    duration_hours = PREP_DURATION_HOURS.get(room_type, 1)

    now = datetime.now()
    schedule = {
        "preparation_start": now.isoformat(),
        "estimated_completion": (now + timedelta(hours=duration_hours)).isoformat(),
        "assigned_team": assigned_team,
        "priority": "High" if room_type == "Suite" else "Normal",
        "duration_hours": duration_hours,
    }

    maintenance = {
        "needs_followup": False,
        "notes": "All systems verified during inspection.",
    }

    logger.info(
        "Room %s (%s) prepared: %d checklist items, team=%s, eta=%dh.",
        room_id, room_type, len(checklist), assigned_team, duration_hours,
    )
    print(
        f"✅ Room {room_id} ({room_type}) ready in ~{duration_hours}h "
        f"with {len(checklist)} checklist items by {assigned_team}"
    )

    return {
        "housekeeping": {
            "status": "Ready",
            "room_id": room_id,
            "room_type": room_type,
            "checklist": checklist,
            "schedule": schedule,
            "maintenance": maintenance,
        },
        "workflow_step": 2,
    }
