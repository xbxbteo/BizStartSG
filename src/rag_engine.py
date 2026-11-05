
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Reuse the local database or build it from data/chunks.jsonl on Streamlit Cloud.
from src.build_vector_db import get_or_build_vector_db


# ============================================================
# 1. ENVIRONMENT AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY is missing. Configure .env locally or Streamlit Cloud secrets."
    )

VECTOR_DB_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "bizstart_sg_knowledge"

EMBEDDING_MODEL = "text-embedding-3-small"

LLM_MODEL = "gpt-4o-mini"

RETRIEVAL_K = 8


# ============================================================
# 2. INITIALISE EMBEDDINGS, VECTOR DATABASE AND LLM
# ============================================================

# On a fresh cloud instance, this creates and embeds the chunks once.
# On subsequent runs, it reuses the existing ChromaDB collection.
vector_db = get_or_build_vector_db()

llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0
)


# ============================================================
# 3. AGENCY KEYWORDS
# ============================================================

AGENCY_KEYWORDS = {

    "ACRA": [
        "register",
        "registration",
        "registered",
        "business structure",
        "sole proprietorship",
        "sole proprietor",
        "partnership",
        "limited partnership",
        "llp",
        "private limited",
        "company",
        "incorporate",
        "incorporation",
        "business name",
        "acra",
        "corppass",
        "company secretary",
        "director"
    ],

    "SFA": [
        "food",
        "bakery",
        "baker",
        "baking",
        "cake",
        "cakes",
        "pastry",
        "pastries",
        "food safety",
        "food handling",
        "food handler",
        "food shop",
        "food stall",
        "food retail",
        "licence",
        "license",
        "licensing",
        "sfa",
        "home-based",
        "home based",
        "hdb",
        "ura",
        "catering",
        "restaurant",
        "supermarket"
    ],

    "IRAS": [
        "tax",
        "taxation",
        "income",
        "income tax",
        "corporate tax",
        "gst",
        "iras",
        "record",
        "records",
        "record keeping",
        "record-keeping",
        "bookkeeping",
        "book-keeping",
        "receipt",
        "receipts",
        "expense",
        "expenses",
        "account",
        "accounts",
        "accounting",
        "revenue",
        "profit",
        "filing",
        "tax return",
        "self-employed",
        "self employed",
        "deduction",
        "deductions"
    ],

    "MOM": [
        "employee",
        "employees",
        "staff",
        "hire",
        "hiring",
        "cpf",
        "work pass",
        "foreign worker",
        "employment",
        "manpower",
        "salary",
        "wages",
        "mom",
        "contribution"
    ]
}


# ============================================================
# 4. AGENCY SEARCH HINTS
# ============================================================

AGENCY_SEARCH_HINTS = {

    "ACRA": (
        "Singapore ACRA business registration eligibility "
        "business structures sole proprietorship partnership "
        "company incorporation requirements"
    ),

    "SFA": (
        "Singapore Food Agency SFA food safety requirements "
        "home-based food business food shop licence licensing "
        "food retail bakery requirements"
    ),

    "IRAS": (
        "Singapore IRAS taxation income tax self-employed "
        "business income record keeping accounts records "
        "receipts expenses simplified record keeping"
    ),

    "MOM": (
        "Singapore Ministry of Manpower employment "
        "employees CPF contributions hiring workers "
        "work pass requirements"
    )
}


# ============================================================
# 5. IDENTIFY RELEVANT GOVERNMENT AGENCIES
# ============================================================

def identify_relevant_agencies(question):

    question_lower = question.lower()

    relevant_agencies = []

    for agency, keywords in AGENCY_KEYWORDS.items():

        for keyword in keywords:

            if keyword in question_lower:

                relevant_agencies.append(agency)
                break

    if not relevant_agencies:

        relevant_agencies = list(AGENCY_KEYWORDS.keys())

    return relevant_agencies


# ============================================================
# 6. RETRIEVE RELEVANT DOCUMENTS
# ============================================================

def retrieve_documents(question, agencies=None):

    if agencies is None:
        agencies = identify_relevant_agencies(question)

    retrieved_docs = []

    seen_documents = set()

    for agency in agencies:

        search_query = (
            question + " " + AGENCY_SEARCH_HINTS.get(agency, "")
        )

        try:

            results = vector_db.similarity_search(
                search_query,
                k=RETRIEVAL_K,
                filter={"agency": agency}
            )

            for doc in results:

                source_id = doc.metadata.get(
                    "source_id", "UNKNOWN"
                )

                chunk_index = doc.metadata.get(
                    "chunk_index", 0
                )

                document_key = (
                    source_id,
                    chunk_index,
                    doc.page_content
                )

                if document_key not in seen_documents:

                    seen_documents.add(document_key)

                    retrieved_docs.append(doc)

        except Exception as e:

            print(
                f"Retrieval error for {agency}: {e}"
            )

    return retrieved_docs


# ============================================================
# 7. PREPARE DOCUMENT CONTEXT
# ============================================================

def prepare_context(retrieved_docs):

    context_parts = []

    for index, doc in enumerate(retrieved_docs, start=1):

        metadata = doc.metadata

        source_id = metadata.get(
            "source_id", "UNKNOWN"
        )

        agency = metadata.get(
            "agency", "Unknown agency"
        )

        topic = metadata.get(
            "topic", "Unknown topic"
        )

        document_title = metadata.get(
            "document_title", "Untitled document"
        )

        url = metadata.get(
            "url", ""
        )

        context_part = f"""
DOCUMENT {index}

Source ID: {source_id}
Agency: {agency}
Topic: {topic}
Document title: {document_title}
Official URL: {url}

Retrieved content:
{doc.page_content}
"""

        context_parts.append(context_part)

    return "\n\n".join(context_parts)


# ============================================================
# 8. PREPARE RETRIEVED SOURCE LIST
# ============================================================

def prepare_sources(retrieved_docs):

    sources = []

    seen_source_ids = set()

    for doc in retrieved_docs:

        metadata = doc.metadata

        source_id = metadata.get(
            "source_id", "UNKNOWN"
        )

        if source_id in seen_source_ids:
            continue

        seen_source_ids.add(source_id)

        sources.append({
            "source_id": source_id,
            "agency": metadata.get(
                "agency", "Unknown agency"
            ),
            "topic": metadata.get(
                "topic", "Unknown topic"
            ),
            "document_title": metadata.get(
                "document_title", "Untitled document"
            ),
            "url": metadata.get(
                "url", ""
            )
        })

    return sources


# ============================================================
# 9. SYSTEM PROMPT
# ============================================================

def build_system_prompt(allowed_source_ids):

    allowed_source_ids_text = ", ".join(
        allowed_source_ids
    )

    system_prompt = f"""
You are BizStart SG, an AI assistant that helps users
understand the process of starting a business in Singapore.

You answer questions using retrieved information from
official Singapore government sources.

Your purpose is to make government information easier
for aspiring business owners to understand.

IMPORTANT: This application is an educational prototype.
It is not intended for real-world decision-making.


============================================================
A. USE THE RETRIEVED GOVERNMENT INFORMATION
============================================================

1. Base factual claims on the retrieved government documents
   provided in the user's context.

2. Do not invent laws, regulations, licences, fees,
   deadlines, eligibility conditions or requirements.

3. Do not use general knowledge to fill gaps in the
   retrieved documents.

4. If the retrieved documents do not contain enough
   information to answer a question, clearly state this.

5. Explain information in simple, plain English.

6. Focus on answering the user's actual question.


============================================================
B. SOURCE ID VALIDATION
============================================================

The ONLY source IDs you are permitted to cite are:

{allowed_source_ids_text}

Rules:

1. Never invent, guess or create a source ID.

2. Never cite a source ID that is not in the allowed list.

3. Only cite a source if its retrieved content directly
   supports the statement.

4. Do not cite a source simply because it is related
   to the general topic.

5. If a relevant source was not retrieved, do not pretend
   that you have consulted it.

6. If you cannot support a claim with the retrieved
   information, say that further verification is needed.

7. Cite sources using their exact IDs, for example:
   (Source ID: ACRA-03).


============================================================
C. BUSINESS REGISTRATION AND STRUCTURES
============================================================

1. Distinguish between business registration and
   business licensing.

2. Do not assume every business must obtain a licence.

3. Distinguish sole proprietorships, partnerships,
   limited liability partnerships and companies.

4. Do not recommend a business structure unless the
   retrieved information supports the explanation.

5. Do not assume a home-based business must operate
   as a sole proprietorship.

6. Do not assume a user's eligibility or residency status.


============================================================
D. FOOD BUSINESSES AND LICENSING
============================================================

1. Distinguish home-based food businesses from
   physical food shops.

2. Do not automatically apply food shop licensing
   requirements to home-based food businesses.

3. Do not automatically assume that every food business
   is exempt from licensing.

4. Explain home-based food business conditions only
   when supported by the retrieved SFA documents.

5. Explain food shop licensing requirements only
   when supported by the retrieved SFA documents.

6. If the retrieved information does not establish
   whether a particular business needs a licence,
   explicitly state that further verification is needed.


============================================================
E. TAX AND RECORD KEEPING
============================================================

1. Distinguish self-employed individuals from companies.

2. Do not apply corporate income tax requirements to
   a sole proprietor without explaining the distinction.

3. Use retrieved IRAS documents to explain tax and
   record-keeping requirements.

4. Do not invent tax thresholds, filing deadlines,
   exemptions or record-retention periods.

5. If a specific threshold or requirement is not
   supported by the retrieved content, do not state it.

6. Do not assume a business is GST-registered or
   non-GST-registered unless the user says so.


============================================================
F. EMPLOYMENT AND CPF
============================================================

1. Do not assume that a self-employed person has
   employees.

2. Only discuss CPF contributions where relevant
   to the user's stated employment situation.

3. Do not claim that all employment laws or obligations
   are irrelevant just because the user is self-employed.

4. If the retrieved MOM information does not cover
   a particular employment question, say so.


============================================================
G. ANSWER STRUCTURE
============================================================

1. Answer the specific question directly.

2. Do not force the answer into unrelated sections
   such as registration, tax, licensing or employment.

3. Use headings and bullet points only where useful.

4. For comparison questions, use a comparison table
   where appropriate.

5. For step-by-step questions, use numbered steps.

6. Personalise explanations using only details explicitly
   provided by the user.

7. Distinguish clearly between:
   - Requirements supported by retrieved sources
   - Suggested next steps
   - Matters requiring further verification

8. Keep answers reasonably concise and avoid repetition.

9. End with practical next steps only when relevant.
"""

    return system_prompt


# ============================================================
# 10. MAIN RAG FUNCTION
# ============================================================

def ask_bizstart(
    question,
    agencies=None,
    retrieval_query=None
):

    if not question or not question.strip():

        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    # Use a separate focused query for retrieval when provided.
    # Otherwise, use the original question.
    search_query = retrieval_query or question

    # Step 1: Identify relevant agencies.
    if agencies is None:

        agencies = identify_relevant_agencies(search_query)

    # Step 2: Retrieve relevant document chunks.
    retrieved_docs = retrieve_documents(
        search_query,
        agencies
    )

    # Step 3: Prepare source information.
    sources = prepare_sources(retrieved_docs)

    if not retrieved_docs:

        return {
            "answer": (
                "I could not find relevant information in "
                "the current government-source knowledge base. "
                "Please try rephrasing your question or consult "
                "the relevant official government website."
            ),
            "sources": []
        }

    # Step 4: Prepare the retrieved context.
    context = prepare_context(retrieved_docs)

    # Step 5: Create the allowed source ID list.
    allowed_source_ids = sorted({
        doc.metadata.get("source_id")
        for doc in retrieved_docs
        if doc.metadata.get("source_id")
    })

    # Step 6: Build the system prompt.
    system_prompt = build_system_prompt(
        allowed_source_ids
    )

    # Step 7: Build the user prompt.
    # IMPORTANT:
    # Use the original question here, not search_query.
    # The original question contains the detailed
    # Navigator instructions and business scenario.
    human_prompt = f"""
USER QUESTION AND RESPONSE INSTRUCTIONS:

{question}


RETRIEVED GOVERNMENT DOCUMENTS:

{context}


INSTRUCTIONS:

Follow the response instructions in the user's question.

Answer using the retrieved government documents above.

Focus on information relevant to the user's business scenario.

Do not introduce unrelated topics.

Cite only valid source IDs from the system prompt.

Do not invent source IDs or unsupported requirements.

If the retrieved information is insufficient,
clearly explain what is missing.

Remember that this is an educational prototype.
"""

    # Step 8: Ask the LLM.
    try:

        response = llm.invoke([
            ("system", system_prompt),
            ("human", human_prompt)
        ])

        answer = response.content

    except Exception as e:

        print(f"LLM error: {e}")

        answer = (
            "Sorry, I encountered an error while generating "
            "the answer. Please try again."
        )

    # Step 9: Return answer and retrieved sources.
    return {
        "answer": answer,
        "sources": sources
    }


# ============================================================
# 11. TERMINAL TEST AND SOURCE INVENTORY
# ============================================================

def inspect_source_inventory():

    print("\n===== VECTOR DATABASE SOURCE INVENTORY =====")

    results = vector_db.get(
        include=["metadatas"]
    )

    source_counts = {}

    for metadata in results["metadatas"]:

        source_id = metadata.get(
            "source_id", "UNKNOWN"
        )

        source_counts[source_id] = (
            source_counts.get(source_id, 0) + 1
        )

    for source_id, count in sorted(source_counts.items()):

        print(f"{source_id}: {count} chunks")

    print("\n===== END OF INVENTORY =====")


if __name__ == "__main__":

    inspect_source_inventory()

    print("\n========================================")
    print("       BIZSTART SG RAG ENGINE")
    print("========================================")

    while True:

        question = input(
            "\nEnter your question (or type 'exit'): "
        )

        if question.lower().strip() == "exit":
            break

        result = ask_bizstart(question)

        print("\nANSWER")
        print("----------------------------------------")
        print(result["answer"])

        print("\nRETRIEVED GOVERNMENT SOURCES")
        print("----------------------------------------")

        for source in result["sources"]:

            print(
                f"\n{source['source_id']} | "
                f"{source['agency']} | "
                f"{source['document_title']}"
            )

            print(source["url"])

        print("\n========================================")
