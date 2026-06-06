# Smart Cafeteria Rating System

A hybrid fuzzy-logic system that turns text reviews into a 1.0–5.0 rating per cafeteria.

- **Knowledge-driven half:** expert IF–THEN rules in a Mamdani fuzzy inference system.
- **Data-driven half:** Fuzzy C-Means learns where Low / Medium / High sit and sets the membership functions.
- The two are coupled — FCM builds the scale, the rules reason on it; neither produces a rating alone.

Pipeline: `reviews → (normalise) → aspect extraction → VADER scoring → FCM → Mamdani FIS → rating`

---

## Project Files

(listed in pipeline order)

| File | Stage | What it does |
| ---- | ----- | ------------ |
| `cafeteria_normalise.py` | 0 | Cleaning functions (rule pass + local LLM); run alone to test cleaning |
| `normalise_to_csv.py` | 0 | One-time helper: produces `reviews_clean.csv` from the raw CSV |
| `cafeteria_frontend.py` | 1 | Reads the CSV, scores each review per aspect (lexicon + VADER) |
| `cafeteria_fcm.py` | 2 | Pools reviews per cafeteria; runs FCM to learn membership functions |
| `cafeteria_fis.py` | 3 | Mamdani FIS — combines stages 1–2 and outputs the final ratings |
| `Variable_and_keywords_refined.xlsx` | data | Lexicon (aspect words) + membership-function defaults |
| `Rule_based_refined.txt` | data | The 17 expert rules (reference; rules are coded in `cafeteria_fis.py`) |
| `*Form_Responses*.csv` | data | The Google Form review export. (Make sure the google form csv file you download must change to this name `Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1`) |

> `cafeteria_fis.py` runs the whole engine (it imports stages 1 and 2). Run the
> earlier files on their own only if you want to inspect that stage's output.
> `aspect_scoring.py` (an early draft) is no longer used and can be deleted.


---
## (我们主要用VS Code)

## 1. Install Required Libraries （用cd command改去你们save这些file的folder path）

Open the project folder (确保你的folder里面有所有你下载的python file, csv和txt file) in VS Code, then open its terminal (Terminal → New Terminal) and run:

```bash
pip install vaderSentiment openpyxl pandas scikit-fuzzy networkx numpy scipy
```

> `scikit-fuzzy` and `networkx` are both needed for the FIS (Stage 3).
> `ollama` is only needed for the optional normalisation step (Section 2).


---


## 2. Text Normalisation (Ollama)

Cleans messy English ("queue v long lah", "5/10") into standard English so VADER
reads it correctly. Needs a small local model via Ollama.

### 2a. Install Ollama (下载了exe要install，install完之后直接退出)
Install from https://ollama.com (one Windows installer). Make sure the **Ollama app
is running** — look for its icon in the system tray (bottom-right near the clock;
click the arrow to show hidden icons).

### 2b. Pull and test the model (use **Command Prompt**（关掉VS Code, 开cmd跑）)
On Windows the `ollama` command often works only in **cmd**. Open Command Prompt
(search "cmd" in the Start menu):

```bat
ollama --version
ollama pull llama3.2:3b
ollama run llama3.2:3b
```

For the last one, type "hello", confirm it replies, then type `/bye` to exit. (这里是测试ollama的功能，你先Hello, 他会问你东西，然后可以测试，最后不要了就打个 `/bye`)

### 2c. Produce the cleaned CSV (from the VS Code terminal (这个步骤开始用回**VS Code**的Terminal来跑)
```bash
pip install ollama
python normalise_to_csv.py
```

This reads your raw CSV, cleans every review with the local model, prints a few
before/after pairs, and saves **`reviews_clean.csv`** (same data + a `review_clean`
column). Run it once; it takes a minute or two.

### 2d. Rate using the cleaned text （这个步骤是跟你说跑了2c后，ollama整理后的data会save去一个新的csv file叫 `reviews_clean`）
Set `CSV = "reviews_clean.csv"` in `cafeteria_fis.py` (and `cafeteria_fcm.py` if you
run it alone), then run `python cafeteria_fis.py`. The pipeline **automatically scores
the `review_clean` column when it is present**, so no other change is needed.

> Tip: run the pipeline once on the raw CSV and once on `reviews_clean.csv` and compare
> the ratings. That before/after is good evidence for the report that cleaning helped.

### Notes
- If Ollama is not running, cleaning **falls back to the rule pass** instead of crashing.
- Temperature is 0, so the model output is reproducible.
- To switch to an API model later, change only the `MODEL_CALL` line in `cafeteria_normalise.py`.
- The model only rewrites text; it never decides aspect or sentiment (that stays with the lexicon + VADER).

### Troubleshooting Ollama
- `'ollama' is not recognized` in PowerShell → use **cmd**. If cmd also fails, restart
  the terminal, then restart the PC, then reinstall.
- Ignore Ollama's "launch coding agents" screen (Claude Code, Codex, Droid…) — unrelated.
  You only need `ollama pull` and `ollama run`.
- The pull just being slow is normal — it is downloading the model.


---


## 3. Set Your File Paths （这个不用理）

Open each script and, near the bottom, point `LEX` and `CSV` to your files. If
everything is in the same folder, just use the filenames:

```python
LEX = "Variable_and_keywords_refined.xlsx"
CSV = "reviews_clean.csv"
```

To rate the **cleaned** text instead, set `CSV = "reviews_clean.csv"` (after Section 2).

---

## 4. Run the Engine

Run the stages in order to inspect each, or just run Stage 3 for the full result.

```bash
python cafeteria_frontend.py   # Stage 1: per-review aspect scores
python cafeteria_fcm.py        # Stage 2: learned membership functions + cafeteria vectors
python cafeteria_fis.py        # Stage 3: FULL pipeline -> final ratings
```

`cafeteria_fis.py` prints a rating per cafeteria plus face-validity sanity checks
(all-excellent → High, bad food → Low via the veto rule, etc.).

---

## General Troubleshooting

- `ModuleNotFoundError: No module named 'skfuzzy'` → install name is `scikit-fuzzy` (with hyphen).
- `ModuleNotFoundError: No module named 'networkx'` → `pip install networkx`.
- `ModuleNotFoundError: No module named 'cafeteria_frontend'` → keep all `.py` files in the same folder.
- `FileNotFoundError` → fix the `LEX` / `CSV` paths (Section 3).
- Scores printing as `np.float64(0.53)` → cosmetic only; the value is correct.

---

## Notes for the Report / Viva

- Aspects are scored by **VADER** (strength) using the **lexicon** for which-aspect; scores are never hand-set.
- **FCM** is run per aspect (1-D) on all reviews pooled, so the Low/Medium/High scale is shared across cafeterias.
- An aspect mentioned by **no** review falls back to Medium (rare, since the form prompts all four aspects).
- FPC (fuzzy partition coefficient) is reported per aspect as a cluster-validity check.
- Normalisation is a front-end cleaning step only; keeping `review` and `review_clean` side by side lets you validate it didn't change meaning.
