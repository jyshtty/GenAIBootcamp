# state that gets passed between agents (dict)

from typing import Any, Dict, List, TypedDict


class HotelState(TypedDict, total=False):
    # all optional so we can do partial updates
    request: Dict[str, Any]
    booking: Dict[str, Any]
    housekeeping: Dict[str, Any]
    customer_service: Dict[str, Any]
    errors: List[str]
    workflow_step: int


def create_initial_state(request: Dict[str, Any]) -> HotelState:
    # just build the starting state dict
    return {
        "request": request,
        "booking": {},
        "housekeeping": {},
        "customer_service": {},
        "errors": [],
        "workflow_step": 0,
    }


def state_to_dict(state: HotelState) -> Dict[str, Any]:
    # for debug, turn state into plain dict
    return dict(state)
