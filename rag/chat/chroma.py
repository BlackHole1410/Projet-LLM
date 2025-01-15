import chromadb
import uuid
from rag.indexing.contrat_to_dico import get_contrat
from sentence_transformers import SentenceTransformer

def Querry(query):
    chroma_client = chromadb.Client()

    # Use `get_or_create_collection` to avoid creating a new collection every time
    collection = chroma_client.get_or_create_collection(
        name="my_collection", 
        embedding_function= SentenceTransformer('HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1.5')
    )

    # List of documents
    document = get_contrat('../../documents')

    # Generate unique IDs for the documents based on the length of the documents list
    document_ids = [str(uuid.uuid4()) for _ in range(len(document))]

    # Use `upsert` to avoid adding the same documents every time
    collection.upsert(
        documents=document,
        ids=document_ids
    )
    results = collection.query(
        query_texts=query,
        n_results=1  # how many results to return
    )

    return results