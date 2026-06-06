"""
Smart Cafeteria Rating System — Stage 0 (front bolt-on): text normalisation
Messy English review  ->  clean standard English  (so VADER reads it correctly)

Runs BEFORE aspect extraction. Order:
  1. Cheap RULE pass: predictable fixes (abbreviations, particles) — free, transparent.
  2. Small local LLM (Ollama, llama3.2:3b) rewrites the rest.
The model ONLY rewrites text into clean English; it never decides aspect or sentiment
(that stays with the lexicon + VADER). Original and cleaned text are kept side by side.

Local <-> API swap: change ONLY `MODEL_CALL` at the bottom. Nothing else moves.
"""

import re

# ---------- 1. cheap rule pass (no model needed) ----------
RULE_MAP = {
    r"\bv\b": "very", r"\bgud\b": "good", r"\bkinda\b": "kind of",
    r"\bppl\b": "people", r"\bbtw\b": "by the way", r"\bn\b": "and",
    r"\bsedap\b": "tasty", r"\bshiok\b": "great", r"\bmahal\b": "expensive",
    r"\bmurah\b": "cheap", r"\bbanyak\b": "many", r"\bsikit\b": "little",
}
PARTICLES = [" lah", " lor", " meh", " leh", " ah", " liao"]

def rule_clean(text):
    t = str(text)
    for pat, rep in RULE_MAP.items():
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    for p in PARTICLES:
        t = re.sub(p + r"\b", "", t, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip()

# ---------- 2. the small-LLM rewrite ----------
PROMPT = (
    "Rewrite this cafeteria review in clear, standard English.\n"
    "Rules: keep the meaning and sentiment EXACTLY; do not add anything; "
    "do not make it more positive, more negative, or more formal; "
    "convert ratings like '5/10' into plain words (e.g. 'average').\n"
    "Return ONLY the rewritten review.\n\n"
    "Review: {text}\nRewritten:"
)

def _strip_preamble(out):
    out = out.strip().strip('"').strip()
    # remove a leading "Rewritten:" / "Here is ...:" if the model adds one
    m = re.match(r"^(rewritten|here.*?|sure.*?)[:\-]\s*(.*)$", out, flags=re.IGNORECASE | re.DOTALL)
    return m.group(2).strip() if m else out

def ollama_call(prompt, model="llama3.2:3b"):
    import ollama
    resp = ollama.chat(model=model,
                       messages=[{"role": "user", "content": prompt}],
                       options={"temperature": 0.0})   # 0 -> reproducible
    return _strip_preamble(resp["message"]["content"])

def passthrough_call(prompt):
    """Fallback used when Ollama isn't available — no LLM rewrite (rule pass only)."""
    return None

# ---------- public API ----------
def normalise_text(text, model_call):
    pre = rule_clean(text)
    try:
        out = model_call(PROMPT.format(text=pre))
        if out:
            return out
    except Exception:
        pass
    return pre            # degrade gracefully to the rule-cleaned text

def normalise_reviews(df, model_call, col="review"):
    out = df.copy()
    out["review_clean"] = out[col].apply(lambda t: normalise_text(t, model_call))
    return out

# ---------- choose the model here (local now, API later) ----------
MODEL_CALL = ollama_call         # <- change to your API function later


if __name__ == "__main__":
    samples = [
        "Food kinda gud but the queue v long lah",
        "Cleanliness 5/10, sometimes got flies",
        "menu banyak choices, sedap n murah",
        "service ok ah, not bad",
    ]
    print("=== rule pass only (works without Ollama) ===")
    for s in samples:
        print(f"  raw : {s}")
        print(f"  rule: {rule_clean(s)}\n")

    print("=== full normalise (needs Ollama running) ===")
    # uses MODEL_CALL; falls back to rule pass if Ollama isn't installed/running
    for s in samples:
        print(f"  raw  : {s}")
        print(f"  clean: {normalise_text(s, MODEL_CALL)}\n")
