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
    """Full RAG: retrieve, then generate a grounded answer."""

    # --- Input router: handle non-questions before the expensive pipeline ---
    cleaned = question.strip().lower()
    greetings = {"hi", "hello", "hey", "yo", "hola", "namaste", "good morning",
                 "good evening", "thanks", "thank you", "ok", "okay", "bye", 
                 "goodbye", "see you", "ciao", "salut", "bonjour", "what can you do?", 
                 "what is this?", "what is this", "who are you?", "who are you", 
                 "what is your name?", "what is your name", "help", "help me", 
                 "can you help me?", "can you help me", "how are you?", 
                 "how are you", "how's it going?", "how's it going", 
                 "what's up?", "what's up", "whats up?", "whats up"}

    capability_triggers = ["what can i ask", "what kind of question",
                           "what questions", "how can you help", "what do you do",
                           "help me", "how does this work"]

    is_capability_q = any(t in cleaned for t in capability_triggers)

    if cleaned in greetings or is_capability_q or len(cleaned) < 5:
        yield {"type": "final",
               "text": "👋 I'm a telecom specifications assistant. I answer questions "
                       "about 3GPP 5G NR specs (TS 38.101-1) — for example: UE power "
                       "classes, maximum output power, emission limits, or transmit "
                       "power for a given power class. What would you like to know?",
               "sources": []}
        return

    # --- Normal RAG pipeline below ---
    hits, in_scope = retrieve(question)

    if not in_scope:
        yield {
            "type": "final",
            "text": "I could not find this in the indexed specifications. "
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

def answer_stream(question: str):
    """
    Generator version: yields the answer in pieces for streaming UIs.
    Yields dicts so the UI knows about scope/sources too.
    """
    cleaned = question.strip().lower()
    greetings = {"hi", "hello", "hey", "yo", "hola", "namaste", "good morning",
                 "good evening", "thanks", "thank you", "ok", "okay", "bye", 
                 "goodbye", "see you", "ciao", "salut", "bonjour", "what can you do?", 
                 "what is this?", "what is this", "who are you?", "who are you", 
                 "what is your name?", "what is your name", "help", "help me", 
                 "can you help me?", "can you help me", "how are you?", 
                 "how are you", "how's it going?", "how's it going", 
                 "what's up?", "what's up", "whats up?", "whats up"}

    capability_triggers = ["what can i ask", "what kind of question",
                               "what questions", "how can you help", "what do you do",
                               "help me", "how does this work"]
    
    is_capability_q = any(t in cleaned for t in capability_triggers)
    
    if cleaned in greetings or is_capability_q or len(cleaned) < 5:
        yield {"type": "final",
                   "text": "👋 I'm a telecom specifications assistant. I answer questions "
                           "about 3GPP 5G NR specs (TS 38.101-1) — for example: UE power "
                           "classes, maximum output power, emission limits, or transmit "
                           "power for a given power class. What would you like to know?",
                "sources": []}
        return
    
    # --- Normal RAG pipeline below ---
    hits, in_scope = retrieve(question)
    
    if not in_scope:
        yield {"type": "final",
               "text": "I could not find this in the indexed specifications. "
                       "This question appears to be outside the scope of the "
                       "documents I have indexed.",
               "sources": []}
        return

    context = format_context(hits)
    user_message = f"""Context:
{context}

Question: {question}

Answer using only the context above."""

    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

    # Stream tokens as they arrive
    for chunk in llm.stream([
        ("system", SYSTEM_PROMPT),
        ("human", user_message),
    ]):
        text = _extract_text(chunk)
        if text:
            yield {"type": "token", "text": text}

    sources = sorted({doc.metadata.get("source_file") for doc, _ in hits})
    yield {"type": "sources", "sources": sources}


'''Main function for testing the answer generation.'''
if __name__ == "__main__":
    q = "What is the maximum output power for a UE in FR1?"
    result = answer(q)

    print(f"\nQ: {q}\n")
    print(result["answer"])
    print(f"\nSources: {', '.join(result['sources']) if result['sources'] else 'none'}")

