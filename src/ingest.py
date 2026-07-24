"""
Offline ingestion: load documents, chunk them, embed, and store in ChromaDB.
Run once (or whenever source documents change).
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import config

def load_documents(raw_dir:Path):
    """Load all documents from the raw dir"""
    docs = []
    for path in raw_dir.iterdir():
        if path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(path))
        elif path.suffix.lower() == ".docx":
            loader = Docx2txtLoader(str(path))
        else:
            print(f"Skipping unsupported file type: {path.name}")
            continue

        loaded = loader.load()

        #Tag every document with its source file name - needed for citations later
        for d in loaded:
            d.metadata["source_file"] = path.name #every page remebers where it came from

        docs.extend(loaded)
        print(f"[Load] {path.name} -> {len(loaded)} document(s)")

    return docs

def chunk_documents(docs):
    """ split documents into overlapping chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = config.CHUNK_SIZE,
        chunk_overlap = config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"[Chunk] {len(docs)} document(s) -> {len(chunks)} chunk(s)")
    return chunks

def build_vectorstore(chunks):
    """ embed chunks and store them in ChromaDB"""
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    vectordb = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        collection_name = config.COLLECTION_NAME,
        persist_directory = str(config.VECTOR_DB_DIR),
    )

    print(f"[STORE] Persisted {len(chunks)} chunks to {config.VECTOR_DB_DIR}")
    return vectordb

if __name__ == "__main__":
    docs = load_documents(config.RAW_DATA_DIR)
    if not docs:
        raise SystemExit("No documents found in data/raw/")
    chunks = chunk_documents(docs)
    build_vectorstore(chunks)
    print("[DONE] Ingestion Complete!")
