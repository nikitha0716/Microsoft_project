import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()


HINDSIGHT_API_KEY = os.getenv(
    "HINDSIGHT_API_KEY"
)

HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io",
)


BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "opsmind-incidents",
)


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

if not HINDSIGHT_API_KEY:
    raise ValueError(
        "HINDSIGHT_API_KEY is missing. "
        "Add it to your .env file."
    )


# ---------------------------------------------------------
# HINDSIGHT CLIENT
# ---------------------------------------------------------

hindsight = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY,
    timeout=60.0,
)


# ---------------------------------------------------------
# INITIALIZE MEMORY BANK
# ---------------------------------------------------------

def initialize_memory():

    try:

        hindsight.create_bank(
            bank_id=BANK_ID,
            name="OpsMind Incident Memory",
            mission=(
                "Remember production incidents, "
                "their symptoms, root causes, "
                "successful resolutions, runbooks, "
                "resolution times and post-mortems. "
                "Prioritize operational knowledge that "
                "helps engineers resolve future incidents."
            ),
        )

    except Exception as e:

        # The bank may already exist.
        # That is not a fatal error.
        error_text = str(e).lower()

        if (
            "already exists" not in error_text
            and "409" not in error_text
            and "conflict" not in error_text
        ):
            raise


# ---------------------------------------------------------
# STORE INCIDENT
# ---------------------------------------------------------

def remember_incident(
    incident_id: str,
    content: str,
):

    hindsight.retain(
        bank_id=BANK_ID,
        content=content,
        context="Production incident post-mortem",
        document_id=incident_id,
        metadata={
            "source": "OpsMind",
            "type": "incident",
            "incident_id": incident_id,
        },
        retain_async=False,
    )


# ---------------------------------------------------------
# RECALL SIMILAR INCIDENTS
# ---------------------------------------------------------

def recall_similar_incidents(
    service: str,
    severity: str,
    logs: str,
):

    query = f"""
Find historical production incidents similar to this incident.

Service:
{service}

Severity:
{severity}

Current symptoms and logs:
{logs}

Focus on:

1. Similar symptoms
2. Similar root causes
3. Successful resolutions
4. Runbooks that worked
5. Resolution times
6. Post-mortem lessons
"""

    result = hindsight.recall(
        bank_id=BANK_ID,
        query=query,
        budget="mid",
        max_tokens=5000,
    )

    memories = []

    for memory in result.results:

        memories.append(
            memory.text
        )

    return memories


# ---------------------------------------------------------
# GET MEMORY COUNT
# ---------------------------------------------------------

def get_memory_count():

    result = hindsight.list_memories(
        bank_id=BANK_ID,
        limit=100,
        offset=0,
    )

    if hasattr(result, "total"):
        return result.total

    if hasattr(result, "items"):
        return len(result.items)

    return 0