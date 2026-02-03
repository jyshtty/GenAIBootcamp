# answers guest questions using DIAL when we have key

import logging
from typing import Dict, Any, List

from src.models.state import HotelState
from src.utils.dial_client import DIALClient

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = (
    "We're sorry we couldn't assist you via AI right now. "
    "Please contact the front desk or call extension 0 for assistance."
)


def customer_service_agent(state: HotelState) -> Dict[str, Any]:
    # build context from booking/housekeeping, ask DIAL for reply. or use fallback
    logger.info("Customer Service Agent: Handling guest interaction")
    print("Customer Service Agent: Handling guest interaction...")

    errors = list(state.get("errors") or [])
    interaction_log: List[Dict[str, Any]] = []

    try:
        dial = DIALClient()
        has_dial = dial and dial.client

        context_parts = []
        if state.get("booking"):
            context_parts.append(f"Booking: {state['booking']}")
        if state.get("housekeeping"):
            context_parts.append(f"Housekeeping: {state['housekeeping']}")
        context = "\n".join(context_parts) if context_parts else "No booking or housekeeping data."

        # what would guest be asking
        if (state.get("booking") or {}).get("status") == "Failed":
            customer_message = "My booking failed. What can I do?"
        elif (state.get("housekeeping") or {}).get("status") == "Ready":
            customer_message = "Is my room ready? When can I check in?"
        else:
            customer_message = "I have a question about my reservation."

        if has_dial:
            response = dial.generate_response(context, customer_message)
        else:
            response = FALLBACK_MESSAGE

        # optional sentiment if they left feedback
        sentiment_result = None
        request = state.get("request") or {}
        feedback = request.get("feedback") or request.get("complaint")
        if feedback and has_dial:
            sentiment_result = dial.analyze_sentiment(str(feedback))
            interaction_log.append({"type": "sentiment", "result": sentiment_result})

        interaction_log.append({"query": customer_message, "response": response})

        customer_service = {
            "response": response,
            "resolution": "addressed" if response else "pending",
            "interaction_log": interaction_log,
            "sentiment": sentiment_result,
        }

        preview = response[:80] + "..." if len(response) > 80 else response
        print(f"   Response: {preview}")
        logger.info("Customer Service: response generated")

        return {"customer_service": customer_service, "workflow_step": 3}

    except Exception as e:
        logger.exception("Customer Service Agent error")
        print(f"Customer Service Agent error: {e}")
        return {
            "customer_service": {
                "response": FALLBACK_MESSAGE,
                "resolution": "error",
                "interaction_log": interaction_log,
                "error": str(e),
            },
            "errors": errors + [f"Customer service error: {str(e)}"],
            "workflow_step": 3,
        }
