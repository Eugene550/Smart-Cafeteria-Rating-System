"""
One-time normalisation: read the raw Google Form CSV, clean every review with the
local LLM, and save a NEW csv with an extra 'review_clean' column.

Run this ONCE (needs Ollama running). After it finishes, point the pipeline's CSV
path at the *_clean.csv file — the rest of the system (frontend/fcm/fis) will
automatically score the cleaned text, no other change needed.

Compare before/after: run the pipeline on the raw CSV, then on the clean CSV.
"""

from cafeteria_frontend import load_reviews_csv
from cafeteria_normalise import normalise_reviews, MODEL_CALL

RAW = "Google_Form___Text-Only_Cafeteria_Feedback__Responses__-_Form_Responses_1.csv"
OUT = "reviews_clean.csv"

if __name__ == "__main__":
    df = load_reviews_csv(RAW)
    print(f"Normalising {len(df)} reviews with the local model... (this takes a minute)")
    cleaned = normalise_reviews(df, MODEL_CALL, col="review")   # adds 'review_clean'
    cleaned.to_csv(OUT, index=False)
    print(f"Saved -> {OUT}\n")

    print("=== before / after (first 6) ===")
    for i in range(min(6, len(cleaned))):
        print("RAW  :", str(cleaned.iloc[i]["review"])[:90])
        print("CLEAN:", str(cleaned.iloc[i]["review_clean"])[:90])
        print()
