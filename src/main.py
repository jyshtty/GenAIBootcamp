"""LangGraph workflow wiring for the multi-agent hotel management system."""

import argparse
from datetime import datetime, timedelta
from typing import Any, Dict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from src.agents.booking import booking_agent
from src.agents.customer_service import customer_service_agent
from src.agents.housekeeping import housekeeping_agent
from src.models.state import HotelState, create_initial_state, state_to_dict

load_dotenv()


def should_continue_to_housekeeping(state: Dict[str, Any]) -> str:
    """Conditional edge from booking: housekeeping on success, otherwise customer_service."""
    booking = (state or {}).get("booking", {}) if isinstance(state, dict) else {}
    if isinstance(booking, dict) and booking.get("status") == "Confirmed":
        return "housekeeping"
    return "customer_service"


def build_graph():
    """Compile the booking → housekeeping/customer_service workflow."""
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

    return workflow.compile()


def main() -> None:
    """CLI entry point that runs a single workflow invocation."""
    parser = argparse.ArgumentParser(description="Hotel Management System Demo")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--customer", default="Alice Johnson", help="Customer name")
    parser.add_argument(
        "--room-type",
        choices=["Standard", "Deluxe", "Suite"],
        default="Deluxe",
        help="Room type",
    )
    parser.add_argument("--nights", type=int, default=2, help="Number of nights")
    args = parser.parse_args()

    request = {
        "customer": args.customer,
        "room_type": args.room_type,
        "nights": args.nights,
        "check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "special_requests": ["late_checkout", "extra_towels"],
    }

    print("🏨 Hotel Management System - Multi-Agent Demo")
    print("=" * 50)
    if args.debug:
        print(f"Input request: {request}")
        print("-" * 30)

    initial = create_initial_state(request)
    graph = build_graph()
    final = graph.invoke(initial)

    print("\n" + "=" * 50)
    print("📊 WORKFLOW RESULTS")
    print("=" * 50)
    print(f"Booking          : {final.get('booking')}")
    print(f"Housekeeping     : {final.get('housekeeping')}")
    print(f"Customer Service : {final.get('customer_service')}")
    if final.get("errors"):
        print(f"⚠️  Errors        : {final['errors']}")

    if args.debug:
        print("\n🔍 Full state:")
        print(state_to_dict(final))


if __name__ == "__main__":
    main()
