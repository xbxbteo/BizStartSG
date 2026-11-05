from rag_engine import retrieve_documents

question = """
I intend to provide software development, IT consulting and website
development services to clients in Singapore. I will operate independently
from my home and receive payments from clients through bank transfers.
I do not intend to hire employees initially.

I am not sure which business structure to choose.
I need to understand registration eligibility, business registration,
business structures, self-employed income tax and record keeping.
"""

documents = retrieve_documents(
    question,
    agencies=["ACRA", "IRAS"]
)

print("\n========== RETRIEVED DOCUMENTS ==========\n")

retrieved_source_ids = set()

for doc in documents:

    source_id = doc.metadata.get("source_id", "UNKNOWN")
    retrieved_source_ids.add(source_id)

    print("Source ID:", source_id)
    print("Agency:", doc.metadata.get("agency"))
    print("Title:", doc.metadata.get("document_title"))
    print("Chunk:", doc.metadata.get("chunk_index"))
    print("Content:", doc.page_content[:250])
    print("-" * 60)

print("\n========== SOURCE SUMMARY ==========\n")

for source_id in sorted(retrieved_source_ids):
    print(source_id)

print("\n========== END OF TEST ==========")