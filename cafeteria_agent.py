"""
Smart Cafeteria Rating System — Agentic Layer (PA3)
====================================================
A small autonomous agent that EVOLVES THE FUZZY SOLUTION ITSELF.

It does NOT touch FCM. FCM stays the data-driven baseline that sets the initial
membership functions. The agent acts on the FIS side: it senses a flaw in those
membership functions, adjusts them within safe bounds, and verifies the fix —
reverting if anything gets worse.

Loop:  SENSE  ->  REASON  ->  ACT  ->  REFLECT

This file IMPORTS the existing pipeline and never modifies it. If you delete this
file, the core system still runs exactly as before.
"""

import copy
import re
from cafeteria_frontend import (
    load_lexicon, build_analyzer, load_reviews_csv, score_dataframe, ASPECTS,
)
from cafeteria_fcm import learn_membership_functions, cafeteria_vectors
from cafeteria_fis import build_fis, rate, label

LEX = "Variable_and_keywords_refined.xlsx"
CSV = "reviews_clean.csv"

# ---------------------------------------------------------------------------
# LLM (llama3.2:3b via Ollama) — powers the REASON step and the RECOMMENDATIONS.
# It is ONE swappable function: change `llm_call` to use an API / Gemini / n8n
# later without touching the rest of the agent. Every LLM use has a rule-based
# FALLBACK, so the demo never breaks if Ollama is off or returns junk.
# ---------------------------------------------------------------------------
def llm_call(prompt):
    import ollama
    resp = ollama.chat(model="llama3.2:3b",
                       messages=[{"role": "user", "content": prompt}],
                       options={"temperature": 0.0})        # reproducible
    return resp["message"]["content"].strip()

# The agent may shift a skewed aspect's Low/Medium peaks DOWN by at most this much.
# Bounded = safe: the agent can correct a skew but can't wildly rewrite the scale.
MAX_SHIFT = 0.20
TRY_SHIFTS = [0.05, 0.10, 0.15, 0.20]
MEDIUM_BAND = (2.5, 3.5)     # an "average" cafeteria should land here


# ---------- helper: rate everything for a given set of membership functions ----------
def evaluate(mfs, vectors):
    system, ants = build_fis(mfs)
    sanity = {
        "all average":   rate({a: 0.5 for a in ASPECTS}, system, ants),
        "all excellent": rate({a: 0.9 for a in ASPECTS}, system, ants),
        "bad food":      rate({"Food Quality": 0.1, "Cleanliness": 0.8,
                               "Menu Variety": 0.8, "Service Speed": 0.8}, system, ants),
    }
    ratings = {caf: rate(vec, system, ants) for caf, vec in vectors.items()}
    return sanity, ratings


# ---------- SENSE: is there a problem, and which aspect causes it? ----------
def sense(mfs, sanity):
    avg = sanity["all average"]
    problem = avg < MEDIUM_BAND[0]          # an average cafeteria is rated Low -> wrong
    return problem, avg


# ---------- REASON: ask the LLM which aspect is the culprit (rule fallback) ----------
def reason_rule_based(mfs):
    """Fallback: the culprit is the aspect whose Low centre sits highest."""
    return max(ASPECTS, key=lambda a: mfs[a]["peaks"][0])


def reason_llm(mfs):
    """Ask llama3.2 to diagnose which aspect causes 'average -> Low'.
    Falls back to the rule if the model is unavailable or unparseable."""
    lines = [f"- {a}: Low/Medium/High centres = {[round(float(x),3) for x in mfs[a]['peaks']]}"
             for a in ASPECTS]
    prompt = (
        "A fuzzy rating system rates an 'all-average' cafeteria (every score 0.5) as "
        "LOW, which is wrong — it should be Medium. This happens because one aspect's "
        "LOW membership-function centre sits too high, so 0.5 is misread as Low.\n\n"
        "Here are the four aspects and their Low/Medium/High centres:\n"
        + "\n".join(lines) +
        "\n\nWhich ONE aspect is most likely the culprit (the one whose Low centre is "
        "highest, closest to or above 0.5)? Reply with ONLY the exact aspect name from "
        "this list: Food Quality, Cleanliness, Menu Variety, Service Speed."
    )
    try:
        out = llm_call(prompt)
        for a in ASPECTS:                      # match the model's answer to a valid aspect
            if a.lower() in out.lower():
                return a, "LLM"
    except Exception:
        pass
    return reason_rule_based(mfs), "rule-based fallback"


# ---------- ACT: shift the culprit aspect's Low/Medium peaks DOWN by `shift` ----------
def act(mfs, aspect, shift):
    new = copy.deepcopy(mfs)
    c0, c1, c2 = (float(x) for x in new[aspect]["peaks"])
    nc0 = max(0.05, c0 - shift)             # pull Low centre down (bounded)
    nc1 = max(nc0 + 0.05, c1 - shift)       # pull Medium centre down, keep order
    new[aspect]["peaks"] = [round(nc0, 3), round(nc1, 3), round(c2, 3)]
    new[aspect]["Low"]    = (0.0, nc0, nc1)
    new[aspect]["Medium"] = (nc0, nc1, c2)
    new[aspect]["High"]   = (nc1, c2, 1.0)
    return new


# ---------- REFLECT: keep the smallest fix that works AND keeps sanity intact ----------
def reflect(baseline_mfs, aspect, vectors, base_sanity):
    for shift in TRY_SHIFTS:
        trial = act(baseline_mfs, aspect, shift)
        sanity, _ = evaluate(trial, vectors)
        avg_ok    = MEDIUM_BAND[0] <= sanity["all average"] < MEDIUM_BAND[1]
        veto_ok   = sanity["bad food"] < 2.5            # bad food still Low
        excel_ok  = sanity["all excellent"] >= 3.5      # excellent still High
        if avg_ok and veto_ok and excel_ok:
            return trial, shift, sanity                 # accept this fix
    return None, None, None                             # no safe fix -> revert


# ---------- external output: a recommendation per cafeteria ----------
ADVICE = {
    "Food Quality":  "review food preparation and taste consistency",
    "Cleanliness":   "increase cleaning frequency and pest control",
    "Menu Variety":  "add more menu options / rotate dishes",
    "Service Speed": "add staff or streamline queues at peak hours",
}

def recommend_llm(caf, weakest, val):
    """Ask the LLM for a one-sentence recommendation; fall back to a template."""
    prompt = (
        f"A cafeteria's weakest aspect is '{weakest}' (score {val} out of 1.0). "
        "Write ONE short, practical recommendation (max 20 words) for the cafeteria "
        "management to improve it. Reply with only the sentence."
    )
    try:
        out = llm_call(prompt).strip().strip('"')
        if out:
            return out.split("\n")[0]
    except Exception:
        pass
    return ADVICE[weakest]               # rule-based fallback

def recommend(vectors, use_llm=True):
    out = {}
    for caf, vec in vectors.items():
        weakest = min(ASPECTS, key=lambda a: vec[a])
        val = vec[weakest]
        advice = recommend_llm(caf, weakest, val) if use_llm else ADVICE[weakest]
        out[caf] = (weakest, val, advice)
    return out


# ================================ RUN THE AGENT ================================
if __name__ == "__main__":
    # --- setup: reuse the existing pipeline, FCM sets the baseline MFs ---
    matching, vu = load_lexicon(LEX)
    sia = build_analyzer(vu)
    scored = score_dataframe(load_reviews_csv(CSV), sia, matching, vu)
    baseline_mfs = learn_membership_functions(scored)      # <-- FCM baseline (untouched)
    vectors, _ = cafeteria_vectors(scored)

    base_sanity, base_ratings = evaluate(baseline_mfs, vectors)

    print("=" * 60)
    print("AGENTIC LAYER — sense / reason / act / reflect")
    print("=" * 60)

    # --- SENSE ---
    problem, avg = sense(baseline_mfs, base_sanity)
    print(f"\n[SENSE]  all-average cafeteria rates {avg} ({label(avg)})")
    if not problem:
        print("         No problem detected — membership functions look healthy.")
        print("         Agent takes no action (this is correct behaviour).")
    else:
        print(f"         Problem: an average cafeteria is rated LOW (should be Medium).")
        # --- REASON (LLM, with rule-based fallback) ---
        culprit, source = reason_llm(baseline_mfs)
        c0 = round(float(baseline_mfs[culprit]['peaks'][0]), 3)
        print(f"\n[REASON] ({source}) Culprit aspect: '{culprit}' — its Low centre is {c0},")
        print(f"         so a mid score (0.5) is misread as Low. Plan: shift its")
        print(f"         Low/Medium peaks down (bounded, max {MAX_SHIFT}).")

        # --- ACT + REFLECT (tries smallest safe fix, verifies, reverts if unsafe) ---
        fixed_mfs, used_shift, new_sanity = reflect(baseline_mfs, culprit, vectors, base_sanity)

        if fixed_mfs is None:
            print(f"\n[ACT]    No bounded shift fixed it safely.")
            print(f"[REFLECT] Reverting to FCM baseline (safety first).")
            final_mfs = baseline_mfs
        else:
            print(f"\n[ACT]    Shifted '{culprit}' peaks down by {used_shift}.")
            print(f"           {[round(float(x),3) for x in baseline_mfs[culprit]['peaks']]}  ->  {fixed_mfs[culprit]['peaks']}")
            print(f"[REFLECT] Re-checked sanity — fix accepted:")
            print(f"           all-average : {base_sanity['all average']} ({label(base_sanity['all average'])})"
                  f"  ->  {new_sanity['all average']} ({label(new_sanity['all average'])})")
            print(f"           bad-food veto still {label(new_sanity['bad food'])}, "
                  f"all-excellent still {label(new_sanity['all excellent'])}")
            final_mfs = fixed_mfs

        # --- show before/after cafeteria ratings ---
        _, final_ratings = evaluate(final_mfs, vectors)
        print("\n--- Cafeteria ratings: before -> after the agent ---")
        for caf in vectors:
            b, f = base_ratings[caf], final_ratings[caf]
            print(f"   {caf:34} {b} ({label(b)})  ->  {f} ({label(f)})")

    # --- EXTERNAL OUTPUT: recommendations (the practical half) ---
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS (external action)")
    print("=" * 60)
    for caf, (asp, val, advice) in recommend(vectors).items():
        print(f"   {caf}")
        print(f"      weakest aspect: {asp} ({val}) -> {advice}\n")
