"""
Generation: take retrieved chunks + question, produce a grounded answer.
"""

import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

import config
from retriever import retrieve
from cache import get_cached, set_cached

MODEL_NAME = "gemini-3.6-flash"
PROMPT_VERSION = "v2"   # bump this whenever you change SYSTEM_PROMPT

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


# Shared input-routing data (used by both answer() and answer_stream())
GREETINGS = {
    "hi", "hello", "hey", "yo", "hola", "namaste", "good morning",
    "good evening", "thanks", "thank you", "ok", "okay", "bye",
    "goodbye", "see you", "ciao", "salut", "bonjour", "what can you do?",
    "what is this?", "what is this", "who are you?", "who are you",
    "what is your name?", "what is your name", "help", "help me",
    "can you help me?", "can you help me", "how are you?",
    "how are you", "how's it going?", "how's it going",
    "what's up?", "what's up", "whats up?", "whats up",
}

CAPABILITY_TRIGGERS = [
    "what can i ask", "what kind of question", "what questions",
    "how can you help", "what do you do", "help me", "how does this work",
]

ROUTER_MESSAGE = (
    "👋 I'm a telecom specifications assistant. I answer questions "
    "about 3GPP 5G NR specs (TS 38.101-1) — for example: UE power "
    "classes, maximum output power, emission limits, or transmit "
    "power for a given power class. What would you like to know?"
)

OUT_OF_SCOPE_MESSAGE = (
    "I could not find this in the indexed specifications. "
    "This question appears to be outside the scope of the "
    "documents I have indexed."
)


def _is_non_question(question: str) -> bool:
    """Return True for greetings, capability questions, or trivially short input."""
    cleaned = question.strip().lower()
    is_capability_q = any(t in cleaned for t in CAPABILITY_TRIGGERS)
    return cleaned in GREETINGS or is_capability_q or len(cleaned) < 5


def _extract_text(response):
    """Safely extract text from Gemini content, which may be a string,
    a list of parts, or empty (during streaming)."""
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        if not content:                 # empty list — streaming keepalive chunk
            return ""
        part = content[0]
        if isinstance(part, dict):
            return part.get("text", "")
        if isinstance(part, str):
            return part
    return ""


def format_context(hits):
    """Turn retrieved chunks into a numbered context block for the prompt."""
    blocks = []
    for i, (doc, score) in enumerate(hits, start=1):
        source = doc.metadata.get("source_file", "unknown")
        blocks.append(f"[Context {i} from source: {source}]\n{doc.page_content}")
    return "\n\n".join(blocks)


def answer(question: str):
    """Full RAG: retrieve, then generate a grounded answer. Returns a dict."""

    # --- Input router: handle non-questions before the expensive pipeline ---
    if _is_non_question(question):
        return {
            "answer": ROUTER_MESSAGE,
            "sources": [],
            "in_scope": True,
        }

    # --- Retrieve and scope-gate ---
    hits, in_scope = retrieve(question)

    if not in_scope:
        return {
            "answer": OUT_OF_SCOPE_MESSAGE,
            "sources": [],
            "in_scope": False,
        }

    context = format_context(hits)
    user_message = f"""Context:
{context}

Question: {question}

Answer using only the context above."""

    # --- Check cache before calling the API ---
    cached = get_cached(question, MODEL_NAME, PROMPT_VERSION)
    if cached is not None:
        return cached

    llm = ChatGoogleGenerativeAI(model=MODEL_NAME)
    response = llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", user_message),
    ])

    answer_text = _extract_text(response)
    sources = sorted({doc.metadata.get("source_file", "unknown") for doc, _ in hits})

    result = {
        "answer": answer_text,
        "sources": sources,
        "in_scope": True,
    }

    set_cached(question, MODEL_NAME, PROMPT_VERSION, result)   # save for next time
    return result


def answer_stream(question: str):
    """
    Streaming version: yields the answer in pieces for the chat UI.
    Yields dicts tagged with 'type' so the UI can route tokens/final/sources.
    """
    # --- Input router ---
    if _is_non_question(question):
        yield {"type": "final", "text": ROUTER_MESSAGE, "sources": []}
        return

    # --- Retrieve and scope-gate ---
    hits, in_scope = retrieve(question)

    if not in_scope:
        yield {"type": "final", "text": OUT_OF_SCOPE_MESSAGE, "sources": []}
        return

    context = format_context(hits)
    user_message = f"""Context:
{context}

Question: {question}

Answer using only the context above."""

    llm = ChatGoogleGenerativeAI(model=MODEL_NAME)

    # Stream tokens as they arrive
    for chunk in llm.stream([
        ("system", SYSTEM_PROMPT),
        ("human", user_message),
    ]):
        text = _extract_text(chunk)
        if text:
            yield {"type": "token", "text": text}

    sources = sorted({doc.metadata.get("source_file", "unknown") for doc, _ in hits})
    yield {"type": "sources", "sources": sources}


if __name__ == "__main__":
    q = "What is the maximum output power for a UE in FR1?"
    result = answer(q)

    print(f"\nQ: {q}\n")
    print(result["answer"])
    print(f"\nSources: {', '.join(result['sources']) if result['sources'] else 'none'}")