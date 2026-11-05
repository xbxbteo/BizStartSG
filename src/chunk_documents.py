
import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed_sources.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "data" / "chunks.jsonl"


def load_documents():
    """Load extracted government webpage content from JSONL."""

    documents = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                documents.append(json.loads(line))

    return documents


def split_documents(documents):
    """Split webpage content into smaller chunks."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for document in documents:

        content = document["content"]

        text_chunks = text_splitter.split_text(content)

        for index, text_chunk in enumerate(text_chunks):

            chunk = {
                "source_id": document["source_id"],
                "agency": document["agency"],
                "topic": document["topic"],
                "document_title": document["document_title"],
                "page_title": document["page_title"],
                "url": document["url"],
                "chunk_index": index,
                "content": text_chunk
            }

            chunks.append(chunk)

    return chunks


def save_chunks(chunks):
    """Save chunks in JSON Lines format."""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")


def main():

    print("Loading extracted documents...")

    documents = load_documents()

    print(f"Documents loaded: {len(documents)}")

    print("Splitting documents into chunks...")

    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    save_chunks(chunks)

    print(f"Chunks saved to: {OUTPUT_FILE}")

    print("\nChunk count by source:")

    source_counts = {}

    for chunk in chunks:
        source_id = chunk["source_id"]
        source_counts[source_id] = source_counts.get(source_id, 0) + 1

    for source_id, count in source_counts.items():
        print(f"{source_id}: {count} chunks")

    print("\nExample chunk:")
    print(chunks[0]["content"][:500])


if __name__ == "__main__":
    main()
