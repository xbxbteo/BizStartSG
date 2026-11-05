
from rag_engine import retrieve_documents

question = """
What are the eligibility requirements for registering
a business in Singapore?

Explain who is required to register, who may be exempt,
the minimum age requirement, local residency requirements,
and any Medisave contribution requirements.
"""

documents = retrieve_documents(
    question,
    agencies=["ACRA"]
)

print("\n===== ACRA RETRIEVAL TEST =====")

for doc in documents:

    print("\nSource ID:", doc.metadata.get("source_id"))
    print("Document:", doc.metadata.get("document_title"))
    print("Chunk:", doc.metadata.get("chunk_index"))
    print("Content:")
    print(doc.page_content[:1000])
    print("-" * 70)

print("\n===== SOURCE SUMMARY =====")

source_ids = sorted({
    doc.metadata.get("source_id")
    for doc in documents
})

for source_id in source_ids:
    print(source_id)

print("\n===== END OF TEST =====")
