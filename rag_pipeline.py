import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from dotenv import load_dotenv
from document_loader import chunking

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


class Rag_Pipeline:
  def __init__(self, collection_name="rag_system_vectorstore", persist_path=".chroma"):
    self.llm_model = genai.GenerativeModel("gemini-2.5-flash")
    self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    self.chroma_client = chromadb.PersistentClient(path=persist_path, settings=Settings(anonymized_telemetry=False))
    self.collection = self.chroma_client.get_or_create_collection(name=collection_name)


  def create_index(self, documents, chunk_size=500, chunk_overlap=50):
    all_chunk = []
    all_metadata = []
    all_ids = []
    chunk_id = 0

    for document in documents:
      chunks = chunking(document['content'], chunk_size=chunk_size, chunk_overlap=chunk_overlap)

      for chunk in chunks:
        all_chunk.append(chunk)
        all_metadata.append({
            'source': document['title'],
            'chunk_id': chunk_id,
        })
        all_ids.append(f'chunk_id{chunk_id}')
        chunk_id += 1
    print(f"Chunk found {len(all_chunk)}")
    embeddings = self.embedding_model.encode(all_chunk)
    all_embeddings = [emb.tolist() for emb in embeddings]

    self.collection.upsert(
        ids = all_ids,
        embeddings = all_embeddings,
        documents = all_chunk,
        metadatas = all_metadata,
    )


  def retrieve(self, query, top_k):
    query_emb = self.embedding_model.encode([query], normalize_embeddings=True)

    result = self.collection.query(
      query_embeddings = query_emb,
      n_results = top_k,
      include=["documents","metadatas","distances"]
    )
    retrieved = []
    for i in range(len(result['ids'][0])):
      d = result['distances'][0][i]
      cos = 1.0 - float(d)
      retrieved.append({
        'chunk': result['documents'][0][i],
        'source': result['metadatas'][0][i]['source'],
        'distance': d,
        'cosine': cos,
      })
    return retrieved


  def generate_answer(self, relevant_chunks, query):
    context = "\n\n".join([f"From {r['source']}, \n{r['chunk']}" for r in relevant_chunks])
    prompt = f"""You are a helpful assistant. Answer the question using the following context and strictly follow the instructions.\n
    Question: {query}\n
    Context: {context}\n
    Instruction:\n
    1. The answer should be concise and accurate.\n
    2. Must give the answer using the context.\n
    3. If there is not enough context, simply say don't have enough information.\n
    4. Don't Hallucinate\n
    """
    try:
        # print(context)
        response = self.llm_model.generate_content(
            prompt,
        )

        return response.text, context

    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Error generating response", ""


  def query(self, query, top_k = 3):
    relevant_chunks = self.retrieve(query, top_k)
    answer, context = self.generate_answer(relevant_chunks, query)

    sources = set()
    for chunk in relevant_chunks:
      sources.add(chunk['source'])

    return {
        'question': query,
        'answer': answer,
        'source': sources,
        'context': context
    }


  def reset(self):
    name = self.collection.name
    self.chroma_client.delete_collection(name=name)
    self.collection = self.chroma_client.get_or_create_collection(name=name)