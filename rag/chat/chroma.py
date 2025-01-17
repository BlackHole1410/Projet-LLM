import chromadb
from chromadb.utils import embedding_functions

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
