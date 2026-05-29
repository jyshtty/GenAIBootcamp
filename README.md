# 🏨 Multi-Agent Hotel Management System

**Focus:** Multi-agent orchestration with **LangGraph**, with optional EPAM **DIAL** integration for LLM-powered customer responses.

This project implements a small but complete hotel-operations workflow using three cooperating agents wired together by a LangGraph state machine:

1. **Booking Agent** validates the request, reserves a room, and simulates a payment authorisation.
2. **Housekeeping Agent** prepares the assigned room with a tier-aware checklist and team assignment.
3. **Customer Service Agent** composes the guest-facing response (template-based, with optional LLM enrichment via DIAL) and an interaction log.

A conditional edge from Booking routes confirmed bookings to Housekeeping, while failed bookings skip straight to Customer Service.

---

## 🗺️ Workflow

```
                ┌──────────┐
                │  START   │
                └────┬─────┘
                     │
                     ▼
              ┌──────────────┐
              │   booking    │
              └──────┬───────┘
                     │
        Confirmed ───┼─── Failed
                     │
            ┌────────┴────────┐
            ▼                 ▼
    ┌──────────────┐   ┌────────────────────┐
    │ housekeeping │   │ customer_service   │
    └──────┬───────┘   └─────────┬──────────┘
           │                     │
           └────────┬────────────┘
                    ▼
            ┌──────────────────┐
            │ customer_service │  (success path joins here)
            └────────┬─────────┘
                     │
                     ▼
                ┌─────────┐
                │   END   │
                └─────────┘
```

The conditional routing is implemented in `src/main.py`:

```python
def should_continue_to_housekeeping(state):
    booking = state.get("booking") or {}
    return "housekeeping" if booking.get("status") == "Confirmed" else "customer_service"
```

---

## 📁 Project Structure

```
genaibootcampassign4/
├── README.md                     # This document
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── src/
│   ├── __init__.py
│   ├── main.py                   # build_graph + CLI entry point
│   ├── agents/
│   │   ├── __init__.py           # Re-exports the three agents
│   │   ├── __main__.py           # `python -m src.agents`
│   │   ├── booking.py            # Validation, reservation, payment sim
│   │   ├── housekeeping.py       # Checklist, schedule, team assignment
│   │   └── customer_service.py   # Template + optional DIAL enrichment
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py              # HotelState TypedDict + helpers
│   └── utils/
│       ├── __init__.py
│       ├── dial_client.py        # EPAM DIAL (Azure OpenAI) wrapper
│       └── mocks.py              # ROOM_RATES, inventory, helpers
└── tests/
    ├── test.py                   # unittest suite
    └── test_application.py       # pytest suite
```

---

## 🧠 State Management

The workflow uses a `TypedDict` shared state (see `src/models/state.py`):

| Field              | Type             | Purpose                                          |
|--------------------|------------------|--------------------------------------------------|
| `request`          | `Dict[str, Any]` | Original customer request                        |
| `booking`          | `Dict[str, Any]` | Set by booking agent (Confirmed / Failed)        |
| `housekeeping`     | `Dict[str, Any]` | Set by housekeeping agent (Ready / Skipped)      |
| `customer_service` | `Dict[str, Any]` | Final response and interaction log               |
| `errors`           | `List[str]`      | Accumulated validation / processing errors       |
| `workflow_step`    | `int`            | Numeric stage (1 = booking, 2 = HK, 3 = CS)      |

Each agent is a pure function returning a partial-state dict, which LangGraph merges back into the shared state. This keeps agents independently testable and easy to reason about.

---

## 🤖 Agent Responsibilities

### Booking Agent (`src/agents/booking.py`)
- Validates: customer name present, room type ∈ {Standard, Deluxe, Suite}, nights ≥ 1.
- Computes `total_cost = ROOM_RATES[room_type] × nights`.
- Reserves a room via `src.utils.mocks.reserve_room`.
- Simulates a payment authorisation (mock transaction id, status, method).
- Sets `booking.status` to `Confirmed` or `Failed`, increments `workflow_step` to 1.

### Housekeeping Agent (`src/agents/housekeeping.py`)
- Skips with `status="Skipped"` when booking is not confirmed.
- Builds a tiered checklist (base + room-type extras + special-request additions).
- Assigns a team and an estimated completion window based on room tier.
- Records a maintenance follow-up flag for handoff to other systems.

### Customer Service Agent (`src/agents/customer_service.py`)
- Always returns a deterministic template response so tests are stable.
- Lazily initialises the EPAM DIAL client. When `DIAL_API_KEY` is set and the
  client succeeds, the LLM-generated reply replaces the template.
- Logs the interaction with timestamp, booking/housekeeping status, errors,
  special requests, and which source produced the response (`dial` or
  `template`).

---

## 🔌 EPAM DIAL Integration

`src/utils/dial_client.py` wraps `AzureOpenAI` against `https://ai-proxy.lab.epam.com`. It exposes:
- `get_completion(messages, model=None)` — raw chat completions.
- `analyze_sentiment(text)` — sentiment classification helper.
- `generate_response(context, customer_query)` — context-aware reply generator used by the customer-service agent.

Set the API key in `.env`:

```
DIAL_API_KEY=your_dial_api_key_here
DIAL_MODEL=gpt-4
DIAL_TEMPERATURE=0.7
```

If `DIAL_API_KEY` is missing or the call fails, the customer-service agent falls back to its template response — workflows stay green offline.

To explicitly disable DIAL calls (e.g. in CI), set `DISABLE_DIAL=1`.

---

## 🚀 Quick Start

```bash
# 1. Set up venv & install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env   # edit DIAL_API_KEY if you have one

# 3. Run the demo
python -m src.agents
python -m src.agents --customer "John Smith" --room-type Suite --nights 3
python -m src.agents --debug --special-request late_checkout --special-request high_floor
```

Sample output:

```
🏨 Booking Agent: Processing reservation request...
✅ Booking confirmed BKA1B2C3D4 | Alice Johnson | Deluxe #201 | 2 night(s) | $500
🧹 Housekeeping Agent: Preparing room...
✅ Room 201 (Deluxe) ready in ~1h with 11 checklist items by Housekeeping Team B
🎧 Customer Service Agent: Handling customer interaction...
💬 Response prepared for Alice Johnson (source=template)
```

---

## ✅ Testing

Two equivalent suites are provided:

```bash
# unittest
python -m unittest tests.test -v

# pytest (if installed)
python -m pytest tests/ -v
```

The suites cover:
- File layout requirements
- State creation and serialization
- Booking validation (missing customer, invalid room type, invalid nights) and success per room tier
- Housekeeping behaviour for confirmed/failed bookings
- Conditional routing (`should_continue_to_housekeeping`)
- Full graph invocation: success path and failure path
- Customer-service response & log structure
- Mocks (`ROOM_RATES`, `get_available_rooms`, `reserve_room`)

---

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [EPAM DIAL Service](https://ai-proxy.lab.epam.com)
- [Azure OpenAI Python SDK](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/quickstart)
