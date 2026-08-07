"""
Runs the evaluation benchmark and reports metrics.
Usage: python eval/run_eval.py
"""

import sys
import re
import unicodedata
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from generator import answer
from eval_questions import IN_SCOPE, OUT_OF_SCOPE

REFUSAL_MARKER = "could not find this in the indexed specifications"


def normalize_text(text: str) -> str:
    """
    Normalize text before keyword matching.
    """

    text = unicodedata.normalize("NFKC", text)

    # Replace all Unicode hyphens/dashes with a normal hyphen
    for dash in (
        "\u2010",  # Hyphen
        "\u2011",  # Non-breaking hyphen
        "\u2012",  # Figure dash
        "\u2013",  # En dash
        "\u2014",  # Em dash
        "\u2212",  # Minus sign
    ):
        text = text.replace(dash, "-")

    # Treat hyphens and spaces as equivalent
    text = text.replace("-", " ")

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.lower().strip()


def check_in_scope(item):
    """An in-scope question passes if the answer is returned AND contains all key facts."""
    result = answer(item["question"])

    if not result["in_scope"]:
        return False, "wrongly refused (false negative)"

    answer_text = normalize_text(result["answer"])

    missing = [
        kw
        for kw in item["must_contain"]
        if normalize_text(kw) not in answer_text
    ]

    if missing:
        return False, f"missing keywords: {missing}"

    return True, "correct"


def check_out_of_scope(item):
    """An out-of-scope question passes if the system refuses it."""
    result = answer(item["question"])

    answer_text = normalize_text(result["answer"])

    refused = (
        (not result["in_scope"])
        or (normalize_text(REFUSAL_MARKER) in answer_text)
    )

    if refused:
        return True, "correctly refused"

    return False, "wrongly answered (hallucination risk)"


def main():
    print("=" * 60)
    print("IN-SCOPE QUESTIONS (should be answered correctly)")
    print("=" * 60)

    in_pass = 0

    for item in IN_SCOPE:
        ok, reason = check_in_scope(item)
        in_pass += ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {item['question'][:55]:<55} | {reason}")

    print("\n" + "=" * 60)
    print("OUT-OF-SCOPE QUESTIONS (should be refused)")
    print("=" * 60)

    out_pass = 0

    for item in OUT_OF_SCOPE:
        ok, reason = check_out_of_scope(item)
        out_pass += ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {item['question'][:55]:<55} | {reason}")

    # --- Summary metrics ---
    n_in, n_out = len(IN_SCOPE), len(OUT_OF_SCOPE)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"In-scope accuracy:      {in_pass}/{n_in}  ({in_pass/n_in*100:.1f}%)")
    print(f"Out-of-scope refusal:   {out_pass}/{n_out}  ({out_pass/n_out*100:.1f}%)")
    print(
        f"Overall:                {(in_pass+out_pass)}/{n_in+n_out}  "
        f"({(in_pass+out_pass)/(n_in+n_out)*100:.1f}%)"
    )


if __name__ == "__main__":
    main()