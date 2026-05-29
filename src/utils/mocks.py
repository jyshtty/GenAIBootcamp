"""Mock hotel inventory and helper functions used by the agents.

Centralising the fake data here keeps the agents focused on workflow logic
and makes it easy to swap in a real reservation system later — the agents
only depend on the public helpers (`get_available_rooms`, `reserve_room`).
"""

from typing import Dict, List, Optional

# Per-night USD rates used by the booking agent for cost calculations.
ROOM_RATES: Dict[str, int] = {
    "Standard": 150,
    "Deluxe": 250,
    "Suite": 350,
}

# Room inventory grouped by room category.
ROOM_INVENTORY: Dict[str, List[str]] = {
    "Standard": ["101", "102", "103"],
    "Deluxe": ["201", "202"],
    "Suite": ["301"],
}

# Optional descriptions surfaced by the customer-service agent / clients.
ROOM_DESCRIPTIONS: Dict[str, str] = {
    "Standard": "Comfortable queen room with city view and complimentary Wi-Fi.",
    "Deluxe": "Spacious king room with seating area, premium linens, and minibar.",
    "Suite": "Two-room suite with living area, balcony, and turn-down service.",
}

# Common amenities offered to all guests.
HOTEL_AMENITIES: List[str] = [
    "24/7 front desk",
    "Free Wi-Fi",
    "Fitness center",
    "Swimming pool",
    "Restaurant and bar",
    "Concierge service",
]


def get_available_rooms(room_type: str) -> List[str]:
    """Return the list of room numbers for a given room type."""
    return list(ROOM_INVENTORY.get(room_type, []))


def reserve_room(room_type: str) -> Optional[str]:
    """Pick the first available room of the requested type, or None."""
    rooms = get_available_rooms(room_type)
    if not rooms:
        return None
    return rooms[0]


def get_room_description(room_type: str) -> str:
    """Return a human-readable description of the room category."""
    return ROOM_DESCRIPTIONS.get(room_type, "Room details unavailable.")


def get_amenities() -> List[str]:
    """Return the list of hotel-wide amenities."""
    return list(HOTEL_AMENITIES)
