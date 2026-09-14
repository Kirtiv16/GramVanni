import os
import time
import requests
from google import genai


# =========================
# API CONFIGURATION
# =========================

PRISM_HOST = "https://prism.blockconvey.com"
PRISM_PROJECT_ID = "7227f745-0bd7-471f-bec7-909121a6a39f"

PRISM_API_KEY = "pt-sk-797f82eb321440f68a4da482b5d1e441"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# PRISM LOGGING
# =========================

def log_to_prism(user_input, ai_output, latency_ms):

    url = f"{PRISM_HOST}/api/traces"

    headers = {
        "Content-Type": "application/json",
        "X-PRISMtrace-Key": PRISM_API_KEY
    }

    payload = {
        "project_id": PRISM_PROJECT_ID,
        "model": "gemini-3.5-flash-lite",
        "input_messages": [
            {
                "role": "user",
                "content": user_input
            }
        ],
        "output_message": ai_output,
        "latency_ms": int(latency_ms),
        "session_id": "hackathon-live-demo",
        "agent_id": "rural-scheme-advisor"
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=5
        )

        print(f"PRISM Log Status: {response.status_code}")

        return response.status_code == 200

    except Exception as e:

        print(f"Failed to reach PRISM: {e}")

        return False


# =========================
# GEMINI SCHEME ASSISTANT
# =========================

def evaluate_scheme(user_statement):

    prompt = f"""
You are a helpful rural government scheme assistant in India.

Citizen's spoken query:
"{user_statement}"

Consider these schemes:

1. PM-Kisan Samman Nidhi
   - Financial support for eligible farmers.

2. Ayushman Bharat - PM-JAY
   - Health coverage for eligible beneficiaries.

Give a clear, simple response in conversational Hindi.

Mention:
- Which scheme may be relevant
- Why it may be relevant
- What benefit it provides

Do not claim that the citizen is definitely eligible.
Say that final eligibility must be verified using official government records.
Keep the answer short and easy to understand.
"""

    start_time = time.time()

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    latency = (time.time() - start_time) * 1000

    ai_reply = response.text.strip()

    # Send result to PRISM
    log_to_prism(
        user_statement,
        ai_reply,
        latency
    )

    # Temporary demo classification
    if any(
        word in user_statement.lower()
        for word in [
            "kisan",
            "farmer",
            "खेती",
            "किसान",
            "जमीन"
        ]
    ):
        scheme_name = "PM-Kisan"

    else:
        scheme_name = "Ayushman Bharat"

    return ai_reply, scheme_name, latency


# =========================
# TEST
# =========================

if __name__ == "__main__":

    test_query = "मैं एक छोटा किसान हूँ, मुझे खेती के लिए सहायता चाहिए"

    reply, scheme, lat = evaluate_scheme(test_query)

    print("\n--- TEST SUCCESS ---")
    print(f"Scheme Chosen: {scheme}")
    print(f"AI Response: {reply}")
    print(f"Latency: {lat:.2f} ms")