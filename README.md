# telecom-rag-assistant
A chatbot that answers questions over 4G/5G technical documentation (3GPP specs)
# 📡 Telecom Spec Assistant — RAG over 3GPP 5G NR Specifications

A Retrieval-Augmented Generation (RAG) system that answers technical questions about
3GPP 5G New Radio specifications, grounded strictly in the indexed documents and with
source citations. Built to explore production RAG concerns — retrieval quality,
grounding, scope control, evaluation, and cost — not just a demo that "chats with a PDF."

## What it does

Ask a question about 5G NR UE radio requirements (e.g. *"What are the UE power classes?"*)
and the assistant retrieves the most relevant passages from the indexed 3GPP spec,
then generates an answer **using only that retrieved context**, citing the source file.
Questions outside the indexed corpus are **refused rather than answered**, to avoid
hallucination.

## Indexed corpus

- **3GPP TS 38.101-1** — NR User Equipment radio transmission and reception (FR1)
- **Ericsson 5G Security Whitepaper** — trustworthy-5G properties, authentication, encryption

## Architecture

```
Ingestion (offline, run once)
  PDF / DOCX  ->  text + structure-aware table extraction
              ->  chunking (overlapping)
              ->  embeddings (all-MiniLM-L6-v2, local)
              ->  ChromaDB (persisted)

Query (runtime)
  question  ->  input router (greetings / capability / spec question)
            ->  embed query  ->  similarity search (top-k)
            ->  scope gate (distance threshold)
            ->  grounded generation (LLM, context-only, cited)
            ->  answer + sources
```

The ingestion and query paths are deliberately separated: ingestion is slow and runs
offline as a batch job, while queries must be fast. This mirrors how a production RAG
service is structured.

## Key engineering decisions

**Structure-aware table extraction.** 3GPP specs are table-dense, and naive `.docx`
text extraction flattens tables into unreadable number-soup, breaking retrieval of
values like power limits. Tables are extracted separately with `python-docx`, with
column headers attached to each row (`Class 2 (dBm): 26`) so values stay self-describing
and retrievable. Two-row/merged headers are handled.

**Scope gating to prevent hallucination.** A distance threshold on the top retrieval
result decides whether a question is in-scope. Out-of-scope questions are refused before
the LLM is called. The generation prompt additionally instructs the model to answer only
from context and say "I could not find this" otherwise. Two independent layers of
hallucination defense.

**Grounded, cited answers.** Every answer cites its source file and preserves exact
numerical values and clause references from the spec, so claims are auditable.

**Evaluation harness.** A labeled benchmark (in-scope questions with expected key facts,
plus out-of-scope questions that must be refused) measures the system rather than relying
on spot checks. Reports in-scope accuracy and out-of-scope refusal rate.

**Answer caching.** Answers are cached on disk keyed on `question + model + prompt version`,
so repeated eval runs don't re-hit the API and the cache invalidates correctly when the
pipeline changes.

**Input routing.** Greetings and "what can I ask" style inputs are handled before the
expensive retrieval+LLM pipeline, saving latency and cost.

**Streaming chat UI.** A Streamlit chat interface streams tokens as they arrive so the
answer feels responsive despite multi-second LLM latency.

## Results

| Metric | Result |
|---|---|
| Out-of-scope refusal rate | **100%** (never fabricates answers outside the corpus) |
| In-scope retrieval | Reliably surfaces relevant passages into context |
| In-scope keyword-match accuracy | ~40–60% (understated — see Limitations) |

The **100% refusal rate is the headline result**: across every run, the system correctly
refuses telecom-adjacent questions from *other* specs (PFCP, RRC, AMF, MAC scheduling)
as well as unrelated questions — it does not hallucinate.

## Known limitations (and how a production system would address them)

**Keyword-based evaluation understates accuracy.** The eval scores answers by checking
for expected keywords. Because the LLM's answer *phrasing* varies between runs, correct
answers worded differently (e.g. "PC3" vs "power class 3") are sometimes scored as
failures — so the reported in-scope accuracy is a lower bound, not the true quality.
The production fix is **LLM-as-judge** evaluation, where a model grades semantic
correctness rather than exact keyword presence, making the metric robust to phrasing.

**Table-value retrieval ranking.** Structure-aware extraction puts spec values correctly
into the vector store and into the retrieval window, but a general-purpose embedding model
(`all-MiniLM-L6-v2`) ranks natural-language prose above terse numeric table rows for some
queries. The production fix is a **cross-encoder reranker** or a **domain-tuned embedding
model**.

**Distance threshold is hand-tuned.** The scope-gate threshold was set from observed
in-scope vs out-of-scope distance distributions. A rigorous approach sweeps the threshold
against the labeled eval set to trade off false refusals vs false answers explicitly.

**Merged/multi-level table headers.** `python-docx` duplicates merged-cell header text
across columns, adding some noise (data values remain intact). Per-table schema handling
would clean this up.

## Tech stack

LangChain · ChromaDB · sentence-transformers (all-MiniLM-L6-v2) · python-docx · Streamlit ·
Gemini (swappable LLM via LangChain)

## Running locally

```bash
pip install -r requirements.txt

# add your LLM API key
echo "GOOGLE_API_KEY=your_key" > .env

# put spec documents in data/raw/, then ingest (offline, one-time)
python src/ingest.py

# run the chat UI
streamlit run app.py

# run the evaluation benchmark
python eval/run_eval.py
```

## Project structure

```
src/
  ingest.py       # load, extract tables, chunk, embed, store
  retriever.py    # query -> embed -> similarity search -> scope gate
  generator.py    # context + question -> grounded, cited answer (+ streaming)
  cache.py        # disk answer cache
  config.py       # all tunable settings
eval/
  eval_questions.py  # labeled benchmark
  run_eval.py        # harness + metrics
app.py            # Streamlit chat UI
```

---

*Built as a hands-on exploration of production RAG concerns: retrieval quality, grounding,
scope control, evaluation methodology, and cost management.*