"""
Streamlit chat UI for the Telecom RAG Assistant.
Run with: streamlit run app.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import streamlit as st
from generator import answer_stream

st.set_page_config(page_title="Telecom Spec Assistant", page_icon="📡")
st.title("📡 Telecom Spec Assistant")
st.caption(
    "Ask about 3GPP 5G NR specifications (TS 38.101-1 — FR1 UE radio requirements). "
    "Answers are grounded in the indexed documents and cite their sources."
)

with st.sidebar:
    st.header("About")
    st.markdown(
        "- **Retrieval:** semantic search over chunked 3GPP specs\n"
        "- **Scope gate:** out-of-scope questions are refused, not guessed\n"
        "- **Grounding:** answers cite source files, preserve exact values\n"
    )
    st.markdown("---")
    st.markdown("Built with LangChain · ChromaDB · MiniLM · Gemini")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(f"`{s}`" for s in msg["sources"]))

# --- Shared handler so both example buttons and chat input use the same logic ---
def handle_query(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        sources = []

        for event in answer_stream(prompt):
            if event["type"] == "token":
                full_text += event["text"]
                placeholder.markdown(full_text + "▌")
            elif event["type"] == "final":
                full_text = event["text"]
                sources = event.get("sources", [])
                placeholder.markdown(full_text)
            elif event["type"] == "sources":
                sources = event["sources"]

        placeholder.markdown(full_text)
        if sources:
            st.caption("Sources: " + ", ".join(f"`{s}`" for s in sources))

    st.session_state.messages.append({
        "role": "assistant", "content": full_text, "sources": sources
    })


# --- Example questions (only show before any conversation starts) ---
if not st.session_state.messages:
    st.markdown("**Try one of these:**")
    examples = [
        "What are the UE power classes defined in the spec?",
        "What is the maximum output power for a UE in FR1?",
        "What is the transmit power for power class 3?",
    ]
    cols = st.columns(len(examples))
    for col, ex in zip(cols, examples):
        if col.button(ex, use_container_width=True):
            handle_query(ex)
            st.rerun()
            
# Chat input (renders bar with send arrow, submits on Enter)
if prompt := st.chat_input("Ask about 5G NR specs..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        sources = []

        for event in answer_stream(prompt):
            if event["type"] == "token":
                full_text += event["text"]
                placeholder.markdown(full_text + "▌")   # cursor while streaming
            elif event["type"] == "final":
                full_text = event["text"]
                sources = event.get("sources", [])
                placeholder.markdown(full_text)
            elif event["type"] == "sources":
                sources = event["sources"]

        placeholder.markdown(full_text)  # final render without cursor
        if sources:
            st.caption("Sources: " + ", ".join(f"`{s}`" for s in sources))

    st.session_state.messages.append({
        "role": "assistant", "content": full_text, "sources": sources
    })