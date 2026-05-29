"""Mock hotel inventory and helper functions used by the agents."""

from typing import Dict, List

ROOM_RATES: Dict[str, int] = {
    "Standard": 150,
    "Deluxe": 250,
    "Suite": 350,
}

ROOM_INVENTORY: Dict[str, List[str]] = {
    "Standard": ["101", "102", "103"],
    "Deluxe": ["201", "202"],
    "Suite": ["301"],
}


def get_available_rooms(room_type: str) -> List[str]:
    """Return the list of room numbers for a given room type."""
    return list(ROOM_INVENTORY.get(room_type, []))


def reserve_room(room_type: str):
    """Pick the first available room of the requested type, or None."""
    rooms = get_available_rooms(room_type)
    if not rooms:
        return None
    return rooms[0]
