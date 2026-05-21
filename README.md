# Smart-Cafeteria-Rating-System
# Smart Cafeteria Project Setup Instructions

## Step 1: Install Anaconda
Download Anaconda for your OS: https://www.anaconda.com/products/distribution
Install it using default settings.

## Step 2: Create a New Environment
Open Anaconda Prompt (Windows) or terminal (Mac/Linux):

```
conda create -n smartcafeteria python=3.10
```
- `smartcafeteria` is the environment name.
- Python 3.10 is recommended.

## Step 3: Activate the Environment
```
conda activate smartcafeteria
```

## Step 4: Install Required Packages
Install core packages using conda:
```
conda install numpy pandas openpyxl scipy networkx
```
Install additional packages using pip:
```
pip install scikit-fuzzy spacy ipykernel
```

## Step 5: Download spaCy English Model
```
python -m spacy download en_core_web_sm
```

## Step 6: Register the Environment in Jupyter
```
python -m ipykernel install --user --name=smartcafeteria --display-name "Python (smartcafeteria)"
```
- `--name`: internal kernel name
- `--display-name`: shows in Jupyter kernel selector

## Step 7: Launch Jupyter Notebook
```
jupyter-notebook
```
- This opens Jupyter Notebook in your browser.
- Navigate to your project folder and open `Fuzzy_project.ipynb`.

## Step 8: Verify Setup (Optional)
Run the following to check if all packages are installed correctly:
```python
import numpy, pandas, spacy, skfuzzy
print("All packages OK")
```

## Notes
- Always ensure the `smartcafeteria` environment is selected as the kernel in Jupyter Notebook or VS Code.
- You can add VS Code integration later, but Jupyter Notebook is recommended for interactive testing.
- When more survey data is collected, the FIS can be run on multiple reviews in batches.

- Always ensure the `smartcafeteria` environment is selected as the kernel in Jupyter Notebook or VS Code.
- You can add VS Code integration later, but Jupyter Notebook is recommended for interactive testing.
- When more survey data is collected, the FIS can be run on multiple reviews in batches.
