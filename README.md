# 🏨 Multi-Agent Hotel Management System

**Assignment Duration:** 1 Week  
**Target Audience:** Intermediate Level Developers  
**Focus:** Technical Implementation with LangGraph

## 🎯 Learning Objectives

By completing this assignment, you will:
- Build a multi-agent system using **LangGraph**
- Implement agent orchestration and state management
- Practice mocking external APIs and services
- Design scalable agent workflows
- Integrate with **EPAM DIAL** for AI-powered responses

## 📋 Prerequisites

- Python 3.11+ experience
- Basic understanding of async programming
- Familiarity with REST APIs
- Basic knowledge of AI/LLM concepts

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and navigate to project
cd AgentsAssignment

# Create virtual environment (e.g. menv or venv)
python -m venv menv
# Activate: Windows: menv\Scripts\activate  |  Linux/Mac: source menv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create `.env` file in the project root:
```env
DIAL_API_KEY=your_dial_api_key_here
```

**Getting your DIAL API Key:**
1. Obtain your API key from the EPAM Support
2. Replace `your_dial_api_key_here` with your actual key

### 3. Run the Example
```bash
# Run the main application (either entry point works)
python -m src.main
# or
python -m src.agents

# Run with debugging
python -m src.main --debug

# Example with parameters
python -m src.main --customer "John Smith" --room-type "Suite" --nights 3
```

## 📁 Project Structure

Implementation follows this structure:
```
AgentsAssignment/
├── README.md                 # Implementation documentation
├── requirements.txt          # Dependencies
├── .env.example              # Environment template (DIAL_API_KEY, optional DIAL_TEMPERATURE)
├── src/
│   ├── __init__.py
│   ├── main.py               # Main application (orchestration, CLI, workflow graph)
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py         # State schema (TypedDict), create_initial_state, state_to_dict
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── __main__.py       # Entry point for python -m src.agents
│   │   ├── booking.py       # Booking agent (reservations, mock availability, payment simulation)
│   │   ├── housekeeping.py  # Housekeeping agent (room prep, checklist, mock schedule)
│   │   └── customer_service.py  # Customer service agent (DIAL integration, responses, sentiment)
│   └── utils/
│       ├── __init__.py
│       ├── dial_client.py   # EPAM DIAL API client
│       └── mocks.py          # Mock data and APIs (rooms, housekeeping, payment, etc.)
```

## 📋 Implementation Details

- **State:** LangGraph state is a TypedDict (`HotelState`) with `request`, `booking`, `housekeeping`, `customer_service`, `errors`, `workflow_step`. Nodes receive and return partial state dicts.
- **Workflow:** `START -> booking -> (housekeeping | customer_service) -> customer_service -> END`. Conditional routing: if booking status is Confirmed, go to housekeeping then customer_service; otherwise go directly to customer_service.
- **Booking agent:** Validates request, uses mock room availability and rates from `mocks.py`, simulates payment via `mock_payment_confirm`, returns booking and errors.
- **Housekeeping agent:** Runs only after confirmed booking; prepares room using mock schedule, checklist, staff; optional maintenance from mocks.
- **Customer service agent:** Uses DIAL `generate_response` for guest queries; optional `analyze_sentiment` when `feedback`/`complaint` in request; fallback message when DIAL is not configured.
- **Logging:** Standard logging (INFO) for workflow steps and agent actions; `--debug` increases verbosity.
- **DIAL:** Integrated in customer_service for AI-generated responses; test with `python -m src.utils.dial_client`.

## 🏗️ System Architecture

### Core Agents

| Agent | Primary Responsibility | Key Functions |
|-------|----------------------|--------------|
| **Booking Agent** | Room reservation management | Create, update, cancel bookings; Room availability |
| **Housekeeping Agent** | Room maintenance coordination | Status updates, cleaning schedules, room preparation |
| **Customer Service Agent** | Guest support and inquiries | Handle complaints, provide information, resolve issues |


## 📋 Core Requirements

### Phase 1: Basic Implementation (Required)
1. **State Management**
   - Implement shared state object using LangGraph
   - Track booking, housekeeping, and customer service data
   - Handle state transitions between agents

2. **Agent Implementation**
   - Create three functional agents with mock data
   - Implement basic decision-making logic
   - Add proper error handling and validation

3. **Workflow Orchestration**
   - Build LangGraph workflow connecting all agents
   - Implement conditional routing based on agent responses
   - Add logging for debugging and monitoring


## 📝 Submission Requirements

### Required Files
- ✅ Complete source code following the specified structure
- ✅ Updated README.md with your implementation details
- ✅ Requirements.txt with all dependencies
- ✅ .env.example with required environment variables
- ✅ Demonstration of working DIAL API integration

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [EPAM DIAL Service](https://ai-proxy.lab.epam.com)
- [Python Async Programming Guide](https://docs.python.org/3/library/asyncio.html)
- [Azure OpenAI Client Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/quickstart)

## 🔧 Development Commands

```bash
# Run the main application
python -m src.main
# or
python -m src.agents

# Test DIAL API connection
python -m src.utils.dial_client

# Run with different parameters
python -m src.main --customer "John Smith" --room-type "Suite" --nights 3
```
