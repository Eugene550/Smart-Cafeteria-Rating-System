# Smart Cafeteria Rating System

## Overview

This project is a **Hybrid Fuzzy Logic-Based Cafeteria Rating System** that evaluates cafeteria performance based on customer reviews.

The system combines:

- Knowledge-Driven Approach (Fuzzy Inference System)
- Data-Driven Approach (Fuzzy C-Means Clustering)
- Sentiment Analysis using VADER
- Expert-defined Rules

---

## Project Structure

```text
Project_codes_file/
│
├── cafeteria_frontend.py
├── cafeteria_fcm.py
├── cafeteria_fis.py
├── cafeteria_normalise.py
├── normalise_to_csv.py
│
├── reviews_clean.csv
├── Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1.csv
│
├── Variable_and_keywords_refined.xlsx
├── Rule_based_refined.txt
│
└── README.md
```

---

# Prerequisites

Before running the project, install the following software:

## 1. Install Python

Download the latest Python (3.11 recommended) from:

https://www.python.org/downloads/

- Choose the installer for your OS (Windows / Mac / Linux).
- **Important:** Check the box **“Add Python to PATH”** before clicking Install.
- Verify installation by opening a terminal / command prompt and running:

```bash
python --version
```

Expected output example:

```text
Python 3.11.4
```

---

## 2. Install Anaconda

Download and install Anaconda:

https://www.anaconda.com/download

Use the default installation settings.

---

## 3. Install Visual Studio Code (VS Code)

Download and install VS Code:

https://code.visualstudio.com/

Use the default installation settings.

---

# Setting Up the Environment

## Step 1: Open Anaconda Prompt

After installing Anaconda:

1. Open the Start Menu.
2. Search for:

```text
Anaconda Prompt
```

3. Open it.

You should see:

```text
(base) C:\Users\YourName>
```

---

## Step 2: Create a New Conda Environment

Run the following command:

```bash
conda create -n cafeteria python=3.11
```

When prompted, type:

```text
y
```

and press Enter.

---

## Step 3: Activate the Environment

Run:

```bash
conda activate cafeteria
```

You should see:

```text
(cafeteria) C:\Users\YourName>
```

---

## Step 4: Install Required Libraries

Install all required libraries using:

```bash
pip install pandas numpy scikit-fuzzy openpyxl vaderSentiment
```

Alternatively, install them one by one:

```bash
pip install pandas
pip install numpy
pip install scikit-fuzzy
pip install openpyxl
pip install vaderSentiment
```

---

# Opening the Project in VS Code

## Step 5: Navigate to the Project Folder

Example:

```bash
cd Desktop
cd Project_codes_file
```

Replace the path with your actual project location.

---

## Step 6: Open VS Code

Run:

```bash
code .
```

VS Code will open the project folder.

---

## Step 7: Select the Correct Python Interpreter

1. Press:

```text
Ctrl + Shift + P
```

2. Search for:

```text
Python: Select Interpreter
```

3. Select:

```text
cafeteria (Python 3.11)
```

This ensures VS Code uses the correct Anaconda environment.

---

# Verify Installation

Create a test file:

```python
import pandas
import numpy
import skfuzzy
import openpyxl
import vaderSentiment

print("All packages installed successfully!")
```

Run:

```bash
python test.py
```

Expected output:

```text
All packages installed successfully!
```

---

# Running the System

## Stage 1: Process Customer Reviews

Run:

```bash
python cafeteria_frontend.py
```

### Purpose

- Read customer reviews
- Detect cafeteria aspects
- Perform sentiment analysis
- Generate aspect scores

---

## Stage 2: Fuzzy C-Means Clustering (FCM)

Run:

```bash
python cafeteria_fcm.py
```

### Purpose

- Learn fuzzy membership function centres
- Generate Low, Medium, and High fuzzy sets
- Produce cafeteria average vectors

---

## Stage 3: Fuzzy Inference System (FIS)

Run:

```bash
python cafeteria_fis.py
```

### Purpose

- Apply fuzzy rules
- Generate final cafeteria ratings
- Produce fuzzy classification results

---

# Optional: Text Normalisation Using Ollama

The file:

```text
cafeteria_normalise.py
```

supports local Large Language Models (LLMs) through Ollama.

If Ollama is not installed, the system will automatically use rule-based text cleaning.

---

## Install Ollama

Download Ollama:

https://ollama.com

Install using default settings.

---

## Download a Model

Run:

```bash
ollama pull llama3.2:3b
```

---

## Verify Installation

Run:

```bash
ollama run llama3.2:3b
```

If the model responds, Ollama has been installed successfully.

---

# Common Errors and Solutions

## Error: ModuleNotFoundError

Example:

```text
ModuleNotFoundError: No module named 'pandas'
```

### Solution

Install the missing package:

```bash
pip install pandas
```

---

## Error: Python Was Not Found

### Solution

Activate the Conda environment first:

```bash
conda activate cafeteria
```

---

## Error: No Module Named 'skfuzzy'

### Solution

```bash
pip install scikit-fuzzy
```

---

## Error: No Module Named 'vaderSentiment'

### Solution

```bash
pip install vaderSentiment
```

---

# Recommended Workflow

Every time you want to run the project:

### 1. Open Anaconda Prompt

```bash
conda activate cafeteria
```

### 2. Navigate to the Project Folder

```bash
cd path_to_project
```

### 3. Open VS Code

```bash
code .
```

### 4. Run the System

```bash
python cafeteria_frontend.py
```

```bash
python cafeteria_fcm.py
```

```bash
python cafeteria_fis.py
```

---

# Creating a Requirements File (Recommended)

Create a file named:

```text
requirements.txt
```

Add:

```text
pandas
numpy
scikit-fuzzy
openpyxl
vaderSentiment
```

Users can then install all dependencies with a single command:

```bash
pip install -r requirements.txt
```

---

# Authors

**Smart Cafeteria Rating System**

A Hybrid Fuzzy Logic-Based Cafeteria Evaluation System using:

- Sentiment Analysis (VADER)
- Fuzzy C-Means Clustering (FCM)
- Mamdani Fuzzy Inference System (FIS)

to evaluate cafeteria performance based on customer reviews.
