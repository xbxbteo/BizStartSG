
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

CHUNKS_FILE = PROJECT_DIR / "data" / "chunks.jsonl"
CHROMA_DIR = PROJECT_DIR / "chroma_db"

COLLECTION_NAME = "bizstart_sg_knowledge"
EMBEDDING_MODEL = "text-embedding-3-small"

# Load local environment variables.
# On Streamlit Cloud, OPENAI_API_KEY will be supplied
# through Streamlit secrets/environment configuration.
load_dotenv(PROJECT_DIR / ".env")


# ============================================================
# 2. LOAD PREPARED TEXT CHUNKS
# ============================================================

def load_documents():

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Missing chunks file: {CHUNKS_FILE}"
        )

    documents = []

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if not line.strip():
                continue

            record = json.loads(line)

            document = Document(
                page_content=record["content"],
                metadata={
                    "source_id": record["source_id"],
                    "agency": record["agency"],
                    "topic": record["topic"],
                    "document_title": record["document_title"],
                    "url": record["url"],
                    "chunk_index": record["chunk_index"],
                },
            )

            documents.append(document)

    if not documents:
        raise ValueError(
            "No text chunks were found in chunks.jsonl."
        )

    return documents


# ============================================================
# 3. INITIALISE EMBEDDING MODEL
# ============================================================

def get_embeddings():

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. "
            "Set it in your local .env file or "
            "Streamlit Cloud secrets."
        )

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )


# ============================================================
# 4. GET OR BUILD VECTOR DATABASE
# ============================================================

def get_or_build_vector_db():

    embeddings = get_embeddings()

    vector_db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    # If the collection already contains documents,
    # reuse the existing vector database.
    existing_count = vector_db._collection.count()

    if existing_count > 0:

        print(
            f"Reusing existing ChromaDB "
            f"({existing_count} chunks)."
        )

        return vector_db

    print(
        "ChromaDB is empty. "
        "Building knowledge base from chunks.jsonl..."
    )

    documents = load_documents()

    document_ids = [
        (
            f"{doc.metadata['source_id']}-"
            f"{doc.metadata['chunk_index']}"
        )
        for doc in documents
    ]

    # Generate embeddings and store the documents.
    vector_db.add_documents(
        documents=documents,
        ids=document_ids,
    )

    print(
        f"ChromaDB initialised with "
        f"{vector_db._collection.count()} chunks."
    )

    return vector_db


# ============================================================
# 5. TEST VECTOR DATABASE
# ============================================================

def test_vector_db(vector_db):

    print("\nTesting similarity search...")

    question = (
        "What are the steps to register "
        "a business in Singapore?"
    )

    results = vector_db.similarity_search(
        question,
        k=4,
    )

    print(f"\nQuestion: {question}")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(f"\n--- Result {index} ---")
        print(
            f"Source: {result.metadata['source_id']}"
        )
        print(
            f"Agency: {result.metadata['agency']}"
        )
        print(
            f"Content: {result.page_content[:300]}"
        )

    print("\nRetrieval test completed.")


# ============================================================
# 6. RUN DIRECTLY FOR LOCAL TESTING
# ============================================================

if __name__ == "__main__":

    print("BizStart SG - Vector Database Setup")

    vector_db = get_or_build_vector_db()

    print(
        f"Current database contains "
        f"{vector_db._collection.count()} chunks."
    )

    test_vector_db(vector_db)
