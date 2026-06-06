# Install the two libraries it needs:
pip install vaderSentiment openpyxl pandas "Copy"

# Then fix the two file paths at the bottom of the script. Right now they point to my environment:
pythonLEX = "/mnt/user-data/uploads/Variable_and_keywords_refined.xlsx"
CSV = "/mnt/user-data/uploads/Google_Form___..._Responses_1.csv"

# Change those to wherever the two files sit on your computer — for example, if everything's in the same folder, just use the filenames:
pythonLEX = "Variable_and_keywords_refined.xlsx"
CSV = "Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1.csv"

# Then run it:
python cafeteria_frontend.py
