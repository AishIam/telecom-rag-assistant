"""
Evaluation benchmark for the Telecom RAG Assistant.

Indexed Corpus
--------------
- 3GPP TS 23.501
- 3GPP TS 23.502
- 3GPP TS 24.501
- 3GPP TS 29.244
- 3GPP TS 38.413
- 3GPP TS 38.101-1
- Ericsson 5G Security Whitepaper
"""

IN_SCOPE = [

# ==========================================================
# TS 23.501 (5)
# ==========================================================

{
    "question": "What is the role of the AMF in the 5G Core?",
    "must_contain": ["registration", "mobility"],
    "match_mode": "threshold:2",
},

{
    "question": "What are the responsibilities of the SMF?",
    "must_contain": ["pdu session", "upf"],
    "match_mode": "threshold:2",
},

{
    "question": "What is the function of the UPF?",
    "must_contain": ["packet", "forwarding"],
    "match_mode": "threshold:2",
},

{
    "question": "What is the purpose of the NRF?",
    "must_contain": ["network function", "discovery"],
    "match_mode": "threshold:2",
},

{
    "question": "What is a PDU Session?",
    "must_contain": ["pdu session", "connectivity"],
    "match_mode": "threshold:2",
},

# ==========================================================
# TS 23.502 (5)
# ==========================================================

{
    "question": "Explain the UE Registration procedure.",
    "must_contain": ["registration", "initial registration"],
    "match_mode": "threshold:2",
},

{
    "question": "Explain the PDU Session Establishment procedure.",
    "must_contain": ["pdu session", "establishment"],
    "match_mode": "threshold:2",
},

{
    "question": "Which network function authenticates the UE?",
    "must_contain": ["ausf"],
},

{
    "question": "What network functions participate in PDU Session Establishment?",
    "must_contain": ["ue", "smf"],
    "match_mode": "threshold:2",
},

{
    "question": "What are the different registration types in 5G?",
    "must_contain": ["initial", "mobility", "periodic"],
    "match_mode": "threshold:2",
},

# ==========================================================
# TS 24.501 (3)
# ==========================================================

{
    "question": "What is NAS in 5G?",
    "must_contain": ["non-access stratum"],
},

{
    "question": "Which protocol is used between the UE and AMF?",
    "must_contain": ["nas"],
},

{
    "question": "What is the purpose of the Registration Request message?",
    "must_contain": ["registration", "request"],
    "match_mode": "threshold:2",
},

# ==========================================================
# TS 29.244 (3)
# ==========================================================

{
    "question": "What does PFCP stand for?",
    "must_contain": ["packet forwarding control protocol"],
},

{
    "question": "Which network functions communicate using PFCP?",
    "must_contain": ["smf", "upf"],
    "match_mode": "threshold:2",
},

{
    "question": "What is the purpose of PFCP Heartbeat messages?",
    "must_contain": ["heartbeat", "alive"],
    "match_mode": "threshold:2",
},

# ==========================================================
# TS 38.413 (2)
# ==========================================================

{
    "question": "What does NGAP stand for?",
    "must_contain": ["ng application protocol"],
},

{
    "question": "Which network entities communicate using NGAP?",
    "must_contain": ["amf", "ng-ran"],
    "match_mode": "threshold:2",
},

# ==========================================================
# TS 38.101-1 (4)
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
    "question": "What does MPR stand for?",
    "must_contain": [
        "maximum power reduction",
    ],
},

{
    "question": "What is Carrier Aggregation (CA)?",
    "must_contain": [
        "aggregation",
        "component carriers",
    ],
    "match_mode": "threshold:2",
},

# ==========================================================
# Ericsson Whitepaper (3)
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

# ===========================================
# Telecom (not covered by indexed corpus)
# ===========================================

{
    "question": "Explain the Diameter protocol and its message flow."
},

{
    "question": "How does the LTE MME perform Attach procedure?"
},

{
    "question": "Explain GTPv1-U tunnel establishment in LTE."
},

{
    "question": "What is the role of the eNodeB in LTE?"
},

{
    "question": "Explain SIP call setup in IMS."
},

# ===========================================
# General knowledge
# ===========================================

{
    "question": "Explain Kubernetes Pods."
},

{
    "question": "Explain Docker containers."
},

{
    "question": "What is the capital of France?"
},

{
    "question": "Who invented Python?"
},

{
    "question": "Write a Python program to reverse a linked list."
},

]