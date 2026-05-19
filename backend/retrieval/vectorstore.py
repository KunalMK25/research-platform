import chromadb
import os
from retrieval.embeddings import get_embedding
from retrieval.chunker import chunk_text

persist_dir = os.getenv("CHROMA_PERSIST_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(path=persist_dir)

def get_or_create_collection(session_id: str):
    return chroma_client.get_or_create_collection(name=f"session_{session_id}")

def add_documents(session_id: str, texts: list[str], metadata: list[dict], ids: list[str]):
    collection = get_or_create_collection(session_id)
    embeddings = [get_embedding(text) for text in texts]
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadata,
        ids=ids
    )

def query_documents(session_id: str, query: str, n_results: int = 5) -> list[dict]:
    collection = get_or_create_collection(session_id)
    if collection.count() == 0:
        return []
        
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    docs = []
    for i in range(len(results['documents'][0])):
        docs.append({
            "content": results['documents'][0][i],
            "metadata": results['metadatas'][0][i]
        })
    return docs
