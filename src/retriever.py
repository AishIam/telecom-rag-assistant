"""
Runtime retrieval: given a question, find the most relevant chunks.
"""

from chromadb.types import C
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from torch import embedding
from transformers import model_addition_debugger_context

import config

def get_vectorstore():
    """Load the persisted vectorstore from disk"""

    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(config.VECTOR_DB_DIR),
    )

def retrieve(query:str, k:int = None):
    """Return the top k most similar chunks with their similarity scores."""

    k = k or config.TOP_K
    vectordb = get_vectorstore()

    '''similarity_search_with_score returns a list of tuples (Document, score/distances)
    Inside the func:
    Chroma calls embeddings.embed_query(question)
    Question → vector
    Compare against stored vectors
    Rank by similarity
    Return top-k documents '''

    results = vectordb.similarity_search_with_score(query, k=k)

    if not results:
        return [], False
    best_distance = results[0][1]
    in_scope = best_distance <= config.DISTANCE_THRESHOLD

    return results, in_scope

'''Main Function for testing the retriever.'''
if __name__ == "__main__":
    question = "What is threshold and quota in URR handling?"
    hits, in_scope = retrieve(question)

    print(f"\nQuery : {question}\n")
    print(f"In scope: {in_scope}\n")

    for i, (doc, score) in enumerate(hits):
        # Lower distance = more similar
        print(f"--- Result {i} | distance={score:.4f} | {doc.metadata.get('source_file')} ---")
        # Take characters from index 0 up to (but not including) index 400.
        print(doc.page_content[:400].replace("\n", " "))
        print()