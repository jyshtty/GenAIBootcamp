# Hotel Management System - Application Guide

This file has everything about what the app does, how to run it, and example outputs.

---

## What the application does (features)

- **Three agents** that work one after the other: Booking, Housekeeping, Customer Service. They share one state (a dict) that gets updated as the flow runs.

- **Booking agent**
  - Takes customer name, room type (Standard / Deluxe / Suite), nights, check-in.
  - Checks if we have that room type free (using mock data).
  - Validates: need customer name, valid room type, nights at least 1.
  - Simulates payment (mock always succeeds in this demo).
  - Writes booking id, room number, total cost, status (Confirmed or Failed) into state.

- **Housekeeping agent**
  - Runs only when booking status is Confirmed.
  - For the booked room: marks it ready, sets a cleaning schedule slot, checklist (cleaned, stocked, inspected), and which staff is on that room (all from mocks).
  - If there is mock maintenance for that room it shows that too.

- **Customer service agent**
  - Always runs at the end.
  - Builds context from booking + housekeeping and asks EPAM DIAL (AI) for a reply to a guest question (e.g. "Is my room ready?" or "My booking failed, what can I do?").
  - If DIAL_API_KEY is not set it uses a fallback text instead.
  - Can do sentiment on feedback/complaint from the request if you pass that.

- **Workflow**
  - Start → Booking → if Confirmed then Housekeeping then Customer Service, else straight to Customer Service → End.
  - Logging is on so you see when each agent runs.

- **Mock data**
  - Rooms: Standard 101–103, Deluxe 201–202, Suite 301. Rates: 150 / 250 / 350 per night.
  - Housekeeping: schedule slots, staff (Maria, John, Lisa), optional maintenance for room 103.
  - No real payment or real APIs, everything is in-memory.

---

## How to run the application

### 1. Setup (one time)

Open terminal in the **AgentsAssignment** folder.

Create and activate virtual env (we use menv here):

```bash
python -m venv menv
```

Windows:

```bash
menv\Scripts\activate
```

Linux/Mac:

```bash
source menv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional: for AI replies you need a DIAL key. Copy `.env.example` to `.env` and set:

```env
DIAL_API_KEY=your_actual_key_here
```

If you dont set it the app still runs but customer service will use a fallback message.

### 2. Run the app

You can use either:

```bash
python -m src.main
```

or

```bash
python -m src.agents
```

Both do the same thing.

**Useful options:**

- `--customer "Name"` – guest name (default: Alice Johnson)
- `--room-type Standard|Deluxe|Suite` – room type (default: Deluxe)
- `--nights N` – number of nights (default: 2)
- `--debug` – more logging and print full state at the end

**Test DIAL only:**

```bash
python -m src.utils.dial_client
```

---

## Examples and outputs

### Example 1: Default run (Deluxe, 2 nights)

Command:

```bash
python -m src.main
```

What you get (something like this, dates will change):

```
Hotel Management System - Multi-Agent Demo
==================================================
Booking Agent: Processing reservation request...
Booking confirmed: BKXXXXXXXX for Alice Johnson
   Room: Deluxe #201, 2 night(s)
Housekeeping Agent: Preparing room for check-in...
   Room #201 ready. Schedule: 10:30-11:00
Customer Service Agent: Handling guest interaction...
DIAL Client initialized successfully.
   Response: Hello Ms. Johnson, thank you for reaching out...

==================================================
WORKFLOW RESULTS
==================================================
Booking: {'booking_id': 'BKXXXXXXXX', 'customer': 'Alice Johnson', 'room_type': 'Deluxe', 'room_number': '201', 'check_in': '2026-01-29', 'nights': 2, 'status': 'Confirmed', 'total_cost': 500, 'created_at': '...'}
Housekeeping: {'room_id': '201', 'room_type': 'Deluxe', 'status': 'Ready', 'task': 'prepare for check-in', 'schedule': '10:30-11:00', 'checklist': [{'item': 'cleaned', 'done': True}, {'item': 'stocked', 'done': True}, {'item': 'inspected', 'done': True}], 'staff': {...}, 'maintenance_scheduled': [], 'updated_at': '...'}
Customer Service: {'response': "Hello Ms. Johnson...", 'resolution': 'addressed', 'interaction_log': [...], 'sentiment': None}
```

So: booking confirmed, housekeeping marked room ready, customer service got an AI reply (or fallback if no key).

---

### Example 2: Suite, 2 nights, custom customer

Command:

```bash
python -m src.main --customer "John Smith" --room-type "Suite" --nights 2
```

Example output:

```
Hotel Management System - Multi-Agent Demo
==================================================
Booking Agent: Processing reservation request...
Booking confirmed: BK44E7600B for John Smith
   Room: Suite #301, 2 night(s)
Housekeeping Agent: Preparing room for check-in...
   Room #301 ready. Schedule: 11:30-12:00
Customer Service Agent: Handling guest interaction...
DIAL Client initialized successfully.
   Response: Hello Mr. Smith,

Thank you for reaching out! I'm happy to confirm that your S...

==================================================
WORKFLOW RESULTS
==================================================
Booking: {'booking_id': 'BK44E7600B', 'customer': 'John Smith', 'room_type': 'Suite', 'room_number': '301', 'check_in': '2026-01-29', 'nights': 2, 'status': 'Confirmed', 'total_cost': 700, 'created_at': '2026-01-28T18:53:09.836877'}
Housekeeping: {'room_id': '301', 'room_type': 'Suite', 'status': 'Ready', 'task': 'prepare for check-in', 'schedule': '11:30-12:00', 'checklist': [{'item': 'cleaned', 'done': True}, {'item': 'stocked', 'done': True}, {'item': 'inspected', 'done': True}], 'staff': {'id': 'HK003', 'name': 'Lisa', 'assigned_rooms': ['301', '103']}, 'maintenance_scheduled': [], 'updated_at': '2026-01-28T18:53:09.836877'}
Customer Service: {'response': "Hello Mr. Smith,  \n\nThank you for reaching out! I'm happy to confirm that your Suite, room 301, is ready and has been fully prepared for your arrival. Our housekeeping team has completed all necessary cleaning, stocking, and inspections to ensure everything is perfect for your stay.  \n\nCheck-in begins at 3:00 PM, so you're welcome to arrive any time from then. If you have any special requests or need assistance before your arrival, feel free to let us know. We look forward to welcoming you!  \n\nSafe travels,  \n[Your Name]  \nCustomer Service Team", 'resolution': 'addressed', 'interaction_log': [{'query': 'Is my room ready? When can I check in?', 'response': "..."}], 'sentiment': None}
```

So: Suite 301, 700 total (350 x 2), housekeeping ready, DIAL gave a full paragraph back.

---

### Example 3: Debug mode (see full state)

Command:

```bash
python -m src.main --customer "Jane Doe" --room-type "Standard" --nights 1 --debug
```

You get the same flow plus:

- Input request printed at the start.
- At the end a "Full State Debug:" section with the entire state dict (request, booking, housekeeping, customer_service, errors, workflow_step). Useful to see exactly what each agent left in state.

---

### Example 4: When booking "fails" (validation)

If you mess with the code to pass invalid data (e.g. no customer or room type not in the list) then booking agent returns status Failed. Then the graph skip housekeeping and go straight to customer service. Customer service will still run and typically say something like "My booking failed. What can I do?" and DIAL (or fallback) will answer. So you still get a reply and the errors list will have the validation message.

---

## Quick reference

| What you want              | Command / note                                      |
|----------------------------|-----------------------------------------------------|
| Run with defaults          | `python -m src.main` or `python -m src.agents`     |
| Custom guest & room        | `python -m src.main --customer "X" --room-type Suite --nights 3` |
| More logs + full state     | add `--debug`                                      |
| Test DIAL only             | `python -m src.utils.dial_client`                   |
| Room types                 | Standard, Deluxe, Suite                            |

Thats it. For more on project layout and setup see README.md.
