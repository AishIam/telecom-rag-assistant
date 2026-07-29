"""
Runtime retrieval: given a question, find the most relevant chunks.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import config

# Cache the vector store so it is loaded only once
_vectordb = None


def get_vectorstore():
    """Load the persisted vectorstore from disk."""

    global _vectordb

    if _vectordb is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL
        )

        _vectordb = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(config.VECTOR_DB_DIR),
        )

    return _vectordb


def retrieve(query: str, k: int = None):
    """
    Return the top-k most similar chunks with their distances.

    Lower distance = more similar.
    """

    k = k or config.TOP_K
    vectordb = get_vectorstore()

    # Returns List[(Document, distance)]
    results = vectordb.similarity_search_with_score(
        query=query,
        k=k,
    )

    if not results:
        return [], False

    # Best match distance
    best_distance = results[0][1]

    # Decide whether the question is inside the knowledge base
    in_scope = best_distance <= config.DISTANCE_THRESHOLD

    return results, in_scope


if __name__ == "__main__":

    question = "For NR band n104, what maximum output power is specified?"

    hits, in_scope = retrieve(question)

    print("\n" + "=" * 80)
    print(f"Query: {question}")
    print("=" * 80)

    for i, (doc, score) in enumerate(hits, start=1):

        print(f"\nResult {i}")
        print("-" * 60)
        print(f"Distance     : {score:.4f}")
        print(f"Source File  : {doc.metadata.get('source_file')}")
        print(f"Content Type : {doc.metadata.get('content_type')}")
        print(f"Heading      : {doc.metadata.get('heading', 'N/A')}")
        print(f"Table Index  : {doc.metadata.get('table_index', '-')}")
        print(f"Row Index    : {doc.metadata.get('row_index', '-')}")
        print()

        print(doc.page_content[:700])
        print("-" * 60)