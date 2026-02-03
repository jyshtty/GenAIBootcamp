"""
Tests for Week 04 AgentsAssignment - README and assignment requirements.
Run from AgentsAssignment: python -m pytest tests/ -v
Or: python tests/test_application.py
"""

import os
import sys
from datetime import datetime
from io import StringIO
from unittest.mock import patch

# run from project root (AgentsAssignment)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.state import HotelState, create_initial_state, state_to_dict
from src.agents.booking import booking_agent
from src.agents.housekeeping import housekeeping_agent
from src.agents.customer_service import customer_service_agent
from src.main import build_graph, should_continue_to_housekeeping


# ---- Required files (README / Submission) ----
def test_required_files_exist():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required = [
        "README.md",
        "requirements.txt",
        ".env.example",
        "src/main.py",
        "src/models/__init__.py",
        "src/models/state.py",
        "src/agents/__init__.py",
        "src/agents/__main__.py",
        "src/agents/booking.py",
        "src/agents/housekeeping.py",
        "src/agents/customer_service.py",
        "src/utils/__init__.py",
        "src/utils/dial_client.py",
        "src/utils/mocks.py",
    ]
    for path in required:
        full = os.path.join(root, path)
        assert os.path.exists(full), f"Required file missing: {path}"


# ---- State Management (README Phase 1) ----
def test_state_management_initial_state():
    request = {"customer": "Alice", "room_type": "Standard", "nights": 2}
    state = create_initial_state(request)
    assert "request" in state and state["request"] == request
    assert "booking" in state and state["booking"] == {}
    assert "housekeeping" in state and state["housekeeping"] == {}
    assert "customer_service" in state and state["customer_service"] == {}
    assert "errors" in state and state["errors"] == []
    assert "workflow_step" in state and state["workflow_step"] == 0


def test_state_to_dict():
    state = create_initial_state({"customer": "Bob"})
    d = state_to_dict(state)
    assert isinstance(d, dict)
    assert d.get("request", {}).get("customer") == "Bob"


# ---- Booking Agent: success and validation (README Agent Implementation) ----
def test_booking_agent_success_standard():
    state = create_initial_state({
        "customer": "Test User",
        "room_type": "Standard",
        "nights": 2,
        "check_in": "2026-02-01",
    })
    out = booking_agent(state)
    assert "booking" in out
    assert out["booking"].get("status") == "Confirmed"
    assert out["booking"].get("room_type") == "Standard"
    assert out["booking"].get("room_number") in ("101", "102", "103")
    assert out["booking"].get("total_cost") == 300  # 150 * 2
    assert out.get("workflow_step") == 1


def test_booking_agent_success_deluxe():
    state = create_initial_state({
        "customer": "Jane",
        "room_type": "Deluxe",
        "nights": 1,
    })
    out = booking_agent(state)
    assert out["booking"].get("status") == "Confirmed"
    assert out["booking"].get("room_type") == "Deluxe"
    assert out["booking"].get("room_number") in ("201", "202")
    assert out["booking"].get("total_cost") == 250


def test_booking_agent_success_suite():
    state = create_initial_state({
        "customer": "John",
        "room_type": "Suite",
        "nights": 3,
    })
    out = booking_agent(state)
    assert out["booking"].get("status") == "Confirmed"
    assert out["booking"].get("room_type") == "Suite"
    assert out["booking"].get("room_number") == "301"
    assert out["booking"].get("total_cost") == 1050  # 350 * 3


def test_booking_agent_validation_no_customer():
    state = create_initial_state({
        "customer": "",
        "room_type": "Standard",
        "nights": 1,
    })
    out = booking_agent(state)
    assert out["booking"].get("status") == "Failed"
    assert "customer" in out["booking"].get("reason", "").lower() or any(
        "customer" in e.lower() for e in out.get("errors", [])
    )
    assert out.get("workflow_step") == 1


def test_booking_agent_validation_invalid_room_type():
    state = create_initial_state({
        "customer": "Alice",
        "room_type": "InvalidType",
        "nights": 1,
    })
    out = booking_agent(state)
    assert out["booking"].get("status") == "Failed"
    assert "errors" in out
    assert out.get("workflow_step") == 1


def test_booking_agent_validation_invalid_nights():
    state = create_initial_state({
        "customer": "Alice",
        "room_type": "Standard",
        "nights": 0,
    })
    out = booking_agent(state)
    assert out["booking"].get("status") == "Failed"
    assert "errors" in out


# ---- Housekeeping Agent (README) ----
def test_housekeeping_agent_when_booking_confirmed():
    state = create_initial_state({"customer": "X", "room_type": "Suite", "nights": 1})
    state["booking"] = {
        "status": "Confirmed",
        "room_number": "301",
        "room_type": "Suite",
        "check_in": "2026-02-01",
    }
    out = housekeeping_agent(state)
    assert "housekeeping" in out
    assert out["housekeeping"].get("status") == "Ready"
    assert out["housekeeping"].get("room_id") == "301"
    assert "checklist" in out["housekeeping"]
    assert "schedule" in out["housekeeping"]
    assert out.get("workflow_step") == 2


def test_housekeeping_agent_skipped_when_booking_failed():
    state = create_initial_state({"customer": "X", "room_type": "Standard", "nights": 1})
    state["booking"] = {"status": "Failed", "reason": "No rooms"}
    out = housekeeping_agent(state)
    assert out["housekeeping"].get("status") == "Skipped"
    assert "No confirmed booking" in out["housekeeping"].get("reason", "")


# ---- Conditional routing (README Workflow) ----
def test_should_continue_to_housekeeping_when_confirmed():
    state = {"booking": {"status": "Confirmed"}}
    assert should_continue_to_housekeeping(state) == "housekeeping"


def test_should_continue_to_customer_service_when_booking_failed():
    state = {"booking": {"status": "Failed"}}
    assert should_continue_to_housekeeping(state) == "customer_service"


def test_should_continue_to_customer_service_when_no_booking():
    state = {}
    assert should_continue_to_housekeeping(state) == "customer_service"


# ---- Full workflow: success path ----
def test_full_workflow_success_path():
    graph = build_graph()
    request = {
        "customer": "Workflow Test",
        "room_type": "Deluxe",
        "nights": 1,
        "check_in": (datetime(2026, 2, 1)).strftime("%Y-%m-%d"),
    }
    initial = create_initial_state(request)
    with patch("sys.stdout", StringIO()):  # suppress print
        final = graph.invoke(initial)
    assert final.get("booking", {}).get("status") == "Confirmed"
    assert final.get("housekeeping", {}).get("status") == "Ready"
    assert "customer_service" in final
    assert "response" in (final.get("customer_service") or {})
    assert "request" in final
    assert "errors" in final


# ---- Full workflow: booking failed -> customer_service only (no housekeeping prep) ----
def test_full_workflow_booking_failed_path():
    graph = build_graph()
    request = {
        "customer": "",  # invalid
        "room_type": "Standard",
        "nights": 1,
    }
    initial = create_initial_state(request)
    with patch("sys.stdout", StringIO()):
        final = graph.invoke(initial)
    assert final.get("booking", {}).get("status") == "Failed"
    # when booking fails we go straight to customer_service; housekeeping never runs
    # so housekeeping stays {} or has Skipped (we never set Ready)
    hk = final.get("housekeeping") or {}
    assert hk.get("status") != "Ready", "Housekeeping should not have run when booking failed"
    assert "customer_service" in final
    assert "response" in (final.get("customer_service") or {})


# ---- Customer service agent returns structure ----
def test_customer_service_agent_returns_response_and_log():
    state = create_initial_state({"customer": "X", "room_type": "Suite", "nights": 1})
    state["booking"] = {"status": "Confirmed", "room_number": "301", "room_type": "Suite"}
    state["housekeeping"] = {"status": "Ready", "room_id": "301"}
    with patch("sys.stdout", StringIO()):
        out = customer_service_agent(state)
    assert "customer_service" in out
    assert "response" in out["customer_service"]
    assert "interaction_log" in out["customer_service"]
    assert out.get("workflow_step") == 3


# ---- Mocks (README: mock data) ----
def test_mocks_room_rates_and_availability():
    from src.utils.mocks import ROOM_RATES, get_available_rooms, reserve_room
    assert ROOM_RATES["Standard"] == 150
    assert ROOM_RATES["Deluxe"] == 250
    assert ROOM_RATES["Suite"] == 350
    assert "101" in get_available_rooms("Standard")
    assert reserve_room("Suite") == "301"


def run_all():
    """Run all test functions and report pass/fail."""
    test_fns = [
        test_required_files_exist,
        test_state_management_initial_state,
        test_state_to_dict,
        test_booking_agent_success_standard,
        test_booking_agent_success_deluxe,
        test_booking_agent_success_suite,
        test_booking_agent_validation_no_customer,
        test_booking_agent_validation_invalid_room_type,
        test_booking_agent_validation_invalid_nights,
        test_housekeeping_agent_when_booking_confirmed,
        test_housekeeping_agent_skipped_when_booking_failed,
        test_should_continue_to_housekeeping_when_confirmed,
        test_should_continue_to_customer_service_when_booking_failed,
        test_should_continue_to_customer_service_when_no_booking,
        test_full_workflow_success_path,
        test_full_workflow_booking_failed_path,
        test_customer_service_agent_returns_response_and_log,
        test_mocks_room_rates_and_availability,
    ]
    failed = []
    for fn in test_fns:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
        except Exception as e:
            print(f"FAIL: {fn.__name__} - {e}")
            failed.append((fn.__name__, e))
    if failed:
        print(f"\n{len(failed)} failed, {len(test_fns) - len(failed)} passed")
        sys.exit(1)
    print(f"\nAll {len(test_fns)} tests passed.")
    sys.exit(0)


if __name__ == "__main__":
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(cwd)
    try:
        import pytest
        r = pytest.main([__file__, "-v", "--tb=short"])
        sys.exit(r)
    except ImportError:
        run_all()
