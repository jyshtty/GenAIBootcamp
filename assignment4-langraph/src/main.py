"""Top-level orchestration for the multi-agent hotel management system.

Wires the booking, housekeeping, and customer-service agents into a LangGraph
workflow with conditional routing, exposes `build_graph` and the routing
helper used by the unit tests, and provides a CLI entry point for ad-hoc demo
runs.
"""

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from src.agents.booking import booking_agent
from src.agents.customer_service import customer_service_agent
from src.agents.housekeeping import housekeeping_agent
from src.models.state import HotelState, create_initial_state, state_to_dict

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def should_continue_to_housekeeping(state: Dict[str, Any]) -> str:
    """Conditional edge from booking.

    - "housekeeping" when the booking was confirmed
    - "customer_service" otherwise (failed booking goes straight to support)

    The function tolerates both a missing `booking` key and non-dict values to
    keep tests with hand-rolled states forgiving.
    """
    if not isinstance(state, dict):
        return "customer_service"
    booking = state.get("booking") or {}
    if isinstance(booking, dict) and booking.get("status") == "Confirmed":
        return "housekeeping"
    return "customer_service"


def build_graph():
    """Compile the booking → housekeeping/customer_service → END workflow."""
    workflow = StateGraph(HotelState)

    workflow.add_node("booking", booking_agent)
    workflow.add_node("housekeeping", housekeeping_agent)
    workflow.add_node("customer_service", customer_service_agent)

    workflow.add_edge(START, "booking")
    workflow.add_conditional_edges(
        "booking",
        should_continue_to_housekeeping,
        {
            "housekeeping": "housekeeping",
            "customer_service": "customer_service",
        },
    )
    workflow.add_edge("housekeeping", "customer_service")
    workflow.add_edge("customer_service", END)

    logger.info("Hotel management workflow compiled.")
    return workflow.compile()


def _print_section(title: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n{title}\n{bar}")


def main() -> None:
    """CLI entry point that runs a single workflow invocation."""
    parser = argparse.ArgumentParser(description="Hotel Management System Demo")
    parser.add_argument("--debug", action="store_true", help="Print full final state")
    parser.add_argument("--customer", default="Alice Johnson", help="Customer name")
    parser.add_argument(
        "--room-type",
        choices=["Standard", "Deluxe", "Suite"],
        default="Deluxe",
        help="Room type",
    )
    parser.add_argument("--nights", type=int, default=2, help="Number of nights")
    parser.add_argument(
        "--check-in",
        default=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        help="Check-in date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--special-request",
        action="append",
        default=None,
        help="Special request, may be passed multiple times (e.g. --special-request late_checkout)",
    )
    args = parser.parse_args()

    request = {
        "customer": args.customer,
        "room_type": args.room_type,
        "nights": args.nights,
        "check_in": args.check_in,
        "special_requests": args.special_request or ["late_checkout", "extra_towels"],
    }

    _print_section("🏨 Hotel Management System - Multi-Agent Demo")
    if args.debug:
        print(f"Input request: {request}")

    initial = create_initial_state(request)
    graph = build_graph()
    final = graph.invoke(initial)

    _print_section("📊 WORKFLOW RESULTS")
    print(f"Booking          : {final.get('booking')}")
    print(f"Housekeeping     : {final.get('housekeeping')}")
    print(f"Customer Service : {final.get('customer_service')}")
    if final.get("errors"):
        print(f"⚠️  Errors        : {final['errors']}")

    if args.debug:
        _print_section("🔍 FULL STATE")
        print(state_to_dict(final))


if __name__ == "__main__":
    main()
