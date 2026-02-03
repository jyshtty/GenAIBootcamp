# fake data and apis so we dont need real backend

from typing import Dict, List, Optional

# which rooms we got free by type
AVAILABLE_ROOMS: Dict[str, List[str]] = {
    "Standard": ["101", "102", "103"],
    "Deluxe": ["201", "202"],
    "Suite": ["301"],
}

# price per night
ROOM_RATES: Dict[str, int] = {
    "Standard": 150,
    "Deluxe": 250,
    "Suite": 350,
}

# room status for housekeeping
ROOM_STATUSES: Dict[str, str] = {
    "101": "clean",
    "102": "clean",
    "103": "dirty",
    "201": "clean",
    "202": "inspection",
    "301": "clean",
}

# when each room gets cleaned
CLEANING_SCHEDULE: Dict[str, str] = {
    "101": "09:00-09:30",
    "102": "09:30-10:00",
    "103": "10:00-10:30",
    "201": "10:30-11:00",
    "202": "11:00-11:30",
    "301": "11:30-12:00",
}

# staff and their rooms
HOUSEKEEPING_STAFF: List[Dict[str, str]] = [
    {"id": "HK001", "name": "Maria", "assigned_rooms": ["101", "102"]},
    {"id": "HK002", "name": "John", "assigned_rooms": ["201", "202"]},
    {"id": "HK003", "name": "Lisa", "assigned_rooms": ["301", "103"]},
]

# maintenance stuff (we dont actually call anyone)
MAINTENANCE_REQUESTS: List[Dict[str, str]] = [
    {"room_id": "103", "type": "AC repair", "status": "scheduled"},
]

# faq for customer service
FAQ_ENTRIES: List[Dict[str, str]] = [
    {"topic": "check-in", "answer": "Check-in time is 3:00 PM."},
    {"topic": "checkout", "answer": "Check-out time is 11:00 AM."},
    {"topic": "wi-fi", "answer": "Wi-Fi is free. Network: HotelGuest, no password."},
]

COMPLAINT_CATEGORIES: List[str] = [
    "room_quality",
    "noise",
    "service",
    "billing",
    "cleanliness",
]


def get_available_rooms(room_type: str) -> List[str]:
    # list of room numbers for that type
    return list(AVAILABLE_ROOMS.get(room_type, []))


def reserve_room(room_type: str) -> Optional[str]:
    # grab first free room of type (we dont actually remove it)
    rooms = get_available_rooms(room_type)
    return rooms[0] if rooms else None


def mock_payment_confirm(booking_id: str, amount: float) -> bool:
    # always say yes for demo
    return True


def mock_housekeeping_api(room_id: str, action: str) -> Dict[str, str]:
    # fake api - just return ready or status
    status = ROOM_STATUSES.get(room_id, "unknown")
    schedule = CLEANING_SCHEDULE.get(room_id, "TBD")
    return {
        "room_id": room_id,
        "action": action,
        "status": "Ready" if action == "prepare" else status,
        "schedule": schedule,
    }


def get_room_status(room_number: str) -> str:
    return ROOM_STATUSES.get(room_number, "unknown")


def get_staff_for_room(room_number: str) -> Optional[Dict[str, str]]:
    # who is assigned to this room
    for staff in HOUSEKEEPING_STAFF:
        if room_number in staff.get("assigned_rooms", []):
            return staff
    return None
