import chromadb
import uuid
from indexing.embedding import embeddings
from indexing.contrat_text import doc

chroma_client = chromadb.Client()

# switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
collection = chroma_client.create_collection(
name="my_collection", 
embedding_function=embeddings)

# List of documents
documents = doc

# Generate unique IDs for the documents based on the length of the documents list
document_ids = [str(uuid.uuid4()) for _ in range(len(documents))]

# switch `add` to `upsert` to avoid adding the same documents every time
collection.upsert(
        documents=documents,
        ds=document_ids
    )

def chroma(query):
    results = collection.query(
        query_texts=query,
        n_results=1 # how many results to return
    )

    return results