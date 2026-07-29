"""
Evaluation benchmark for the Telecom RAG Assistant.

IN_SCOPE:
Questions that should be answerable from the indexed corpus
(3GPP TS 38.101-1 + Ericsson 5G Security Whitepaper).

OUT_OF_SCOPE:
Questions that should be rejected.
"""

IN_SCOPE = [

    # ==========================================================
    # 3GPP TS 38.101-1
    # ==========================================================

    {
        "question": "What are the UE power classes defined in the specification?",
        "must_contain": [
            "power class 1",
            "power class 1.5",
            "power class 2",
            "power class 3",
        ],
        "match_mode": "threshold:3",
    },

    {
        "question": "Which power class is the default for an NR UE?",
        "must_contain": [
            "power class 3",
        ],
    },

    {
        "question": "What is the nominal maximum output power for Power Class 1?",
        "must_contain": [
            "29",
        ],
        "word_boundary": True,
    },

    {
        "question": "What is the nominal maximum output power for Power Class 2?",
        "must_contain": [
            "26",
        ],
        "word_boundary": True,
    },

    {
        "question": "What is the nominal maximum output power for Power Class 3?",
        "must_contain": [
            "23",
        ],
        "word_boundary": True,
    },

    {
        "question": "For NR band n104, what maximum output power is specified?",
        "must_contain": [
            "n104",
            "26",
        ],
        "match_mode": "threshold:2",
    },

    {
        "question": "Which NR bands support Power Class 2?",
        "must_contain": [
            "power class 2",
        ],
    },

    {
        "question": "What does MPR stand for?",
        "must_contain": [
            "maximum power reduction",
        ],
    },

    {
        "question": "Which clause specifies transmitter characteristics?",
        "must_contain": [
            "clause 6",
        ],
        "match_mode": "any",
    },

    {
        "question": "Which clause specifies receiver characteristics?",
        "must_contain": [
            "clause 7",
        ],
        "match_mode": "any",
    },

    {
        "question": "What is Carrier Aggregation (CA)?",
        "must_contain": [
            "aggregation",
            "component carriers",
        ],
        "match_mode": "threshold:2",
    },

    {
        "question": "What is Dual Connectivity (DC)?",
        "must_contain": [
            "dual connectivity",
        ],
    },

    {
        "question": "What is Supplemental Uplink (SUL)?",
        "must_contain": [
            "supplemental uplink",
        ],
    },

    {
        "question": "Which modulation schemes are included in the reference measurement channels?",
        "must_contain": [
            "qpsk",
            "256qam",
        ],
        "match_mode": "threshold:2",
    },

    # ==========================================================
    # Ericsson 5G Security Whitepaper
    # ==========================================================

    {
        "question": "What are the five properties of a trustworthy 5G system?",
        "must_contain": [
            "resilience",
            "communication security",
            "identity management",
            "privacy",
            "security assurance",
        ],
        "match_mode": "threshold:4",
    },

    {
        "question": "How does the 5G system protect subscriber identities?",
        "must_contain": [
            "elliptic curve",
            "conceal",
        ],
        "match_mode": "threshold:2",
    },

    {
        "question": "Why are IMSI catchers ineffective in a 5G-only system?",
        "must_contain": [
            "temporary",
            "public key",
        ],
        "match_mode": "threshold:2",
    },

]


OUT_OF_SCOPE = [

    # ==========================================================
    # Telecom concepts NOT covered by the indexed corpus
    # ==========================================================

    {
        "question": "Explain PFCP Session Establishment Request."
    },

    {
        "question": "How does the AMF perform UE registration?"
    },

    {
        "question": "Explain the RRC Setup procedure."
    },

    {
        "question": "How does MAC scheduling work in NR?"
    },

    {
        "question": "Explain QoS Flow Identifier (QFI)."
    },

    {
        "question": "How does the SMF select a UPF?"
    },

    {
        "question": "Explain NGAP Initial Context Setup."
    },

    {
        "question": "Explain URR threshold and quota handling."
    },

    # ==========================================================
    # General knowledge
    # ==========================================================

    {
        "question": "What is the capital of France?"
    },

    {
        "question": "Who invented Python?"
    },

    {
        "question": "Explain photosynthesis."
    },

    {
        "question": "Who won the FIFA World Cup in 2022?"
    },

    {
        "question": "Write a Python program to reverse a linked list."
    },

]