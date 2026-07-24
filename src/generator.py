"""
Generation: take retrieved chunks + question, produce a grounded answer.
"""

import enum
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

import config
from retriever import retrieve

load_dotenv()

SYSTEM_PROMPT = """You are a telecom specifications assistant. You answer questions \
about 3GPP 5G NR specifications using ONLY the context provided to you.

Rules:
- Answer strictly from the provided context. Do not use outside knowledge.
- If the context does not contain the answer, say: "I could not find this in the \
indexed specifications." Do not guess.
- Cite the source file for each claim, e.g. [38101-1-j60_s06-06.docx].
- Preserve exact numerical values, units, and clause references from the context.
- Be concise. Technical precision matters more than fluency."""

def _extract_text(response):
    """ GEMINI may return content as a string or a list of parts. This function normalizes it to a single string. """

    if isinstance(response.content, list):
        return response.content[0]["text"]
    return response.content

def format_context(hits):
    """Turn retrieved chunks into a numbered context block for the prompt."""

    blocks = []
    for i, (doc, score) in enumerate(hits, start=1):
        source = doc.metadata.get("source_file", "unknown")
        blocks.append(f"[Context {i} from source: {source}]\n{doc.page_content}")

    return "\n\n".join(blocks)

def answer(question: str):
    """Full RAG: retrieve, then generate a grounded answer."""
    hits, in_scope = retrieve(question)

    if not in_scope:
        return{
            "answer": "I could not find this in the indexed specifications. "
                      "This question appears to be outside the scope of the "
                      "documents I have indexed.",
            "sources": [],
            "in_scope": False,
        }

    context = format_context(hits)
    user_message = f"""Context:
{context}

Question: {question}

Answer using only the context above."""

    llm = ChatGoogleGenerativeAI(
        model = "gemini-3.6-flash"
    )

    response = llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", user_message),
    ])

    answer_text = _extract_text(response)
    sources = sorted({doc.metadata.get("source_file", "unknown") for doc, _ in hits})

    return{
        "answer": answer_text,
        "sources": sources,
        "in_scope": True
    }

'''Main function for testing the answer generation.'''
if __name__ == "__main__":
    q = "What is the maximum output power for a UE in FR1?"
    result = answer(q)

    print(f"\nQ: {q}\n")
    print(result["answer"])
    print(f"\nSources: {', '.join(result['sources']) if result['sources'] else 'none'}")

