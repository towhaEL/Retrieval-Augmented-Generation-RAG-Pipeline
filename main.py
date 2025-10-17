from document_loader import loadDocuments
from rag_pipeline import Rag_Pipeline

PATH = "docs"
TOPICS = [
    "Retrieval-augmented generation",
    "Chroma (database)",
    "Quantum computing"
    ]

rag = Rag_Pipeline()
docs = loadDocuments(path=PATH, topics=TOPICS)
rag.reset()
rag.create_index(docs, chunk_size=512, chunk_overlap=64)

result = rag.query("How attention works in transformer? Explain briefly.", top_k=3)
print(result)
