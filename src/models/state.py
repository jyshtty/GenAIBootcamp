"""Shared state definitions for the hotel-management LangGraph workflow."""

from typing import Any, Dict, List, TypedDict


class HotelState(TypedDict, total=False):
    """Typed shape for state shuttled between agents."""

    request: Dict[str, Any]
    booking: Dict[str, Any]
    housekeeping: Dict[str, Any]
    customer_service: Dict[str, Any]
    errors: List[str]
    workflow_step: int


def create_initial_state(request: Dict[str, Any]) -> Dict[str, Any]:
    """Build the starting state for a workflow invocation."""
    return {
        "request": dict(request) if request else {},
        "booking": {},
        "housekeeping": {},
        "customer_service": {},
        "errors": [],
        "workflow_step": 0,
    }


def state_to_dict(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a plain-dict copy of state (for logging/debugging)."""
    return dict(state)
