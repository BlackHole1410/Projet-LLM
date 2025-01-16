import chromadb
import uuid
from ..indexing.contrat_to_dico import get_contrat
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

def Querry(query):
    """
    Executes a query on a Chroma collection and returns the results.

    Args:
        query (str): The query text to search for.

    Returns:
        list: A list of query results.

    """
    chroma_client = chromadb.Client()
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1")

    # Use `get_or_create_collection` to avoid creating a new collection every time
    collection = chroma_client.get_or_create_collection(
        name="my_collection", 
        embedding_function= sentence_transformer_ef
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