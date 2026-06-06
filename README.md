# Smart Cafeteria Rating System

A hybrid fuzzy-logic system that turns text reviews into a 1.0–5.0 rating per cafeteria.

- **Knowledge-driven half:** expert IF–THEN rules in a Mamdani fuzzy inference system.
- **Data-driven half:** Fuzzy C-Means learns where Low / Medium / High sit and sets the membership functions.
- The two are coupled — FCM builds the scale, the rules reason on it; neither produces a rating alone.

Pipeline: `reviews → (normalise) → aspect extraction → VADER scoring → FCM → Mamdani FIS → rating`

---

## Project Files

| File | Stage | What it does |
| ---- | ----- | ------------ |
| `cafeteria_frontend.py` | 1 | Reads the CSV, scores each review per aspect (lexicon + VADER) |
| `cafeteria_fcm.py` | 2 | Pools reviews per cafeteria; runs FCM to learn membership functions |
| `cafeteria_fis.py` | 3 | Mamdani FIS — combines stages 1–2 and outputs the final ratings |
| `cafeteria_normalise.py` | 0 (optional) | Cleans messy English to standard English before scoring |
| `Variable_and_keywords_refined.xlsx` | data | Lexicon (aspect words) + membership-function defaults |
| `Rule_based_refined.txt` | data | The 17 expert rules (reference; rules are coded in `cafeteria_fis.py`) |
| `*Form_Responses*.csv` | data | The Google Form review export |

> `cafeteria_fis.py` runs the whole engine (it imports stages 1 and 2). Run the
> earlier files on their own only if you want to inspect that stage's output.

---

## 1. Install Required Libraries

Activate your conda environment first, then run:

```bash
pip install vaderSentiment openpyxl pandas scikit-fuzzy networkx numpy scipy
```

> `scikit-fuzzy` and `networkx` are both needed for the FIS (Stage 3).

---

## 2. Set Your File Paths

Open each script and, near the bottom, point `LEX` and `CSV` to where your files
are. If everything is in the same folder, just use the filenames:

```python
LEX = "Variable_and_keywords_refined.xlsx"
CSV = "Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1.csv"
```

---

## 3. Run the Engine

Run the stages in order to inspect each, or just run Stage 3 for the full result.

```bash
python cafeteria_frontend.py   # Stage 1: per-review aspect scores
python cafeteria_fcm.py        # Stage 2: learned membership functions + cafeteria vectors
python cafeteria_fis.py        # Stage 3: FULL pipeline -> final ratings
```

`cafeteria_fis.py` prints a rating per cafeteria plus face-validity sanity checks
(all-excellent → High, bad food → Low via the veto rule, etc.).

---

## 4. (Optional) Text Normalisation

Cleans messy English ("queue v long lah", "5/10") into standard English so VADER
reads it correctly. Needs a small local model via Ollama.

```bash
# install Ollama from https://ollama.com  then:
ollama pull llama3.2:3b
pip install ollama
python cafeteria_normalise.py
```

Notes:
- If Ollama is not running, the step **falls back to the rule pass** instead of crashing.
- Temperature is 0, so output is reproducible.
- To switch to an API model later, change only the `MODEL_CALL` line in the file.
- This step is **not yet wired into the main pipeline** — it currently runs standalone.

---

## Troubleshooting

- `ModuleNotFoundError: No module named 'skfuzzy'` → install name is `scikit-fuzzy` (with hyphen).
- `ModuleNotFoundError: No module named 'networkx'` → `pip install networkx`.
- `ModuleNotFoundError: No module named 'cafeteria_frontend'` → keep all `.py` files in the same folder.
- `FileNotFoundError` → fix the `LEX` / `CSV` paths (Step 2).
- Scores printing as `np.float64(0.53)` → cosmetic only; the value is correct.

---

## Notes for the Report / Viva

- Aspects are scored by **VADER** (strength) using the **lexicon** for which-aspect; scores are never hand-set.
- **FCM** is run per aspect (1-D) on all reviews pooled, so the Low/Medium/High scale is shared across cafeterias.
- An aspect mentioned by **no** review falls back to Medium (rare, since the form prompts all four aspects).
- FPC (fuzzy partition coefficient) is reported per aspect as a cluster-validity check.
