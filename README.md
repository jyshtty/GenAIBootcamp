# 🏨 Multi-Agent Hotel Management System


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

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

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
# Run the basic example
python -m src.agents

# Run with debugging
python -m src.agents --debug
```

## 📁 Project Structure

Your final submission should follow this structure:
```
hotel-management-system/
├── README.md                 # Your implementation documentation
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── src/
│   ├── __init__.py
│   ├── agents.py            # Main application
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py         # State management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── booking.py       # Booking agent
│   │   ├── housekeeping.py  # Housekeeping agent
│   │   └── customer_service.py  # Customer service agent
│   └── utils/
│       ├── __init__.py
│       ├── dial_client.py   # EPAM DIAL API client
│       └── mocks.py         # Mock data and APIs

```

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


## 📋 How You Will Be Evaluated

- **Total marks:** 100 (+ up to 10 bonus). **Passing marks:** 70/100.
- Evaluation focuses on whether your **multi-agent system shows understanding of orchestration**: booking, housekeeping, and customer service agents; LangGraph workflow; conditional routing and basic error handling.
- **Leniency:** Partial implementations are acceptable if they demonstrate the concepts. Basic error handling is enough if core routing works. Minor implementation issues are not heavily penalized when core agent logic is correct.

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
python -m src.agents

# Test DIAL API connection
python -m src.utils.dial_client

# Run with different parameters
python -m src.agents --customer "John Smith" --room-type "Suite" --nights 3
```
