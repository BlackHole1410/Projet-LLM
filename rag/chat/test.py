import chromadb
import uuid
from sentence_transformers import SentenceTransformer


chroma_client = chromadb.Client()

# switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
collection = chroma_client.get_or_create_collection(
        name="my_collection", 
        embedding_function= SentenceTransformer('HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1.5')
    )

# List of documents
documents = [
        "This is a document about pineapple",
        "This is a document about oranges"
    ]

# Generate unique IDs for the documents based on the length of the documents list
document_ids = [str(uuid.uuid4()) for _ in range(len(documents))]

# switch `add` to `upsert` to avoid adding the same documents every time
collection.upsert(
        documents=documents,
        ids=document_ids
    )

results = collection.query(
        query_texts=["This is a query document about florida"], # Chroma will embed this for you
        n_results=1 # how many results to return
    )
print(results)
