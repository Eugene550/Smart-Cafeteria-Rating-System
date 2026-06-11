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
| `*Form_Responses*.csv` | data | The Google Form review export. Scripts expect `Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1.csv`. Rename your export or update `CSV` path in scripts. |

> `cafeteria_fis.py` runs the whole engine (it imports stages 1 and 2). Run earlier files individually only to inspect that stage's output. 
---

## Software Installation (First-Time Setup)

### 1. Install Python

Download Python 3.11 or later from:

https://www.python.org/downloads/

- Check **"Add Python to PATH"** during installation.
- Verify installation:

```bash
python --version
```

Expected output:

```text
Python 3.11.x
```

---

### 2. Install Anaconda

Download and install from:

https://www.anaconda.com/download

Use the default settings. After installation, open:

```text
Anaconda Prompt
```

from the Windows Start Menu.

---

### 3. Install Visual Studio Code (VS Code)

Download from:

https://code.visualstudio.com/

Install with default settings.

---

### 4. Create a Conda Environment

Open **Anaconda Prompt**:

```bash
conda create -n cafeteria python=3.11
```

Type `y` to confirm. Activate the environment:

```bash
conda activate cafeteria
```

---

### 5. Open the Project in VS Code

Navigate to your project folder:

```bash
cd path_to_project_folder
```

Example:

```bash
cd Desktop
cd Smart_Cafeteria_Rating_System
```

Open VS Code:

```bash
code .
```

---

### 6. Select Python Interpreter in VS Code

1. Press **Ctrl + Shift + P**
2. Search for `Python: Select Interpreter`
3. Choose `cafeteria (Python 3.11)`.

---

### 7. Install Required Libraries

Activate the Conda environment first:

```bash
conda activate cafeteria
```

Then run:

```bash
pip install vaderSentiment openpyxl pandas scikit-fuzzy networkx numpy scipy
```

Verify installation:

```bash
pip list
```

---

## 1. Install Required Libraries (Original Section)

> `scikit-fuzzy` and `networkx` are needed for FIS (Stage 3). `ollama` is only needed for optional normalisation.

---

## 2. Text Normalisation (Ollama)

Cleans messy English into standard English for VADER.

### 2a. Install Ollama
https://ollama.com

Ensure the **Ollama app is running** (system tray icon).

### 2b. Pull and test the model (use Command Prompt)

```bat
ollama --version
ollama pull llama3.2:3b
ollama run llama3.2:3b
```

Type "hello" to confirm it replies, then `/bye` to exit.

### 2c. Produce the cleaned CSV

```bash
pip install ollama
python normalise_to_csv.py
```

Creates **`reviews_clean.csv`** with cleaned reviews.

### 2d. Rate using the cleaned text

Set:

```python
CSV = "reviews_clean.csv"
```

in `cafeteria_fis.py` (and `cafeteria_fcm.py` if run separately). Running Stage 3 automatically uses the cleaned column.

---

## 3. Set Your File Paths

```python
LEX = "Variable_and_keywords_refined.xlsx"
CSV = "Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1.csv"
```

For cleaned text:

```python
CSV = "reviews_clean.csv"
```

---

## 4. Run the Engine

```bash
python cafeteria_frontend.py   # Stage 1
python cafeteria_fcm.py        # Stage 2
python cafeteria_fis.py        # Stage 3 (FULL pipeline)
```

---

---

## General Troubleshooting

- `ModuleNotFoundError: No module named 'skfuzzy'` → `pip install scikit-fuzzy`
- `ModuleNotFoundError: No module named 'networkx'` → `pip install networkx`
- `ModuleNotFoundError: No module named 'cafeteria_frontend'` → keep all `.py` files in the same folder
- `FileNotFoundError` → fix `LEX` / `CSV` paths
- Scores printing as `np.float64(0.53)` → cosmetic only

---

## Notes for Report / Viva

- VADER scores aspects using the lexicon.
- FCM is run per aspect on all reviews pooled to share Low/Medium/High scales across cafeterias.
- Aspects not mentioned default to Medium.
- FPC is reported as a cluster-validity check.
- Normalisation is a front-end cleaning step; keeping both `review` and `review_clean` allows validation.
