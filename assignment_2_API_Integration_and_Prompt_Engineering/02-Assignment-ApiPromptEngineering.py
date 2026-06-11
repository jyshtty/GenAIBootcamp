# ============================================================
# SOLUTIONS FOR TASKS 1–4
# ============================================================

# Updated configuration for DIAL API

import os
import json
from openai import AzureOpenAI

API_KEY = os.getenv("DIAL_API_KEY", "dial-uuz93obm0e4q01s2rlnnvenljb6")

AZURE_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_VERSION = "2025-04-01-preview"
DEPLOYMENT_NAME = "gpt-5-mini-2025-08-07"


# Initialize Client
client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
)


# ============================================================
# Helper Function
# ============================================================

def get_completion(messages, model=DEPLOYMENT_NAME):
    """
    Calls the DIAL Chat Completions API
    and returns assistant response text.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"


# ============================================================
# TASK 1
# classify_and_prioritize(ticket_text)
# ============================================================

def classify_and_prioritize(ticket_text):

    prompt = f"""
You are an AI support assistant.

Classify the support ticket into ONE category:
- Bug
- Feature Request
- Question
- Praise
- Complaint

Also assign a priority:
- High
- Medium
- Low

Examples:

Ticket:
"The application crashes every time I click the payment button."
Output:
{{"category":"Bug","priority":"High"}}

Ticket:
"It would be great if the dashboard supported dark mode."
Output:
{{"category":"Feature Request","priority":"Medium"}}

Ticket:
"How can I change my account password?"
Output:
{{"category":"Question","priority":"Low"}}

Ticket:
"Your customer support team was extremely helpful."
Output:
{{"category":"Praise","priority":"Low"}}

Ticket:
"I am very unhappy with the delayed response from your team."
Output:
{{"category":"Complaint","priority":"Medium"}}

Now classify this ticket:

Ticket:
"{ticket_text}"

Return ONLY valid JSON.
"""

    messages = [{"role": "user", "content": prompt}]

    response = get_completion(messages)

    try:
        return json.loads(response)
    except:
        return response


# ============================================================
# TASK 2
# solve_logic_puzzle(puzzle)
# ============================================================

def solve_logic_puzzle(puzzle):

    prompt = f"""
Solve the puzzle carefully using step-by-step reasoning.

Example Puzzle:
Three students — Tom, Jerry, and Mike —
are standing in a line.

Rules:
1. Tom is not first.
2. Jerry is before Mike.

Reasoning:
- Jerry must stand before Mike.
- Tom cannot be first.
- One valid order satisfying both rules is:
Jerry, Tom, Mike

Final Answer:
Jerry, Tom, Mike

-----------------------------------

Now solve this puzzle:

{puzzle}

Think step-by-step internally.

Return ONLY the final order from front to back.
"""

    messages = [{"role": "user", "content": prompt}]

    response = get_completion(messages)

    return response.strip()


# ============================================================
# TASK 3
# generate_python_function(description)
# ============================================================

def generate_python_function(description):

    prompt = f"""
Generate a correct and runnable Python function.

Example:

Description:
"Create a Python function named add_numbers
that takes two integers and returns their sum."

Code:
def add_numbers(a, b):
    return a + b

-----------------------------------

Now generate code for:

Description:
"{description}"

Return ONLY Python code.
Do NOT include markdown.
Do NOT include explanations.
"""

    messages = [{"role": "user", "content": prompt}]

    response = get_completion(messages)

    return response.strip()


# ============================================================
# TASK 4
# parse_email_body(email_text)
# ============================================================

def parse_email_body(email_text):

    prompt = f"""
Extract the PRIMARY sender's contact details
from the email body.

Rules:
- Extract:
  - Name
  - Email
  - Phone
- Ignore forwarded email chains
- Ignore quoted replies
- Ignore secondary signatures
- Return ONLY valid JSON
- If no clear signature exists, return null

Example:

Email:
"
Hi Team,

Please review the document.

Regards,
Jane Doe
Product Manager
jane.doe@company.com
+1 555-123-4567

----- Forwarded Message -----

John Smith
john@other.com
"

Output:
{{
    "name": "Jane Doe",
    "email": "jane.doe@company.com",
    "phone": "+1 555-123-4567"
}}

-----------------------------------

Now parse this email:

{email_text}
"""

    messages = [{"role": "user", "content": prompt}]

    response = get_completion(messages)

    try:
        return json.loads(response)
    except:
        return response


# ============================================================
# TESTING TASK 1
# ============================================================

print("\n================ TASK 1 ================\n")

ticket = """
The mobile application crashes whenever
I upload a profile picture.
"""

result = classify_and_prioritize(ticket)

print(result)


# ============================================================
# TESTING TASK 2
# ============================================================

print("\n================ TASK 2 ================\n")

puzzle = """
Four friends, Alex, Ben, Chris, and David,
are standing in a line.

Rules:
- Chris is not at either end.
- Ben is directly in front of Alex.
- David is somewhere behind Chris.

Determine the order from front to back.
"""

result = solve_logic_puzzle(puzzle)

print(result)


# ============================================================
# TESTING TASK 3
# ============================================================

print("\n================ TASK 3 ================\n")

description = """
Create a Python function named calculate_average
that takes a list of numbers and returns their average.
"""

result = generate_python_function(description)

print(result)


# ============================================================
# TESTING TASK 4
# ============================================================

print("\n================ TASK 4 ================\n")

email_text = """
Hello Team,

Please find the updated report attached.

Regards,
Ajay Kumar Shetty
Software Engineer
ajay.shetty@example.com
+91 9876543210

----- Forwarded Message -----

John Doe
john@example.com
+1 222-333-4444
"""

result = parse_email_body(email_text)

print(result)
