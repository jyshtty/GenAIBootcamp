"""Housekeeping agent: prepares the room once a booking is confirmed."""

from datetime import datetime, timedelta
from typing import Any, Dict


BASE_CHECKLIST = [
    "Change bed linens",
    "Clean and sanitize bathroom",
    "Vacuum and mop floors",
    "Dust all surfaces",
    "Restock toiletries",
    "Replace towels",
    "Empty trash bins",
]

ROOM_TYPE_EXTRAS = {
    "Deluxe": ["Restock minibar", "Polish wooden furniture"],
    "Suite": [
        "Restock minibar",
        "Polish marble surfaces",
        "Stock premium toiletries",
        "Arrange welcome amenities",
    ],
}


def housekeeping_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare the assigned room or skip if booking did not confirm."""
    print("🧹 Housekeeping Agent: Preparing room...")

    booking = state.get("booking", {}) or {}

    if booking.get("status") != "Confirmed":
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

    checklist = list(BASE_CHECKLIST)
    checklist.extend(ROOM_TYPE_EXTRAS.get(room_type, []))

    now = datetime.now()
    schedule = {
        "preparation_start": now.isoformat(),
        "estimated_completion": (now + timedelta(hours=1)).isoformat(),
        "assigned_team": "Housekeeping Team A",
        "priority": "High" if room_type == "Suite" else "Normal",
    }

    print(f"✅ Room {room_id} ({room_type}) prepared with {len(checklist)} checklist items")

    return {
        "housekeeping": {
            "status": "Ready",
            "room_id": room_id,
            "room_type": room_type,
            "checklist": checklist,
            "schedule": schedule,
        },
        "workflow_step": 2,
    }
