import os
import chromadb
from rag.indexing.scrapping import get_contrat_from_file
from chromadb.utils import embedding_functions
import chromadb.api

def dict_to_chroma():
    """
    Converts documents from a specified directory into embeddings and stores them in a Chroma collection.
    This function initializes a Chroma client and uses a SentenceTransformer model to generate embeddings
    for HTML documents found in the './documents' directory. The embeddings are then upserted into a Chroma
    collection named "my_collection".
    Steps:
    1. Initialize a Chroma client.
    2. List all HTML files in the './documents' directory.
    3. Initialize a SentenceTransformer embedding function with a specified model.
    4. Get or create a Chroma collection with the embedding function.
    5. Read and process each HTML file to extract document content.
    6. Generate embeddings for the documents and upsert them into the Chroma collection.
    Returns:
        None
    """
    
    # Clear the system cache
    chromadb.api.client.SharedSystemClient.clear_system_cache()

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
