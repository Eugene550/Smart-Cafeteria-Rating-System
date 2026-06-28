"""
Smart Cafeteria Rating System — Stage 0 (front bolt-on): text normalisation
Messy review (English / Malay / slang)  ->  clean standard English  (so VADER reads it correctly)

Runs BEFORE aspect extraction. Pure-LLM design:
  The raw review is sent straight to a small local LLM (Ollama, llama3.2:3b), which
  rewrites it into clean standard English — translating Malay words, dropping Malaysian
  particles (lah/lor/meh/liao), and expanding slang — WITHOUT changing meaning or sentiment.
There is no hand-written word list; all of that is handled by the prompt.

The model ONLY rewrites text into clean English; it never decides aspect or sentiment
(that stays with the lexicon + VADER). Original and cleaned text are kept side by side.

If Ollama is unavailable the text passes through unchanged (no normalisation), so the
pipeline still runs end to end.

Local <-> API swap: change ONLY `MODEL_CALL` at the bottom. Nothing else moves.
"""

import re

# ---------- the small-LLM rewrite ----------
PROMPT = (
    "Rewrite this cafeteria review in clear, standard English.\n"
    "Rules:\n"
    "- Translate any Malay or non-English words into English.\n"
    "- Remove Malaysian particles such as 'lah', 'lor', 'meh', 'leh', 'ah', 'liao'.\n"
    "- Expand abbreviations and slang (e.g. 'gud' -> 'good', 'v' -> 'very').\n"
    "- Convert ratings like '5/10' into plain words (e.g. 'average').\n"
    "- Keep the meaning and sentiment EXACTLY; do not add anything; "
    "do not make it more positive, more negative, or more formal.\n"
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
    """Fallback swap used when no LLM is wanted — returns nothing (text passes through)."""
    return None

# ---------- public API ----------
def normalise_text(text, model_call):
    raw = str(text).strip()
    if not raw:
        return raw
    try:
        out = model_call(PROMPT.format(text=raw))
        if out:
            return out
    except Exception:
        pass
    return raw            # Ollama unavailable -> pass through unchanged (no normalisation)

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
    print("=== full normalise (needs Ollama running; passes text through if not) ===")
    for s in samples:
        print(f"  raw  : {s}")
        print(f"  clean: {normalise_text(s, MODEL_CALL)}\n")
