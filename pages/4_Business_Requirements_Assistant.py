
import streamlit as st
import sys
from pathlib import Path


# ============================================================
# 1. PROJECT CONFIGURATION AND IMPORTS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from rag_engine import ask_bizstart


st.set_page_config(
    page_title="Business Requirements Assistant | BizStart SG",
    page_icon="💬",
    layout="wide"
)


# ============================================================
# 2. PAGE HEADER
# ============================================================

st.title("💬 Business Requirements Assistant")

st.write(
    """
    Ask questions about starting a business in Singapore.
    BizStart SG searches its government-source knowledge base
    and provides plain-language explanations to help you
    understand relevant business requirements.
    """
)

st.divider()


# ============================================================
# 3. SESSION STATE INITIALISATION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_example" not in st.session_state:
    st.session_state.selected_example = None


# ============================================================
# 4. EXAMPLE QUESTIONS
# ============================================================

EXAMPLE_QUESTIONS = {
    "🏢 Business structures":
        "What is the difference between a sole proprietorship "
        "and a private limited company?",

    "💰 Tax obligations":
        "What are the tax obligations of a self-employed "
        "person in Singapore?",

    "📋 Business registration":
        "What are the steps to register a business in Singapore?",

    "🍰 Home-based food business":
        "What requirements apply to a home-based food business "
        "in Singapore?",

    "📒 Business record keeping":
        "What business records should I maintain?",

    "👥 Hiring employees":
        "What should I know about CPF contributions "
        "when hiring employees?"
}


# ============================================================
# 5. HELPER FUNCTION: BUILD RETRIEVAL QUERY
# ============================================================

def build_retrieval_query(messages, current_question):
    """
    Combine recent conversation context with the latest question.

    This helps the RAG engine retrieve relevant documents
    for follow-up questions.
    """

    recent_messages = messages[-6:]

    conversation_context = []

    for message in recent_messages:

        role = message["role"].upper()
        content = message["content"]

        conversation_context.append(
            f"{role}: {content}"
        )

    conversation_text = "\n".join(conversation_context)

    retrieval_query = f"""
PREVIOUS CONVERSATION:

{conversation_text}


LATEST USER QUESTION:

{current_question}


RETRIEVAL INSTRUCTIONS:

Retrieve official Singapore government information
relevant to the latest question.

Use the previous conversation to understand the
user's business scenario and the context of the question.

Prioritise documents that directly address the latest question.
"""

    return retrieval_query


# ============================================================
# 6. HELPER FUNCTION: BUILD ASSISTANT PROMPT
# ============================================================

def build_assistant_prompt(messages, current_question):
    """
    Prepare conversation history and response instructions
    for the LLM.
    """

    recent_messages = messages[-8:]

    conversation_context = []

    for message in recent_messages:

        role = message["role"].upper()
        content = message["content"]

        conversation_context.append(
            f"{role}:\n{content}"
        )

    conversation_text = "\n\n".join(conversation_context)

    assistant_prompt = f"""
You are BizStart SG's Business Requirements Assistant.

Your role is to help aspiring business owners understand
Singapore business setup requirements using the retrieved
government documents.

CONVERSATION HISTORY:

{conversation_text}


LATEST USER QUESTION:

{current_question}


RESPONSE INSTRUCTIONS:

1. Answer the latest question directly.

2. Use the conversation history to understand the user's
   business activity, business structure and operating
   arrangements where relevant.

3. Do not ask the user to repeat information already
   provided in the conversation.

4. Explain government requirements in simple,
   plain English.

5. Use headings, bullet points and tables where they
   improve readability.

6. Distinguish between mandatory requirements,
   recommendations and matters requiring further verification.

7. Cite supporting information using only the exact
   source IDs provided in the system instructions.

8. Never invent source IDs, government requirements,
   fees, deadlines or licence conditions.

9. If the retrieved documents do not contain enough
   information, clearly explain the limitation.

10. Do not present assumptions as confirmed requirements.

11. Keep the answer relevant to the user's latest question.

12. Where appropriate, suggest a useful follow-up question
    that helps the user understand the next step.

IMPORTANT:

This application is an educational prototype.
Do not present the response as professional legal,
financial or regulatory advice.
"""

    return assistant_prompt


# ============================================================
# 7. HELPER FUNCTION: DISPLAY GOVERNMENT SOURCES
# ============================================================

def display_sources(sources):
    """
    Display retrieved government documents and their
    official source links.
    """

    if not sources:
        st.caption("No government sources were returned.")
        return

    with st.expander(
        f"📚 View government sources ({len(sources)})",
        expanded=False
    ):

        for index, source in enumerate(sources):

            agency = source.get("agency", "Unknown agency")
            title = source.get(
                "document_title",
                "Untitled government document"
            )
            source_id = source.get("source_id", "Unknown")
            topic = source.get("topic", "Not specified")
            url = source.get("url", "")

            st.markdown(
                f"**{agency} — {title}**"
            )

            st.caption(
                f"Source ID: {source_id} | Topic: {topic}"
            )

            if url:
                st.markdown(
                    f"[Open official government source ↗]({url})"
                )

            if index < len(sources) - 1:
                st.divider()


# ============================================================
# 8. SIDEBAR: ASSISTANT INFORMATION AND CONTROLS
# ============================================================

with st.sidebar:

    st.subheader("About this assistant")

    st.write(
        """
        BizStart SG helps you explore information about
        starting and operating a business in Singapore.
        """
    )

    st.markdown("**Topics you can ask about:**")

    st.markdown(
        """
        - Business registration
        - Choosing a business structure
        - Tax obligations
        - Business record keeping
        - Food business requirements
        - Employment and CPF matters
        """
    )

    st.divider()

    st.subheader("Conversation")

    st.caption(
        "Start a new conversation if you want to explore "
        "a different business scenario."
    )

    if st.button(
        "🗑️ Clear conversation",
        width="stretch",
        disabled=not st.session_state.messages
    ):

        st.session_state.messages = []
        st.session_state.selected_example = None

        st.rerun()


# ============================================================
# 9. WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown("### 👋 Welcome! How can I help you?")

    st.write(
        """
        Whether you are exploring a business idea or preparing
        to register your business, you can ask questions about
        the requirements involved.
        """
    )

    st.info(
        """
        **Getting started**

        Select one of the example questions below, or type
        your own question in the message box at the bottom
        of the page.
        """
    )

    st.markdown("#### 💡 Explore common business questions")

    question_items = list(EXAMPLE_QUESTIONS.items())

    for row_start in range(0, len(question_items), 2):

        col1, col2 = st.columns(2)

        for column, item_index in zip(
            [col1, col2],
            [row_start, row_start + 1]
        ):

            if item_index < len(question_items):

                label, example_question = question_items[item_index]

                with column:

                    if st.button(
                        label,
                        key=f"example_{item_index}",
                        width="stretch"
                    ):

                        st.session_state.selected_example = (
                            example_question
                        )

                        st.rerun()

else:

    st.caption(
        "💬 Continue your conversation below. "
        "You can ask follow-up questions using your earlier context."
    )


# ============================================================
# 10. DISPLAY EXISTING CONVERSATION
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            display_sources(
                message.get("sources", [])
            )


# ============================================================
# 11. CHAT INPUT
# ============================================================

question = st.chat_input(
    "👇 Type your business setup question here..."
)

# Use a selected example question if the user clicked a button.
if st.session_state.selected_example:

    question = st.session_state.selected_example

    st.session_state.selected_example = None


# ============================================================
# 12. PROCESS USER QUESTION
# ============================================================

if question:

    # Preserve previous conversation before adding the new question.
    previous_messages = st.session_state.messages.copy()

    # Display and save the user's question.
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Build separate prompts for retrieval and answer generation.
    retrieval_query = build_retrieval_query(
        previous_messages,
        question
    )

    assistant_prompt = build_assistant_prompt(
        previous_messages,
        question
    )

    # Generate the response using the existing RAG engine.
    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Searching government information and preparing your answer..."
        ):

            try:

                result = ask_bizstart(
                    question=assistant_prompt,
                    retrieval_query=retrieval_query
                )

                answer = result.get(
                    "answer",
                    "Sorry, I could not generate an answer."
                )

                sources = result.get("sources", [])

            except Exception as error:

                # Keep technical details in the terminal.
                print(
                    f"Business Requirements Assistant error: {error}"
                )

                answer = (
                    "Sorry, something went wrong while retrieving "
                    "government information. Please try again."
                )

                sources = []

        # Display the answer.
        st.markdown(answer)

        # Display retrieved government documents.
        display_sources(sources)

    # Save the assistant response and its sources together.
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })


# ============================================================
# 13. EDUCATIONAL DISCLAIMER
# ============================================================

st.divider()

st.caption(
    """
    Educational prototype only. Information may be incomplete
    or inaccurate. Always consult official government sources
    and qualified professionals for real-world decisions.
    """
)
