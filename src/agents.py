"""
🏨 Multi-Agent Hotel Management System - Starter Implementation

This starter implementation provides a working LangGraph-based multi-agent
system for hotel management. Students should extend this foundation to
implement the full requirements.

Key Features Demonstrated:
✅ LangGraph workflow orchestration
✅ Shared state management
✅ Agent interaction patterns
✅ Mock data handling
"""

import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, START, END
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import DIAL client
from src.utils.dial_client import DIALClient


class HotelState:
    """
    Shared state object for hotel management workflow.
    
    Attributes:
        request: Initial customer request data
        booking: Booking information and status
        housekeeping: Room preparation status
        customer_service: Customer interaction logs
        errors: Any errors encountered during processing
        dial_client: DIAL API client for AI functionality
    """
    def __init__(self, request: Dict[str, Any]):
        self.request = request
        self.booking: Dict[str, Any] = {}
        self.housekeeping: Dict[str, Any] = {}
        self.customer_service: Dict[str, Any] = {}
        self.errors: list = []
        self.workflow_step = 0
        self.dial_client = DIALClient()

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for easier debugging."""
        return {
            "request": self.request,
            "booking": self.booking,
            "housekeeping": self.housekeeping,
            "customer_service": self.customer_service,
            "errors": self.errors,
            "workflow_step": self.workflow_step
        }


def booking_agent(state: HotelState) -> HotelState:
    """
    Booking Agent: Handles room reservations and availability checks.
    
    TODO for students:
    - Add room availability validation
    - Implement payment processing simulation
    - Add booking modification/cancellation logic
    - Integrate with external booking APIs (extension)
    """
    print("🏨 Booking Agent: Processing reservation request...")
    
    try:
        customer = state.request.get("customer")
        room_type = state.request.get("room_type", "Standard")
        check_in = state.request.get("check_in", datetime.now().strftime("%Y-%m-%d"))
        nights = state.request.get("nights", 1)
        
        # Mock room availability check
        available_rooms = {
            "Standard": ["101", "102", "103"],
            "Deluxe": ["201", "202"],
            "Suite": ["301"]
        }
        
        if room_type in available_rooms and available_rooms[room_type]:
            # Simulate booking creation
            booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
            room_number = available_rooms[room_type][0]  # Take first available
            
            state.booking = {
                "booking_id": booking_id,
                "customer": customer,
                "room_type": room_type,
                "room_number": room_number,
                "check_in": check_in,
                "nights": nights,
                "status": "Confirmed",
                "total_cost": 150 * nights if room_type == "Standard" else 250 * nights,
                "created_at": datetime.now().isoformat()
            }
            
            print(f"✅ Booking confirmed: {booking_id} for {customer}")
            print(f"   Room: {room_type} #{room_number}, {nights} night(s)")
            
        else:
            state.booking = {"status": "Failed", "reason": f"No {room_type} rooms available"}
            state.errors.append(f"Room unavailable: {room_type}")
            print(f"❌ Booking failed: No {room_type} rooms available")
            
    except Exception as e:
        state.errors.append(f"Booking error: {str(e)}")
        print(f"❌ Booking Agent error: {e}")
    
    state.workflow_step = 1
    return state


def housekeeping_agent(state: HotelState) -> HotelState:
    """
    Housekeeping Agent: Manages room preparation and maintenance.
    
    TODO for students: Implement this agent functionality
    - Add room inspection checklist
    - Implement cleaning schedule optimization
    - Add maintenance request handling
    - Create staff assignment logic
    """
    print("🧹 Housekeeping Agent: TODO - Implement housekeeping logic")
    
    # TODO: Students should implement this agent
    # For now, just pass through
    state.workflow_step = 2
    return state


def customer_service_agent(state: HotelState) -> HotelState:
    """
    Customer Service Agent: Handles guest communications and support.
    
    TODO for students: Implement this agent functionality
    - Add sentiment analysis for customer feedback
    - Implement complaint resolution workflow
    - Add proactive service recommendations
    - Integrate with external communication APIs
    """
    print("🎧 Customer Service Agent: TODO - Implement customer service logic")
    
    # TODO: Students should implement this agent
    # For now, just pass through
    state.workflow_step = 3
    return state


def should_continue_to_housekeeping(state: HotelState) -> str:
    """Route decision: proceed to housekeeping only if booking succeeded."""
    if state.booking.get("status") == "Confirmed":
        return "housekeeping"
    else:
        return "customer_service"


def build_graph() -> StateGraph:
    """
    Constructs the LangGraph workflow for hotel management.
    
    Basic workflow for students to extend:
    1. Booking Agent (implemented as example)
    2. TODO: Students add other agents and routing logic
    """
    # Create the graph
    workflow = StateGraph(HotelState)
    
    # Add nodes (agents) - students should add more
    workflow.add_node("booking", booking_agent)
    # TODO: Students should add housekeeping and customer_service nodes

    
    # Add edges (workflow routing) - students should implement routing logic
    workflow.add_edge(START, "booking")
    workflow.add_edge("booking", END)  # Simplified for now
    
    # TODO: Students should implement conditional routing:

    return workflow.compile()


def main():
    """Main execution function with argument parsing."""
    parser = argparse.ArgumentParser(description="Hotel Management System Demo")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--customer", default="Alice Johnson", help="Customer name")
    parser.add_argument("--room-type", choices=["Standard", "Deluxe", "Suite"], 
                       default="Deluxe", help="Room type")
    parser.add_argument("--nights", type=int, default=2, help="Number of nights")
    
    args = parser.parse_args()
    
    print("🏨 Hotel Management System - Multi-Agent Demo")
    print("=" * 50)
    
    # Example input data for simulation
    request_data = {
        "customer": args.customer,
        "room_type": args.room_type,
        "nights": args.nights,
        "check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "special_requests": ["late_checkout", "extra_towels"]
    }
    
    if args.debug:
        print(f"Input Request: {request_data}")
        print("-" * 30)
    
    # Initialize state and execute workflow
    initial_state = HotelState(request=request_data)
    
    try:
        hotel_graph = build_graph()
        final_state: HotelState = hotel_graph.invoke(initial_state)
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 WORKFLOW RESULTS")
        print("=" * 50)
        
        if final_state.booking:
            print(f"Booking: {final_state.booking}")
        if final_state.housekeeping:
            print(f"Housekeeping: {final_state.housekeeping}")
        if final_state.customer_service:
            print(f"Customer Service: {final_state.customer_service}")
        
        if final_state.errors:
            print(f"\n⚠️  Errors encountered: {final_state.errors}")
            
        if args.debug:
            print(f"\n🔍 Full State Debug:")
            print(final_state.to_dict())
            
    except Exception as e:
        print(f"❌ System error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
