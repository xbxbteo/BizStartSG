
import streamlit as st
from src.auth import require_login

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="About Us | BizStart SG",
    page_icon="🚀",
    layout="wide",
)

require_login()

# ============================================================
# 2. PAGE HEADER
# ============================================================

st.title("🚀 About BizStart SG")

st.markdown(
    """
    ### Making business setup information easier to navigate

    **BizStart SG** is an AI-powered web application developed as
    an educational prototype for the AI Bootcamp capstone project.

    It brings together selected publicly available information
    from Singapore government websites and uses
    **Retrieval-Augmented Generation (RAG)** and a
    **Large Language Model (LLM)** to help aspiring business
    owners explore the steps involved in starting a business.

    The application offers two complementary experiences:
    a personalised **Business Setup Navigator** and an interactive
    **Business Requirements Assistant**.
    """
)

st.info(
    """
    **Educational prototype only**

    BizStart SG is designed to demonstrate how generative AI
    can improve access to government information. It is not
    an official government service and must not be used for
    real-world business decisions.
    """
)

st.divider()


# ============================================================
# 3. PROBLEM STATEMENT
# ============================================================

st.header("🎯 The Problem")

st.markdown(
    """
    Aspiring business owners in Singapore may need to navigate
    information across multiple government websites to understand
    the steps involved in starting a business, including
    registration, licensing and other relevant requirements.

    For first-time business owners, it can be difficult to
    identify which information applies to their specific
    business scenario and what they should do next.

    **The opportunity:** Consolidate relevant publicly available
    government information and provide a simpler, more
    personalised way to understand the business setup process.
    """
)

st.divider()


# ============================================================
# 4. PROJECT OBJECTIVES
# ============================================================

st.header("🎯 Project Objectives")

objectives = [
    {
        "icon": "🔎",
        "title": "Simplify Information Access",
        "description": (
            "Bring selected government information into a "
            "single searchable knowledge base."
        ),
    },
    {
        "icon": "🧭",
        "title": "Personalise Business Guidance",
        "description": (
            "Use generic business details to identify "
            "potentially relevant setup steps and requirements."
        ),
    },
    {
        "icon": "💬",
        "title": "Support Interactive Questions",
        "description": (
            "Allow users to ask questions and obtain "
            "plain-language explanations from retrieved information."
        ),
    },
    {
        "icon": "📋",
        "title": "Improve Understanding",
        "description": (
            "Present information through structured checklists, "
            "explanations and references to official sources."
        ),
    },
]

left, right = st.columns(2, gap="medium")

for index, objective in enumerate(objectives):

    target_column = left if index % 2 == 0 else right

    with target_column:

        with st.container(border=True):

            st.subheader(
                f"{objective['icon']} {objective['title']}"
            )

            st.write(objective["description"])

st.divider()


# ============================================================
# 5. INTENDED USERS
# ============================================================

st.header("👥 Who Is BizStart SG For?")

st.markdown(
    """
    BizStart SG is designed primarily for people who are
    exploring business ideas in Singapore, particularly
    those who are unfamiliar with the business setup process.
    """
)

user_col1, user_col2, user_col3 = st.columns(3, gap="medium")

with user_col1:
    with st.container(border=True):
        st.subheader("🌱 First-Time Entrepreneurs")
        st.write(
            "Individuals exploring how to register and "
            "set up their first business."
        )

with user_col2:
    with st.container(border=True):
        st.subheader("🏠 Home-Based Businesses")
        st.write(
            "Individuals considering home-based activities "
            "and looking for relevant starting information."
        )

with user_col3:
    with st.container(border=True):
        st.subheader("🛒 Online and Small Businesses")
        st.write(
            "Individuals planning online shops, freelance "
            "services or other small business activities."
        )

st.caption(
    "Users should provide only generic, non-personally identifiable "
    "business information. Do not enter NRIC numbers, personal "
    "addresses, financial account details or confidential information."
)

st.divider()


# ============================================================
# 6. TWO MAIN USE CASES
# ============================================================

st.header("✨ What Can BizStart SG Do?")

st.markdown(
    """
    BizStart SG supports two main use cases. The Navigator
    helps users explore a business scenario, while the
    Assistant helps users understand specific questions.
    """
)

navigator_col, assistant_col = st.columns(2, gap="large")

with navigator_col:

    with st.container(border=True):

        st.subheader("🧭 Business Setup Navigator")

        st.caption("USE CASE 1")

        st.markdown(
            """
            **Generate a personalised starting checklist**

            Provide generic information about the business
            you intend to start, including:

            - Business activity or idea
            - Preferred business structure
            - Operating arrangement
            - Whether employees will be hired

            The Navigator analyses the scenario, retrieves
            relevant government information and generates
            a structured checklist of potentially applicable
            setup steps and requirements.

            Source references are included to help identify
            relevant official information.
            """
        )

        st.button(
            "Open Business Setup Navigator",
            key="about_open_navigator",
            width="stretch",
            type="primary",
            on_click=lambda: st.switch_page(
                "pages/3_Business_Setup_Navigator.py"
            ),
        )

with assistant_col:

    with st.container(border=True):

        st.subheader("💬 Business Requirements Assistant")

        st.caption("USE CASE 2")

        st.markdown(
            """
            **Ask questions about business requirements**

            Explore questions such as:

            - What business structures are available?
            - What should a freelancer know about tax?
            - What should I check before starting
              a home-based food business?
            - What records should a small business keep?

            The Assistant retrieves relevant information
            from the knowledge base and generates
            plain-language explanations with source references.

            You can submit additional questions within
            the same chat session. Each question currently
            triggers a separate retrieval and response.
            """
        )

        st.button(
            "Open Business Requirements Assistant",
            key="about_open_assistant",
            width="stretch",
            on_click=lambda: st.switch_page(
                "pages/4_Business_Requirements_Assistant.py"
            ),
        )

st.caption(
    "The Assistant displays chat history but does not currently "
    "pass previous messages to the LLM. Follow-up questions "
    "should therefore include enough context to stand alone."
)

st.divider()


# ============================================================
# 7. GOVERNMENT INFORMATION SOURCES
# ============================================================

st.header("🏛️ Government Information Sources")

st.markdown(
    """
    BizStart SG uses a curated knowledge base containing
    **13 source entries** from five Singapore government
    agencies and portals.

    These sources were selected to demonstrate how
    information from different government websites
    can be retrieved and presented together.
    """
)

sources = [
    {
        "agency": "ACRA",
        "full_name": (
            "Accounting and Corporate Regulatory Authority"
        ),
        "coverage": (
            "Business registration, eligibility, business "
            "structures and selected post-registration guidance."
        ),
        "url": "https://www.acra.gov.sg/",
        "count": 4,
    },
    {
        "agency": "GoBusiness",
        "full_name": "GoBusiness Singapore",
        "coverage": (
            "Official business services portal overview, "
            "including entry points to licensing and "
            "other government business services. "
            "Detailed licence-specific pages are not "
            "currently included in the knowledge base."
        ),
        "url": "https://www.gobusiness.gov.sg/",
        "count": 1,
    },
    {
        "agency": "IRAS",
        "full_name": (
            "Inland Revenue Authority of Singapore"
        ),
        "coverage": (
            "Self-employed taxation, corporate income tax, "
            "business income and record-keeping guidance."
        ),
        "url": "https://www.iras.gov.sg/",
        "count": 4,
    },
    {
        "agency": "SFA",
        "full_name": "Singapore Food Agency",
        "coverage": (
            "Selected home-based food business requirements, "
            "home-based business scheme information "
            "and food retail licensing requirements."
        ),
        "url": "https://www.sfa.gov.sg/",
        "count": 3,
    },
    {
        "agency": "MOM",
        "full_name": "Ministry of Manpower",
        "coverage": (
            "Selected employer-related information, "
            "particularly CPF contribution eligibility."
        ),
        "url": "https://www.mom.gov.sg/",
        "count": 1,
    },
]

for source in sources:

    with st.expander(
        f"{source['agency']} — {source['full_name']}"
    ):

        st.markdown(
            f"**Coverage in BizStart SG:** {source['coverage']}"
        )

        st.write(
            f"Selected source entries: {source['count']}"
        )

        st.link_button(
            f"Visit {source['agency']} Official Website",
            source["url"],
        )

st.info(
    """
    **Source coverage is selective, not exhaustive.**

    The current knowledge base contains 13 source entries
    divided into 170 text chunks for semantic retrieval.

    It does not cover all business activities, licences,
    government agencies or regulatory requirements.

    Government webpages may also change after collection.
    """
)

st.divider()


# ============================================================
# 8. HOW BIZSTART SG WORKS
# ============================================================

st.header("⚙️ How BizStart SG Works")

st.markdown(
    """
    BizStart SG uses **Retrieval-Augmented Generation (RAG)**,
    combining semantic search with an LLM.

    The system first prepares a knowledge base from selected
    government webpages. When a user submits a business
    scenario or question, it retrieves relevant text
    and provides that information to the LLM.
    """
)

st.markdown(
    """
    **The main process:**
    """
)

steps = [
    (
        "1. Collect",
        "Extract text from selected publicly accessible "
        "government webpages.",
    ),
    (
        "2. Prepare",
        "Clean and split source text into smaller chunks "
        "with source metadata.",
    ),
    (
        "3. Embed",
        "Generate vector embeddings and store them "
        "in ChromaDB.",
    ),
    (
        "4. Retrieve",
        "Use semantic similarity search to find "
        "relevant government text.",
    ),
    (
        "5. Generate",
        "Use GPT-4o-mini to create a checklist "
        "or plain-language explanation.",
    ),
    (
        "6. Present",
        "Display the response and relevant "
        "government source references.",
    ),
]

for index in range(0, len(steps), 3):

    columns = st.columns(3, gap="medium")

    for column, step in zip(
        columns,
        steps[index:index + 3],
    ):

        with column:

            with st.container(border=True):

                st.markdown(f"**{step[0]}**")
                st.write(step[1])

st.markdown(
    """
    For the Business Setup Navigator, deterministic Python
    rules also help identify potentially relevant agencies
    and permitted source IDs based on the business scenario.

    The Navigator checks generated citation IDs against
    permitted and retrieved sources. This improves source
    reference consistency but does not guarantee the
    factual accuracy of every statement.
    """
)

st.page_link(
    "pages/2_Methodology.py",
    label="View Detailed Methodology and Architecture",
    icon="🛠️",
)

st.divider()


# ============================================================
# 9. TECHNOLOGY STACK
# ============================================================

st.header("🧰 Technology Stack")

technology = [
    {
        "Component": "Application",
        "Technology": "Python and Streamlit",
        "Purpose": (
            "Business logic, interactive forms, "
            "chat interface and multipage web app"
        ),
    },
    {
        "Component": "Web Extraction",
        "Technology": "Requests and BeautifulSoup",
        "Purpose": (
            "Retrieve and extract text from "
            "selected government webpages"
        ),
    },
    {
        "Component": "Document Processing",
        "Technology": "LangChain",
        "Purpose": (
            "Split documents into chunks and "
            "integrate retrieval components"
        ),
    },
    {
        "Component": "Embeddings",
        "Technology": "text-embedding-3-small",
        "Purpose": (
            "Represent documents and queries "
            "as numerical vectors"
        ),
    },
    {
        "Component": "Vector Database",
        "Technology": "ChromaDB",
        "Purpose": (
            "Store document embeddings and "
            "support semantic similarity search"
        ),
    },
    {
        "Component": "Language Model",
        "Technology": "GPT-4o-mini",
        "Purpose": (
            "Generate checklists and "
            "plain-language explanations"
        ),
    },
]

st.dataframe(
    technology,
    width="stretch",
    hide_index=True,
)

st.divider()


# ============================================================
# 10. PROJECT SCOPE AND LIMITATIONS
# ============================================================

st.header("⚠️ Scope and Limitations")

scope_col, limitation_col = st.columns(
    2,
    gap="large",
)

with scope_col:

    st.subheader("✅ What This Prototype Demonstrates")

    st.markdown(
        """
        - Consolidating selected publicly accessible
          government information.
        - Using embeddings and semantic retrieval
          to find relevant text.
        - Generating scenario-based business
          setup checklists.
        - Providing question-and-answer assistance.
        - Presenting official source references.
        - Building an interactive multipage
          web application using Streamlit.
        """
    )

with limitation_col:

    st.subheader("🚫 What It Does Not Do")

    st.markdown(
        """
        - Provide comprehensive regulatory coverage.
        - Guarantee complete or accurate answers.
        - Automatically update government information.
        - Determine official business eligibility.
        - Submit registrations or licence applications.
        - Provide authoritative legal, financial
          or tax advice.
        - Replace government agencies or
          qualified professionals.
        """
    )

st.warning(
    """
    LLM-generated content may contain inaccuracies,
    omissions or unsupported claims. Retrieved source
    references do not guarantee that every statement
    in an answer is correct.
    """
)

st.divider()


# ============================================================
# 11. EDUCATIONAL DISCLAIMER
# ============================================================

st.header("📌 Important Notice")

st.warning(
    """
    **IMPORTANT NOTICE:** This web application is a prototype
    developed for **educational purposes only.** The information
    provided here is **NOT intended for real-world usage**
    and should not be relied upon for making any decisions,
    especially those related to financial, legal, or
    healthcare matters.

    **Furthermore, please be aware that the LLM may generate
    inaccurate or incorrect information. You assume full
    responsibility for how you use any generated output.**

    Always consult with qualified professionals for accurate
    and personalised advice.
    """
)

st.caption(
    "BizStart SG | AI Bootcamp Capstone Project | 2026"
)
