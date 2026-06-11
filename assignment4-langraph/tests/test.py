"""
Unit tests for genaibootcampassign4 (Hotel Management Multi-Agent Demo).
Uses unittest. Run from repo root: python -m unittest tests.test
Requires: pip install -r requirements.txt
"""

import os
import sys
import unittest
from datetime import datetime
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.state import HotelState, create_initial_state, state_to_dict
from src.agents.booking import booking_agent
from src.agents.housekeeping import housekeeping_agent
from src.agents.customer_service import customer_service_agent
from src.main import build_graph, should_continue_to_housekeeping


class TestRequiredFiles(unittest.TestCase):
    """Required files for submission."""

    def test_required_files_exist(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        required = [
            "README.md",
            "requirements.txt",
            ".env.example",
            "src/main.py",
            "src/models/state.py",
            "src/agents/booking.py",
            "src/agents/housekeeping.py",
            "src/agents/customer_service.py",
            "src/utils/dial_client.py",
            "src/utils/mocks.py",
        ]
        for path in required:
            full = os.path.join(root, path)
            self.assertTrue(os.path.exists(full), f"Required file missing: {path}")


class TestStateManagement(unittest.TestCase):
    """State creation and serialization."""

    def test_create_initial_state(self):
        request = {"customer": "Alice", "room_type": "Standard", "nights": 2}
        state = create_initial_state(request)
        self.assertIn("request", state)
        self.assertEqual(state["request"], request)
        self.assertIn("booking", state)
        self.assertEqual(state["booking"], {})
        self.assertIn("housekeeping", state)
        self.assertIn("customer_service", state)
        self.assertEqual(state["errors"], [])
        self.assertEqual(state["workflow_step"], 0)

    def test_state_to_dict(self):
        state = create_initial_state({"customer": "Bob"})
        d = state_to_dict(state)
        self.assertIsInstance(d, dict)
        self.assertEqual(d.get("request", {}).get("customer"), "Bob")


class TestBookingAgent(unittest.TestCase):
    """Booking agent success and validation."""

    def test_booking_agent_success_standard(self):
        state = create_initial_state({
            "customer": "Test User",
            "room_type": "Standard",
            "nights": 2,
            "check_in": "2026-02-01",
        })
        out = booking_agent(state)
        self.assertIn("booking", out)
        self.assertEqual(out["booking"].get("status"), "Confirmed")
        self.assertEqual(out["booking"].get("room_type"), "Standard")
        self.assertIn(out["booking"].get("room_number"), ("101", "102", "103"))
        self.assertEqual(out["booking"].get("total_cost"), 300)
        self.assertEqual(out.get("workflow_step"), 1)

    def test_booking_agent_validation_no_customer(self):
        state = create_initial_state({
            "customer": "",
            "room_type": "Standard",
            "nights": 1,
        })
        out = booking_agent(state)
        self.assertEqual(out["booking"].get("status"), "Failed")
        self.assertIn("errors", out)


class TestHousekeepingAgent(unittest.TestCase):
    """Housekeeping agent behavior."""

    def test_housekeeping_when_booking_confirmed(self):
        state = create_initial_state({"customer": "X", "room_type": "Suite", "nights": 1})
        state["booking"] = {
            "status": "Confirmed",
            "room_number": "301",
            "room_type": "Suite",
            "check_in": "2026-02-01",
        }
        out = housekeeping_agent(state)
        self.assertIn("housekeeping", out)
        self.assertEqual(out["housekeeping"].get("status"), "Ready")
        self.assertEqual(out["housekeeping"].get("room_id"), "301")
        self.assertIn("checklist", out["housekeeping"])
        self.assertEqual(out.get("workflow_step"), 2)

    def test_housekeeping_skipped_when_booking_failed(self):
        state = create_initial_state({"customer": "X", "room_type": "Standard", "nights": 1})
        state["booking"] = {"status": "Failed", "reason": "No rooms"}
        out = housekeeping_agent(state)
        self.assertEqual(out["housekeeping"].get("status"), "Skipped")


class TestConditionalRouting(unittest.TestCase):
    """Workflow routing from booking."""

    def test_should_continue_to_housekeeping_when_confirmed(self):
        state = {"booking": {"status": "Confirmed"}}
        self.assertEqual(should_continue_to_housekeeping(state), "housekeeping")

    def test_should_continue_to_customer_service_when_failed(self):
        state = {"booking": {"status": "Failed"}}
        self.assertEqual(should_continue_to_housekeeping(state), "customer_service")

    def test_should_continue_to_customer_service_when_no_booking(self):
        state = {}
        self.assertEqual(should_continue_to_housekeeping(state), "customer_service")


class TestFullWorkflow(unittest.TestCase):
    """End-to-end graph invocation."""

    def test_full_workflow_success_path(self):
        graph = build_graph()
        request = {
            "customer": "Workflow Test",
            "room_type": "Deluxe",
            "nights": 1,
            "check_in": datetime(2026, 2, 1).strftime("%Y-%m-%d"),
        }
        initial = create_initial_state(request)
        with patch("sys.stdout", StringIO()):
            final = graph.invoke(initial)
        self.assertEqual(final.get("booking", {}).get("status"), "Confirmed")
        self.assertEqual(final.get("housekeeping", {}).get("status"), "Ready")
        self.assertIn("customer_service", final)

    def test_full_workflow_booking_failed_path(self):
        graph = build_graph()
        request = {"customer": "", "room_type": "Standard", "nights": 1}
        initial = create_initial_state(request)
        with patch("sys.stdout", StringIO()):
            final = graph.invoke(initial)
        self.assertEqual(final.get("booking", {}).get("status"), "Failed")
        hk = final.get("housekeeping") or {}
        self.assertNotEqual(hk.get("status"), "Ready")


class TestMocks(unittest.TestCase):
    """Mock data and helpers."""

    def test_room_rates_and_availability(self):
        from src.utils.mocks import ROOM_RATES, get_available_rooms, reserve_room
        self.assertEqual(ROOM_RATES["Standard"], 150)
        self.assertEqual(ROOM_RATES["Deluxe"], 250)
        self.assertEqual(ROOM_RATES["Suite"], 350)
        self.assertIn("101", get_available_rooms("Standard"))
        self.assertEqual(reserve_room("Suite"), "301")


if __name__ == "__main__":
    unittest.main()
