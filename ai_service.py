import os

from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------

load_dotenv()


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b",
)


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

if not GROQ_API_KEY:

    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file."
    )


# ---------------------------------------------------------
# GROQ CLIENT
# ---------------------------------------------------------

client = Groq(
    api_key=GROQ_API_KEY
)


# ---------------------------------------------------------
# AI INCIDENT ANALYSIS
# ---------------------------------------------------------

def analyze_incident(
    service: str,
    severity: str,
    logs: str,
    memories: list,
):

    if memories:

        historical_context = "\n\n".join(
            [
                f"HISTORICAL MEMORY {i + 1}:\n{memory}"
                for i, memory in enumerate(memories)
            ]
        )

    else:

        historical_context = (
            "No relevant historical memories were found."
        )


    prompt = f"""
You are OpsMind, an AI Incident Response Agent.

Your job is to help production engineers investigate
software incidents using historical incident memory.

CURRENT INCIDENT

Service:
{service}

Severity:
{severity}

Logs:
{logs}


HISTORICAL INCIDENT MEMORY

{historical_context}


INSTRUCTIONS

Analyze the current incident using the historical memory.

You must:

1. Identify the likely root cause.
2. Explain why the historical incidents are relevant.
3. Recommend a proven resolution if one exists.
4. Recommend the relevant runbook.
5. Mention successful historical outcomes.
6. Mention resolution times when available.
7. Mention post-mortem lessons when available.
8. Clearly distinguish historical evidence from inference.
9. Do not invent historical incidents.
10. If the memory is insufficient, say so.


FORMAT YOUR RESPONSE AS:

## 🔍 Incident Diagnosis

[Diagnosis]

## 🧠 Historical Evidence

[Relevant historical incidents and why they matter]

## 🛠 Recommended Resolution

[Recommended action]

## 📘 Recommended Runbook

[Runbook]

## ⏱ Historical Resolution Time

[Historical resolution times]

## 📋 Post-Mortem Lessons

[Lessons]

## ⚠️ Confidence / Limitations

[Explain whether the recommendation is strongly supported by memory]
"""


    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a production incident response "
                    "assistant. Be precise, concise and evidence-based."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=1500,
    )


    return response.choices[0].message.content