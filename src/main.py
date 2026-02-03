# main app - wires up the graph and run it

import argparse
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from src.agents.booking import booking_agent
from src.agents.customer_service import customer_service_agent
from src.agents.housekeeping import housekeeping_agent
from src.models.state import HotelState, create_initial_state, state_to_dict

load_dotenv()

# so we can see what happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def should_continue_to_housekeeping(state: HotelState) -> str:
    # if booking ok go to housekeeping else straight to customer service
    if (state.get("booking") or {}).get("status") == "Confirmed":
        return "housekeeping"
    return "customer_service"


def build_graph():
    # booking first, then housekeeping if confirmed or customer_service, then always customer_service
    workflow = StateGraph(HotelState)

    workflow.add_node("booking", booking_agent)
    workflow.add_node("housekeeping", housekeeping_agent)
    workflow.add_node("customer_service", customer_service_agent)

    workflow.add_edge(START, "booking")
    workflow.add_conditional_edges(
        "booking",
        should_continue_to_housekeeping,
        {"housekeeping": "housekeeping", "customer_service": "customer_service"},
    )
    workflow.add_edge("housekeeping", "customer_service")
    workflow.add_edge("customer_service", END)

    return workflow.compile()


def main():
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

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    print("Hotel Management System - Multi-Agent Demo")
    print("=" * 50)

    request_data = {
        "customer": args.customer,
        "room_type": args.room_type,
        "nights": args.nights,
        "check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "special_requests": ["late_checkout", "extra_towels"],
    }

    if args.debug:
        print(f"Input Request: {request_data}")
        print("-" * 30)

    initial_state = create_initial_state(request_data)

    try:
        hotel_graph = build_graph()
        logger.info("Workflow starting")
        final_state: HotelState = hotel_graph.invoke(initial_state)
        logger.info("Workflow completed")

        print("\n" + "=" * 50)
        print("WORKFLOW RESULTS")
        print("=" * 50)

        if final_state.get("booking"):
            print(f"Booking: {final_state['booking']}")
        if final_state.get("housekeeping"):
            print(f"Housekeeping: {final_state['housekeeping']}")
        if final_state.get("customer_service"):
            print(f"Customer Service: {final_state['customer_service']}")

        if final_state.get("errors"):
            print(f"\nErrors encountered: {final_state['errors']}")

        if args.debug:
            print(f"\nFull State Debug:")
            print(state_to_dict(final_state))

    except Exception as e:
        logger.exception("System error")
        print(f"System error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
