import os
import streamlit as st
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io"
)

HINDSIGHT_BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "opsmind-incidents"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="OpsMind",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #9ca3af;
        margin-bottom: 25px;
    }

    .memory-box {
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #30343b;
        background-color: #151820;
        margin-bottom: 12px;
    }

    .result-box {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30343b;
        background-color: #151820;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "last_memories" not in st.session_state:
    st.session_state.last_memories = []

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None


# =========================================================
# API CLIENTS
# =========================================================

hindsight = None
groq_client = None

hindsight_error = None
groq_error = None


# ---------------------------------------------------------
# HINDSIGHT
# ---------------------------------------------------------

if HINDSIGHT_API_KEY:

    try:

        hindsight = Hindsight(
            base_url=HINDSIGHT_BASE_URL,
            api_key=HINDSIGHT_API_KEY,
            timeout=60.0
        )

    except Exception as e:

        hindsight_error = str(e)

else:

    hindsight_error = (
        "HINDSIGHT_API_KEY is missing from .env"
    )


# ---------------------------------------------------------
# GROQ
# ---------------------------------------------------------

if GROQ_API_KEY:

    try:

        groq_client = Groq(
            api_key=GROQ_API_KEY
        )

    except Exception as e:

        groq_error = str(e)

else:

    groq_error = (
        "GROQ_API_KEY is missing from .env"
    )


# =========================================================
# HINDSIGHT MEMORY FUNCTIONS
# =========================================================

def initialize_memory():

    if hindsight is None:

        raise RuntimeError(
            "Hindsight client is not initialized."
        )

    try:

        hindsight.create_bank(
            bank_id=HINDSIGHT_BANK_ID,
            name="OpsMind Incident Memory",
            mission=(
                "Remember production incidents, "
                "their symptoms, root causes, resolutions, "
                "successful runbooks, resolution times and "
                "post-mortems. Help engineers resolve future "
                "incidents using historical operational knowledge."
            )
        )

    except Exception as e:

        error_text = str(e).lower()

        # The bank may already exist.
        if (
            "already exists" not in error_text
            and "409" not in error_text
            and "conflict" not in error_text
        ):

            raise


def remember_incident(
    incident_id,
    service,
    severity,
    root_cause,
    resolution,
    runbook,
    outcome,
    resolution_time,
    post_mortem
):

    if hindsight is None:

        raise RuntimeError(
            "Hindsight is not connected."
        )

    content = f"""
Production Incident

Incident ID:
{incident_id}

Service:
{service}

Severity:
{severity}

Root Cause:
{root_cause}

Resolution:
{resolution}

Runbook:
{runbook}

Outcome:
{outcome}

Resolution Time:
{resolution_time}

Post-Mortem:
{post_mortem}
"""

    hindsight.retain(
        bank_id=HINDSIGHT_BANK_ID,
        content=content,
        context="Production incident and post-mortem",
        document_id=incident_id,
        metadata={
            "source": "OpsMind",
            "type": "incident",
            "incident_id": incident_id,
            "service": service,
            "severity": severity,
            "outcome": outcome
        },
        retain_async=False
    )


def recall_similar_incidents(
    service,
    severity,
    logs
):

    if hindsight is None:

        raise RuntimeError(
            "Hindsight is not connected."
        )

    query = f"""
Find historical production incidents similar to this
current incident.

Current Service:
{service}

Current Severity:
{severity}

Current Logs:
{logs}

Find incidents with similar:

- service
- error messages
- symptoms
- root causes
- database failures
- connection pool problems
- HTTP status codes
- successful resolutions
- runbooks
- post-mortem lessons

Prioritize incidents that were successfully resolved.
"""

    result = hindsight.recall(
        bank_id=HINDSIGHT_BANK_ID,
        query=query,
        budget="mid",
        max_tokens=5000
    )

    memories = []

    for memory in result.results:

        memories.append({
            "text": memory.text,
            "type": getattr(
                memory,
                "type",
                "memory"
            )
        })

    return memories


def get_memory_count():

    if hindsight is None:
        return 0

    result = hindsight.list_memories(
        bank_id=HINDSIGHT_BANK_ID,
        limit=100,
        offset=0
    )

    return getattr(
        result,
        "total",
        len(getattr(result, "items", []))
    )


# =========================================================
# GROQ AI FUNCTION
# =========================================================

def analyze_incident(
    service,
    severity,
    logs,
    memories
):

    if groq_client is None:

        raise RuntimeError(
            "Groq is not connected."
        )

    if memories:

        historical_context = "\n\n".join(
            [
                f"""
HISTORICAL MEMORY {index}

{memory["text"]}
"""
                for index, memory
                in enumerate(memories, 1)
            ]
        )

    else:

        historical_context = (
            "No relevant historical memory was found."
        )


    prompt = f"""
You are OpsMind, an AI Incident Response Agent.

Your job is to help production engineers investigate
software incidents using historical operational memory.

==================================================
CURRENT INCIDENT
==================================================

Service:
{service}

Severity:
{severity}

Logs:
{logs}


==================================================
HISTORICAL MEMORY FROM HINDSIGHT
==================================================

{historical_context}


==================================================
TASK
==================================================

Analyze the current production incident.

Use the historical memories as evidence.

You must:

1. Identify the likely root cause.

2. Explain why the historical incidents
   are relevant.

3. Recommend a resolution.

4. Recommend the most relevant runbook.

5. Mention successful historical outcomes.

6. Mention historical resolution times.

7. Mention post-mortem lessons.

8. Clearly distinguish:
   - historical evidence
   - your inference

9. NEVER invent historical incidents.

10. If there is insufficient historical evidence,
    clearly say so.


==================================================
RESPONSE FORMAT
==================================================

## 🔍 Incident Diagnosis

Explain the likely root cause.

## 🧠 Historical Evidence

Explain which previous incidents are relevant.

## 🛠 Recommended Resolution

Give the recommended remediation.

## 📘 Recommended Runbook

Give the runbook name if historical evidence supports one.

## ⏱ Historical Resolution Time

Mention relevant previous resolution times.

## 📋 Post-Mortem Lessons

Mention lessons learned from previous incidents.

## ⚠️ Confidence & Limitations

Explain how strongly the historical evidence supports
the recommendation.
"""


    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise production "
                    "incident response assistant."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        max_tokens=1800
    )

    return response.choices[0].message.content


# =========================================================
# INITIALIZE HINDSIGHT BANK
# =========================================================

memory_ready = False

if hindsight:

    try:

        initialize_memory()

        memory_ready = True

    except Exception as e:

        hindsight_error = str(e)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🚨 OpsMind</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Memory-powered AI Incident Response Agent'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "OpsMind remembers previous production incidents, "
    "their root causes, resolutions and post-mortems."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🧠 OpsMind Status")

    st.divider()

    # Hindsight status

    if memory_ready:

        st.success(
            "Hindsight Memory Connected"
        )

        try:

            memory_count = get_memory_count()

            st.metric(
                "Stored Memories",
                memory_count
            )

        except Exception:

            st.metric(
                "Stored Memories",
                "Connected"
            )

    else:

        st.error(
            "Hindsight Not Connected"
        )

        if hindsight_error:

            st.caption(
                hindsight_error
            )


    st.divider()


    # Groq status

    if groq_client:

        st.success(
            "Groq AI Connected"
        )

        st.caption(
            f"Model: {GROQ_MODEL}"
        )

    else:

        st.error(
            "Groq Not Connected"
        )

        if groq_error:

            st.caption(
                groq_error
            )


    st.divider()


    st.markdown(
        """
        ### Architecture

        🚨 Incident

        ↓

        🧠 Hindsight Recall

        ↓

        📚 Historical Memory

        ↓

        🤖 Groq Reasoning

        ↓

        🛠 Recommendation

        ↓

        📋 Post-Mortem

        ↓

        🧠 Hindsight Retain
        """
    )


# =========================================================
# TABS
# =========================================================

investigate_tab, teach_tab = st.tabs(
    [
        "🚨 Investigate Incident",
        "🧠 Teach OpsMind"
    ]
)


# =========================================================
# INVESTIGATE TAB
# =========================================================

with investigate_tab:

    st.header(
        "New Production Incident"
    )

    st.caption(
        "Describe the current production failure. "
        "OpsMind will search its historical memory "
        "before generating a recommendation."
    )


    # -----------------------------------------------------
    # SERVICE
    # -----------------------------------------------------

    service = st.text_input(
        "Service",

        value="Payment API",

        key="investigate_service"
    )


    # -----------------------------------------------------
    # SEVERITY
    # -----------------------------------------------------

    severity = st.selectbox(
        "Severity",

        [
            "SEV-1",
            "SEV-2",
            "SEV-3",
            "SEV-4"
        ],

        key="investigate_severity"
    )


    # -----------------------------------------------------
    # LOGS
    # -----------------------------------------------------

    logs = st.text_area(
        "Error / Logs",

        value="""HTTP 503 Service Unavailable.

Connection pool exhausted.
Database connection timeout.
Retry attempts exceeded.""",

        height=180,

        key="investigate_logs"
    )


    # -----------------------------------------------------
    # INVESTIGATE BUTTON
    # -----------------------------------------------------

    investigate_button = st.button(
        "🔍 Investigate Incident",

        type="primary",

        use_container_width=True,

        key="investigate_button"
    )


    # -----------------------------------------------------
    # INVESTIGATION
    # -----------------------------------------------------

    if investigate_button:

        if not logs.strip():

            st.warning(
                "Please provide incident logs."
            )

        elif not memory_ready:

            st.error(
                "Hindsight memory is not connected. "
                "Check your HINDSIGHT_API_KEY."
            )

        elif not groq_client:

            st.error(
                "Groq is not connected. "
                "Check your GROQ_API_KEY."
            )

        else:

            # =============================================
            # STEP 1 — HINDSIGHT RECALL
            # =============================================

            with st.spinner(
                "🧠 Searching Hindsight memory..."
            ):

                try:

                    memories = recall_similar_incidents(
                        service=service,
                        severity=severity,
                        logs=logs
                    )

                    st.session_state.last_memories = memories

                except Exception as e:

                    st.error(
                        f"Hindsight recall failed:\n\n{e}"
                    )

                    memories = []


            # =============================================
            # MEMORY RESULTS
            # =============================================

            st.subheader(
                "🧠 Historical Memory"
            )

            if memories:

                st.success(
                    f"Found {len(memories)} relevant "
                    "historical memories."
                )

                for index, memory in enumerate(
                    memories,
                    1
                ):

                    with st.expander(
                        f"Historical Memory {index}"
                    ):

                        st.caption(
                            f"Memory Type: "
                            f"{memory['type']}"
                        )

                        st.write(
                            memory["text"]
                        )

            else:

                st.warning(
                    "No relevant historical incidents "
                    "were found."
                )


            # =============================================
            # STEP 2 — GROQ REASONING
            # =============================================

            with st.spinner(
                "🤖 Analyzing incident with historical evidence..."
            ):

                try:

                    answer = analyze_incident(
                        service=service,
                        severity=severity,
                        logs=logs,
                        memories=memories
                    )

                    st.session_state.last_analysis = answer

                except Exception as e:

                    st.error(
                        f"AI analysis failed:\n\n{e}"
                    )

                    answer = None


            # =============================================
            # AI RESULT
            # =============================================

            if answer:

                st.divider()

                st.subheader(
                    "🤖 OpsMind Recommendation"
                )

                st.markdown(
                    answer
                )

                st.success(
                    "This recommendation was generated "
                    "using historical incident memory."
                )


# =========================================================
# TEACH OPSMIND TAB
# =========================================================

with teach_tab:

    st.header(
        "🧠 Teach OpsMind"
    )

    st.caption(
        "Store a resolved production incident and "
        "post-mortem in Hindsight so future incidents "
        "can benefit from it."
    )


    # -----------------------------------------------------
    # INCIDENT ID
    # -----------------------------------------------------

    incident_id = st.text_input(
        "Incident ID",

        placeholder="INC-1821",

        key="teach_incident_id"
    )


    # -----------------------------------------------------
    # SERVICE
    # -----------------------------------------------------

    incident_service = st.text_input(
        "Service",

        value="Payment API",

        key="teach_incident_service"
    )


    # -----------------------------------------------------
    # SEVERITY
    # -----------------------------------------------------

    incident_severity = st.selectbox(
        "Incident Severity",

        [
            "SEV-1",
            "SEV-2",
            "SEV-3",
            "SEV-4"
        ],

        key="teach_incident_severity"
    )


    # -----------------------------------------------------
    # ROOT CAUSE
    # -----------------------------------------------------

    root_cause = st.text_area(
        "Root Cause",

        placeholder=(
            "Database connection pool exhaustion"
        ),

        key="teach_root_cause"
    )


    # -----------------------------------------------------
    # RESOLUTION
    # -----------------------------------------------------

    resolution = st.text_area(
        "Resolution",

        placeholder=(
            "Increased database connection pool "
            "from 50 to 100 and restarted "
            "the payment service."
        ),

        key="teach_resolution"
    )


    # -----------------------------------------------------
    # RUNBOOK
    # -----------------------------------------------------

    runbook = st.text_input(
        "Runbook",

        placeholder=(
            "payment-db-connection-pool-v2"
        ),

        key="teach_runbook"
    )


    # -----------------------------------------------------
    # OUTCOME
    # -----------------------------------------------------

    outcome = st.selectbox(
        "Outcome",

        [
            "SUCCESS",
            "PARTIAL",
            "FAILED"
        ],

        key="teach_outcome"
    )


    # -----------------------------------------------------
    # RESOLUTION TIME
    # -----------------------------------------------------

    resolution_time = st.text_input(
        "Resolution Time",

        placeholder="7 minutes",

        key="teach_resolution_time"
    )


    # -----------------------------------------------------
    # POST-MORTEM
    # -----------------------------------------------------

    post_mortem = st.text_area(
        "Post-Mortem",

        placeholder=(
            "Added database connection pool "
            "monitoring and alerts."
        ),

        key="teach_post_mortem"
    )


    # -----------------------------------------------------
    # STORE BUTTON
    # -----------------------------------------------------

    teach_button = st.button(
        "🧠 Store Incident in Memory",

        type="primary",

        use_container_width=True,

        key="teach_store_button"
    )


    # -----------------------------------------------------
    # STORE INCIDENT
    # -----------------------------------------------------

    if teach_button:

        if not incident_id.strip():

            st.warning(
                "Please enter an Incident ID."
            )

        elif not root_cause.strip():

            st.warning(
                "Please enter the root cause."
            )

        elif not resolution.strip():

            st.warning(
                "Please enter the resolution."
            )

        elif not memory_ready:

            st.error(
                "Hindsight is not connected."
            )

        else:

            with st.spinner(
                "🧠 Teaching OpsMind..."
            ):

                try:

                    remember_incident(

                        incident_id=incident_id,

                        service=incident_service,

                        severity=incident_severity,

                        root_cause=root_cause,

                        resolution=resolution,

                        runbook=runbook,

                        outcome=outcome,

                        resolution_time=resolution_time,

                        post_mortem=post_mortem
                    )


                    st.success(
                        f"🧠 OpsMind learned from "
                        f"{incident_id}."
                    )


                    st.info(
                        "This incident has been "
                        "stored in Hindsight memory."
                    )


                    st.markdown(
                        """
                        ### 🔄 Memory Learning Cycle

                        Incident Resolved
                        ↓
                        Post-Mortem
                        ↓
                        Hindsight Retain
                        ↓
                        Persistent Memory
                        ↓
                        Future Incident Recall
                        """
                    )


                except Exception as e:

                    st.error(
                        f"Failed to store incident:\n\n{e}"
                    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "OpsMind • Hindsight-powered AI Incident Response Agent"
)