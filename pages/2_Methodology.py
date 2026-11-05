
import streamlit as st
from src.auth import require_login

# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Methodology | BizStart SG",
    page_icon="🛠️",
    layout="wide",
)

require_login()

st.title("🛠️ Methodology")

st.markdown(
    """
    This page explains how **BizStart SG** is designed and implemented,
    including its data preparation process, Retrieval-Augmented Generation
    (RAG) architecture, and the workflows supporting its two use cases.

    BizStart SG combines publicly available Singapore government information
    with semantic retrieval, deterministic Python logic, and a Large
    Language Model (LLM) to generate scenario-relevant explanations.

    The application is an **educational prototype**, not an authoritative
    government advisory service.
    """
)

st.divider()


# ============================================================
# 1. Overall system architecture
# ============================================================

st.header("1. Overall System Architecture")

st.markdown(
    """
    BizStart SG uses a **Retrieval-Augmented Generation (RAG)** architecture.

    Instead of relying only on the LLM's general knowledge, the application
    retrieves relevant text from a locally prepared knowledge base of
    government information and includes that text in the LLM prompt.

    The architecture has two main processes:

    1. **Offline knowledge base preparation:** Government webpages are
       collected, processed, divided into chunks, embedded, and stored
       in a vector database.
    2. **Online user interaction:** User inputs are processed, relevant
       information is retrieved, and an LLM generates an explanation
       or business setup checklist.
    """
)

overall_architecture = """
digraph OverallArchitecture {

    graph [
        rankdir=TB,
        bgcolor="transparent",
        pad="0.3",
        nodesep="0.35",
        ranksep="0.55",
        fontname="Arial"
    ];

    node [
        shape=box,
        style="rounded,filled",
        fontname="Arial",
        fontsize=11,
        color="#CBD5E1",
        fillcolor="#F8FAFC",
        margin="0.18,0.12"
    ];

    edge [
        color="#64748B",
        arrowsize=0.7,
        fontname="Arial",
        fontsize=9
    ];

    subgraph cluster_offline {

        label="OFFLINE: Knowledge Base Preparation";
        labelloc=t;
        fontsize=13;
        fontname="Arial";
        style="rounded";
        color="#93C5FD";

        sources [
            label="Official Government Webpages\\nACRA | GoBusiness | IRAS | MOM | SFA",
            fillcolor="#DBEAFE"
        ];

        inventory [
            label="Source Inventory\\ndata/source_inventory.csv"
        ];

        ingestion [
            label="Webpage Extraction\\nRequests + BeautifulSoup"
        ];

        preprocessing [
            label="Text Cleaning and Chunking\\n800 characters | 100 overlap"
        ];

        embeddings [
            label="Text Embeddings\\ntext-embedding-3-small"
        ];

        vector_db [
            label="ChromaDB Knowledge Base\\n170 chunks from 13 source entries",
            fillcolor="#DCFCE7"
        ];

        sources -> inventory;
        inventory -> ingestion;
        ingestion -> preprocessing;
        preprocessing -> embeddings;
        embeddings -> vector_db;
    }

    subgraph cluster_online {

        label="ONLINE: User Interaction";
        labelloc=t;
        fontsize=13;
        fontname="Arial";
        style="rounded";
        color="#86EFAC";

        user [
            label="User Input\\nBusiness Profile or Question",
            fillcolor="#DBEAFE"
        ];

        processing [
            label="Use-Case Processing\\nScenario Rules / Agency Routing"
        ];

        retrieval [
            label="Semantic Retrieval\\nRelevant Government Text Chunks"
        ];

        prompt [
            label="Prompt Construction\\nInstructions + Retrieved Context"
        ];

        llm [
            label="GPT-4o-mini\\nGenerate Response",
            fillcolor="#FEF3C7"
        ];

        output [
            label="Streamlit Output\\nChecklist or Explanation + Sources",
            fillcolor="#DCFCE7"
        ];

        user -> processing;
        processing -> retrieval;
        retrieval -> prompt;
        prompt -> llm;
        llm -> output;
    }

    vector_db -> retrieval [
        label="Search stored embeddings",
        style=dashed,
        color="#2563EB"
    ];
}
"""

st.graphviz_chart(
    overall_architecture,
    width="stretch",
)

st.info(
    """
    **Key design principle:** The knowledge base is prepared separately
    from user interaction. When a user submits a question or business
    scenario, the application searches the existing ChromaDB collection
    rather than downloading government webpages again.
    """
)

st.divider()


# ============================================================
# 2. Knowledge base preparation
# ============================================================

st.header("2. Knowledge Base Preparation")

st.markdown(
    """
    The knowledge base is constructed from selected publicly accessible
    Singapore government webpages. The preparation pipeline follows
    the RAG concepts covered in the AI Bootcamp, including document
    extraction, chunking, embeddings, and vector database storage.
    """
)

st.subheader("Step 1: Identify and Record Government Sources")

st.markdown(
    """
    Relevant government webpages are recorded in
    `data/source_inventory.csv`.

    Each source entry includes identifying information such as its
    source ID, government agency, topic, document title, and URL.

    The current prototype contains **13 source entries** from five
    government agencies or portals.
    """
)

source_table = [
    {
        "Agency / Portal": "ACRA",
        "Coverage in Prototype": (
            "Business registration, eligibility, business structures, "
            "and post-registration guidance"
        ),
    },
    {
        "Agency / Portal": "GoBusiness",
        "Coverage in Prototype": (
            "Portal overview and entry points to business services "
            "and licensing information"
        ),
    },
    {
        "Agency / Portal": "IRAS",
        "Coverage in Prototype": (
            "Self-employed taxation, corporate income tax, "
            "record keeping, and business income"
        ),
    },
    {
        "Agency / Portal": "MOM",
        "Coverage in Prototype": (
            "Selected employer-related information, including "
            "CPF contribution eligibility"
        ),
    },
    {
        "Agency / Portal": "SFA",
        "Coverage in Prototype": (
            "Home-based food business requirements, home-based "
            "business schemes, and food retail licensing"
        ),
    },
]

st.table(source_table)

st.caption(
    "Coverage is limited to the selected webpages in the source inventory. "
    "The prototype does not contain every government requirement, "
    "licence, or business activity."
)

st.subheader("Step 2: Extract Webpage Content")

st.markdown(
    """
    The script `src/ingest_sources.py` reads the source inventory
    and retrieves webpage content using:

    - **Requests** to download webpage HTML.
    - **BeautifulSoup** to extract readable text.
    - Basic HTML cleaning to remove elements such as navigation,
      scripts, headers, and footers.

    The processed records are saved in
    `data/processed_sources.jsonl`.

    Each record retains source information so that retrieved content
    can be traced back to its original webpage.
    """
)

st.subheader("Step 3: Split Content into Text Chunks")

st.markdown(
    """
    The script `src/chunk_documents.py` uses LangChain's
    `RecursiveCharacterTextSplitter`.

    The configured chunking parameters are:
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Chunk Size", "800", "characters")

with col2:
    st.metric("Chunk Overlap", "100", "characters")

with col3:
    st.metric("Stored Chunks", "170")

st.markdown(
    """
    Chunk overlap helps preserve some context between adjacent
    text segments.

    Each chunk retains metadata such as:

    - Source ID and government agency
    - Document title and topic
    - Original webpage URL
    - Chunk index

    These metadata fields support source filtering and attribution
    during retrieval.
    """
)

st.subheader("Step 4: Generate Embeddings and Build ChromaDB")

st.markdown(
    """
    The script `src/build_vector_db.py` converts text chunks into
    vector embeddings using OpenAI's `text-embedding-3-small` model.

    The resulting embeddings and document metadata are stored in
    a local **ChromaDB** collection named:

    `bizstart_sg_knowledge`

    The current knowledge base contains **170 text chunks** generated
    from the 13 selected source entries.

    During retrieval, the application compares the user's query
    embedding with stored embeddings to identify semantically
    relevant text chunks.
    """
)

st.divider()


# ============================================================
# 3. Use Case 1 - Business Setup Navigator
# ============================================================

st.header("3. Use Case 1: Business Setup Navigator")

st.markdown(
    """
    The **Business Setup Navigator** generates a scenario-relevant
    checklist based on generic information supplied by the user.

    The form collects information such as:

    - Intended business activity
    - Preferred business structure
    - Operating arrangement
    - Whether employees will be hired
    - Optional additional business details

    The workflow combines **deterministic Python scenario rules**
    with **RAG-based information retrieval** and LLM generation.
    """
)

navigator_flow = """
digraph NavigatorFlow {

    graph [
        rankdir=TB,
        bgcolor="transparent",
        pad="0.25",
        nodesep="0.3",
        ranksep="0.4"
    ];

    node [
        shape=box,
        style="rounded,filled",
        fontname="Arial",
        fontsize=11,
        color="#CBD5E1",
        fillcolor="#F8FAFC",
        margin="0.18,0.12"
    ];

    edge [
        color="#64748B",
        arrowsize=0.7
    ];

    start [
        label="User Opens\\nBusiness Setup Navigator",
        fillcolor="#DBEAFE"
    ];

    profile [
        label="Complete Business Profile Form\\nActivity | Structure | Location | Employees"
    ];

    rules [
        label="Deterministic Scenario Analysis\\nIdentify Relevant Agencies and Source IDs",
        fillcolor="#FEF3C7"
    ];

    query [
        label="Construct Focused Retrieval Query\\nBased on Business Scenario"
    ];

    retrieve [
        label="Semantic Search in ChromaDB\\nFilter by Relevant Agencies",
        fillcolor="#DCFCE7"
    ];

    context [
        label="Prepare Retrieved Context\\nand Source References"
    ];

    prompt [
        label="Build Detailed Navigator Prompt\\nScenario + Checklist Instructions + Context"
    ];

    generate [
        label="GPT-4o-mini Generates\\nScenario-Relevant Checklist",
        fillcolor="#FEF3C7"
    ];

    validate [
        label="Validate Citation Source IDs\\nAgainst Permitted and Retrieved IDs"
    ];

    output [
        label="Display Checklist and\\nReferenced Government Sources",
        fillcolor="#DCFCE7"
    ];

    start -> profile;
    profile -> rules;
    rules -> query;
    query -> retrieve;
    retrieve -> context;
    context -> prompt;
    prompt -> generate;
    generate -> validate;
    validate -> output;
}
"""

st.graphviz_chart(
    navigator_flow,
    width="stretch",
)

st.subheader("How the Navigator Works")

st.markdown(
    """
    **1. Scenario analysis**

    Python rules examine the submitted business profile and identify
    potentially relevant agencies and source IDs.

    For example, a food-related business may trigger SFA-related
    sources, while a scenario involving employees may trigger
    MOM-related information.

    **2. Focused retrieval**

    The application constructs a retrieval query based on the
    business scenario and searches ChromaDB for relevant text chunks.

    Agency filters help narrow the search. The scenario's permitted
    source IDs are also used when checking citations in the
    generated answer.

    **3. Prompt construction and generation**

    The application sends the LLM a detailed prompt containing the
    business profile, checklist-generation instructions, retrieved
    government text, and available source references.

    **4. Citation validation**

    The generated answer is checked for source ID references.
    A citation is accepted only if its ID belongs to both the
    scenario's permitted source IDs and the retrieved source IDs.

    **5. Output presentation**

    The application displays the generated checklist and the
    retrieved government sources that are cited in the answer.
    """
)

st.warning(
    """
    **Limitation:** The scenario rules are based on selected business
    characteristics and keywords. They do not constitute a complete
    regulatory decision engine.

    Citation validation checks whether referenced source IDs are
    permitted and retrieved; it does **not** independently verify
    that every generated statement is factually supported by the
    cited source.
    """
)

st.divider()


# ============================================================
# 4. Use Case 2 - Business Requirements Assistant
# ============================================================

st.header("4. Use Case 2: Business Requirements Assistant")

st.markdown(
    """
    The **Business Requirements Assistant** allows users to ask
    questions in natural language about starting and operating
    a business in Singapore, within the coverage of the prototype.

    It retrieves relevant information from the knowledge base and
    generates a plain-language explanation with source references.

    Users can submit additional questions in the same chat interface.
    """
)

assistant_flow = """
digraph AssistantFlow {

    graph [
        rankdir=TB,
        bgcolor="transparent",
        pad="0.25",
        nodesep="0.3",
        ranksep="0.4"
    ];

    node [
        shape=box,
        style="rounded,filled",
        fontname="Arial",
        fontsize=11,
        color="#CBD5E1",
        fillcolor="#F8FAFC",
        margin="0.18,0.12"
    ];

    edge [
        color="#64748B",
        arrowsize=0.7
    ];

    start [
        label="User Opens\\nBusiness Requirements Assistant",
        fillcolor="#DBEAFE"
    ];

    question [
        label="User Submits a Question\\nin Natural Language"
    ];

    routing [
        label="Keyword-Based Agency Identification\\nand Query Processing",
        fillcolor="#FEF3C7"
    ];

    retrieval [
        label="Semantic Retrieval from ChromaDB\\nRelevant Government Text Chunks",
        fillcolor="#DCFCE7"
    ];

    context [
        label="Prepare Retrieved Context\\nand Source References"
    ];

    llm [
        label="GPT-4o-mini Generates\\nPlain-Language Explanation",
        fillcolor="#FEF3C7"
    ];

    display [
        label="Display Answer and\\nRetrieved Government Sources",
        fillcolor="#DCFCE7"
    ];

    history [
        label="Save and Display Chat Messages\\nUsing Streamlit Session State"
    ];

    followup [
        label="User Submits Another Question\\nNew Retrieval for That Question",
        fillcolor="#DBEAFE"
    ];

    start -> question;
    question -> routing;
    routing -> retrieval;
    retrieval -> context;
    context -> llm;
    llm -> display;
    display -> history;
    history -> followup;
    followup -> routing [
        label="New question"
    ];
}
"""

st.graphviz_chart(
    assistant_flow,
    width="stretch",
)

st.subheader("How the Assistant Works")

st.markdown(
    """
    **1. Question submission**

    The user enters a question through Streamlit's chat interface.

    **2. Agency identification**

    The RAG engine examines the question for keywords associated
    with agencies such as ACRA, IRAS, SFA, and MOM.

    **3. Semantic retrieval**

    The application searches ChromaDB for relevant government
    information, using agency filtering where applicable.

    **4. Response generation**

    GPT-4o-mini receives the question, retrieved text chunks,
    and instructions to answer within the available evidence
    and identify relevant source references.

    **5. Chat interface**

    Streamlit's `st.session_state` stores and displays previous
    messages during the current application session.

    Users may submit another question, which triggers another
    retrieval and generation cycle.
    """
)

st.info(
    """
    **Current follow-up behaviour:** Previous chat messages are
    displayed in the interface, but the RAG engine currently receives
    only the latest submitted question.

    Therefore, the Assistant supports multiple questions within one
    session, but does not yet provide full context-aware conversational
    memory. A follow-up question should be sufficiently self-contained.
    """
)

st.divider()


# ============================================================
# 5. Technology stack
# ============================================================

st.header("5. Technology Stack")

technology_stack = [
    {
        "Component": "Python",
        "Technology": "Python 3",
        "Purpose": (
            "Application logic, data processing, scenario rules, "
            "and integration"
        ),
    },
    {
        "Component": "Web Interface",
        "Technology": "Streamlit",
        "Purpose": (
            "Multipage application, forms, chat interface, "
            "session state, and output presentation"
        ),
    },
    {
        "Component": "Web Extraction",
        "Technology": "Requests and BeautifulSoup",
        "Purpose": (
            "Download and extract text from selected government webpages"
        ),
    },
    {
        "Component": "Text Processing",
        "Technology": "LangChain",
        "Purpose": (
            "Document chunking, metadata handling, "
            "and RAG integration"
        ),
    },
    {
        "Component": "Embedding Model",
        "Technology": "text-embedding-3-small",
        "Purpose": (
            "Convert text chunks and retrieval queries "
            "into vector representations"
        ),
    },
    {
        "Component": "Vector Database",
        "Technology": "ChromaDB",
        "Purpose": (
            "Store embeddings and support semantic similarity search"
        ),
    },
    {
        "Component": "Language Model",
        "Technology": "GPT-4o-mini",
        "Purpose": (
            "Generate business setup checklists and "
            "plain-language explanations"
        ),
    },
    {
        "Component": "Flowcharts",
        "Technology": "Graphviz",
        "Purpose": (
            "Visualise the overall architecture and "
            "the two use-case workflows"
        ),
    },
]

st.table(technology_stack)

st.divider()


# ============================================================
# 6. Implementation structure
# ============================================================

st.header("6. Implementation Structure")

st.markdown(
    """
    The prototype separates its interface, knowledge-base preparation,
    and RAG logic into different Python modules.

    The main implementation files are:
    """
)

st.code(
    """
BizStartSG/
|
|-- Home.py
|
|-- pages/
|   |-- 1_About_Us.py
|   |-- 2_Methodology.py
|   |-- 3_Business_Setup_Navigator.py
|   |-- 4_Business_Requirements_Assistant.py
|
|-- src/
|   |-- ingest_sources.py
|   |-- chunk_documents.py
|   |-- build_vector_db.py
|   |-- rag_engine.py
|
|-- data/
|   |-- source_inventory.csv
|   |-- processed_sources.jsonl
|
|-- chroma_db/
|
|-- requirements.txt
|-- .env
|-- .gitignore
    """,
    language="text",
)

st.markdown(
    """
    The `src/` modules implement data ingestion, document chunking,
    vector database creation, and retrieval-based response generation.

    The `pages/` modules implement the user-facing pages, including
    the two capstone use cases.

    The local `chroma_db/` directory contains the prepared vector
    database used by the application.
    """
)

st.divider()


# ============================================================
# 7. Scope, limitations, and safeguards
# ============================================================

st.header("7. Scope, Limitations and Safeguards")

st.markdown(
    """
    **Scope**

    BizStart SG focuses on selected information relevant to
    establishing a business in Singapore, particularly registration,
    business structures, taxation, basic employer-related obligations,
    and selected food-business requirements.

    **Limitations**

    - The knowledge base covers only 13 selected government source
      entries and is not a comprehensive regulatory database.
    - Source content reflects the webpages at the time they were
      collected and is not automatically refreshed.
    - GoBusiness coverage currently consists of a portal overview
      and service entry points, rather than a complete catalogue
      of licence-specific requirements.
    - Keyword-based scenario routing may miss relevant requirements
      or select information that is not applicable.
    - Semantic retrieval may fail to retrieve all relevant evidence.
    - The LLM may generate incomplete, outdated, inaccurate, or
      unsupported statements.
    - Source ID validation does not guarantee factual accuracy.
    - The Assistant does not currently pass previous conversation
      messages to the LLM.
    - The application does not submit government applications,
      determine legal eligibility, or provide authoritative advice.

    **Safeguards**

    - Use publicly accessible government information as the
      knowledge-base input.
    - Ask for generic business scenarios rather than personal
      or sensitive information.
    - Include source references to help users identify relevant
      official webpages.
    - Restrict the application to educational demonstration use.
    - Display clear warnings about the limitations of LLM-generated
      information.
    """
)

st.divider()


# ============================================================
# 8. Educational prototype notice
# ============================================================

st.header("8. Educational Prototype Notice")

st.warning(
    """
    **IMPORTANT NOTICE:** This web application is a prototype
    developed for **educational purposes only.** The information
    provided here is **NOT intended for real-world usage** and
    should not be relied upon for making any decisions, especially
    those related to financial, legal, or healthcare matters.

    **Furthermore, please be aware that the LLM may generate
    inaccurate or incorrect information. You assume full
    responsibility for how you use any generated output.**

    Always consult with qualified professionals for accurate
    and personalised advice.
    """
)

st.caption(
    "BizStart SG | AI Bootcamp Capstone Project | "
    "Educational prototype only"
)
