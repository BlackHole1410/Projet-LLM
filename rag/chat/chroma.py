import os
import chromadb
from chromadb.config import Settings
import uuid
from ..indexing.contrat_to_dico import get_contrat_from_file
from chromadb.utils import embedding_functions

def dict_to_chroma():
    """
    Inserts documents into a Chroma collection.
    """
    chroma_client = chromadb.Client()
    documents_dir = './documents'
    files = [os.path.join(documents_dir, f) for f in os.listdir(documents_dir) if f.endswith('.html')]
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1"
    )

    collection = chroma_client.get_or_create_collection(
        name="my_collection", 
        embedding_function=sentence_transformer_ef
    )

    documents = []
    ids = []

    for i, file in enumerate(files):
        doc = get_contrat_from_file(file)
        documents.append(str(doc))
        ids.append(str(i + 1))

    collection.upsert(
        documents=documents,
        ids=ids
    )

def chroma_query(query):
    """
    Executes a query on a Chroma collection and returns the results.

    Args:
        query (str): The query text to search for.

    Returns:
        list: A list of query results.
    """
    chroma_client = chromadb.Client()
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1"
    )

    collection = chroma_client.get_or_create_collection(
        name="my_collection", 
        embedding_function=sentence_transformer_ef
    )

    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    return results
