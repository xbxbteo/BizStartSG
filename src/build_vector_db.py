
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


# --------------------------------------------------
# 1. Set up paths and load environment variables
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

CHUNKS_FILE = PROJECT_DIR / "data" / "chunks.jsonl"
CHROMA_DIR = PROJECT_DIR / "chroma_db"

load_dotenv(PROJECT_DIR / ".env")


# --------------------------------------------------
# 2. Check that the input file exists
# --------------------------------------------------

if not CHUNKS_FILE.exists():
    raise FileNotFoundError(
        f"Could not find the chunks file: {CHUNKS_FILE}"
    )


# --------------------------------------------------
# 3. Load the 93 text chunks
# --------------------------------------------------

print("Loading text chunks...")

documents = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
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

print(f"Loaded {len(documents)} chunks.")


# --------------------------------------------------
# 4. Initialise the OpenAI embedding model
# --------------------------------------------------

print("\nInitialising OpenAI embedding model...")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# --------------------------------------------------
# 5. Create the ChromaDB vector database
# --------------------------------------------------

print("\nGenerating embeddings and building ChromaDB...")

vector_db = Chroma(
    collection_name="bizstart_sg_knowledge",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)

document_ids = [
    f"{doc.metadata['source_id']}-{doc.metadata['chunk_index']}"
    for doc in documents
]

vector_db.add_documents(
    documents=documents,
    ids=document_ids,
)

print("\nVector database created successfully!")
print(f"Database location: {CHROMA_DIR}")


# --------------------------------------------------
# 6. Test a similarity search
# --------------------------------------------------

print("\nTesting similarity search...")

test_question = (
    "What are the steps to register a business in Singapore?"
)

results = vector_db.similarity_search(
    test_question,
    k=4,
)

print(f"\nQuestion: {test_question}")
print("\nTop 4 retrieved results:")

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print(f"Source: {result.metadata['source_id']}")
    print(f"Agency: {result.metadata['agency']}")
    print(f"Topic: {result.metadata['topic']}")
    print(f"Content: {result.page_content[:500]}")

print("\nRetrieval test completed.")