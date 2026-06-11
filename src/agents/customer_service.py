"""Customer service agent.

Composes the guest-facing response and an interaction log entry. Uses the
EPAM DIAL client to enrich the response with an LLM-generated message when an
API key is available, falling back to a deterministic template otherwise so
the workflow stays robust in tests and offline environments.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Cache the DIAL client at module level so we only instantiate it once per
# process. We initialise lazily inside the function — touching the network
# during import would be wasteful and fragile under tests.
_dial_client = None
_dial_init_attempted = False


def _get_dial_client():
    """Return a cached DIAL client instance, or None if it cannot be created."""
    global _dial_client, _dial_init_attempted
    if _dial_init_attempted:
        return _dial_client

    _dial_init_attempted = True
    try:
        from src.utils.dial_client import DIALClient

        client = DIALClient()
        if getattr(client, "client", None) is None:
            logger.info("DIAL client unavailable; using template responses.")
            return None
        _dial_client = client
        logger.debug("DIAL client ready for customer service responses.")
        return _dial_client
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("DIAL client initialisation failed: %s", exc)
        return None


def _build_template_response(
    customer: str,
    booking: Dict[str, Any],
    housekeeping: Dict[str, Any],
) -> str:
    """Produce a deterministic guest response based on workflow state."""
    booking_status = booking.get("status", "Unknown")
    if booking_status == "Confirmed":
        room_type = booking.get("room_type", "room")
        room_number = booking.get("room_number", "TBD")
        nights = booking.get("nights", 1)
        total_cost = booking.get("total_cost", 0)
        hk_status = housekeeping.get("status", "in progress")
        return (
            f"Welcome, {customer}! Your {room_type} reservation is confirmed. "
            f"Room {room_number} for {nights} night(s), total ${total_cost}. "
            f"Housekeeping status: {hk_status}. We look forward to your stay!"
        )
    if booking_status == "Failed":
        reason = booking.get("reason", "an unexpected issue")
        return (
            f"We're sorry, {customer}. We could not complete your booking ({reason}). "
            f"Please review your request or contact our support team for assistance."
        )
    return (
        f"Hello {customer}, thank you for reaching out. "
        f"How may we help you today?"
    )


def _try_dial_response(context: str, query: str) -> Optional[str]:
    """Attempt to generate an LLM response via DIAL; return None on failure."""
    if os.getenv("DISABLE_DIAL", "").lower() in ("1", "true", "yes"):
        return None
    client = _get_dial_client()
    if client is None:
        return None
    try:
        text = client.generate_response(context=context, customer_query=query)
        if not text or text.startswith("❌"):
            return None
        return text.strip()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("DIAL response generation failed: %s", exc)
        return None


def customer_service_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Build the customer response and an interaction log entry."""
    print("🎧 Customer Service Agent: Handling customer interaction...")
    logger.info("Customer service agent processing booking outcome.")

    request = state.get("request", {}) or {}
    booking = state.get("booking", {}) or {}
    housekeeping = state.get("housekeeping", {}) or {}
    errors = state.get("errors", []) or []

    customer = request.get("customer") or "Guest"
    booking_status = booking.get("status", "Unknown")
    special_requests = request.get("special_requests") or []

    base_response = _build_template_response(customer, booking, housekeeping)

    # Try to enrich with DIAL — strictly optional.
    dial_context = (
        f"Booking status: {booking_status}. "
        f"Room: {booking.get('room_type', 'N/A')} #{booking.get('room_number', 'N/A')}. "
        f"Housekeeping: {housekeeping.get('status', 'N/A')}. "
        f"Special requests: {', '.join(special_requests) if special_requests else 'none'}. "
        f"Errors: {'; '.join(errors) if errors else 'none'}."
    )
    dial_query = (
        f"Write a concise, warm reply to guest {customer} based on the context. "
        f"Acknowledge their booking outcome and any special requests."
    )
    enriched = _try_dial_response(dial_context, dial_query)
    response = enriched or base_response
    response_source = "dial" if enriched else "template"

    interaction_log = {
        "timestamp": datetime.now().isoformat(),
        "customer": customer,
        "booking_status": booking_status,
        "housekeeping_status": housekeeping.get("status", "Unknown"),
        "errors": list(errors),
        "special_requests": list(special_requests),
        "response_source": response_source,
        "channel": "automated_agent",
    }

    print(f"💬 Response prepared for {customer} (source={response_source})")
    logger.info(
        "Customer service response generated for %s via %s.", customer, response_source
    )

    return {
        "customer_service": {
            "response": response,
            "interaction_log": interaction_log,
        },
        "workflow_step": 3,
    }
