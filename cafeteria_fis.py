"""
Smart Cafeteria Rating System — Stage 3 (knowledge-driven): Mamdani FIS

This is the join. The FIS is built from:
  - membership functions whose PEAKS came from FCM (Stage 2)  -> data-driven scale
  - the 17 expert IF-THEN rules from Rule_based_refined.txt     -> knowledge-driven logic
It then rates each cafeteria's averaged vector (Stage 2) on a 1.0-5.0 scale.

Neither half works alone: remove the rules and there's nothing to combine the
aspects; remove FCM and the rules have no calibrated scale to fire on.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from cafeteria_frontend import (
    load_lexicon, build_analyzer, load_reviews_csv, score_dataframe, ASPECTS,
)
from cafeteria_fcm import learn_membership_functions, cafeteria_vectors

# Output Rating sets (1.0-5.0) from the Membership Functions sheet
RATING_MF = {"Low": (1, 1, 2.5), "Medium": (2, 3, 4), "High": (3.5, 5, 5)}
KEY = {"Food Quality": "food", "Cleanliness": "clean",
       "Menu Variety": "variety", "Service Speed": "speed"}


def build_fis(mfs):
    u = np.arange(0, 1.001, 0.01)
    food    = ctrl.Antecedent(u, "food")
    clean   = ctrl.Antecedent(u, "clean")
    variety = ctrl.Antecedent(u, "variety")
    speed   = ctrl.Antecedent(u, "speed")
    rating  = ctrl.Consequent(np.arange(1, 5.001, 0.01), "rating")

    ants = {"food": food, "clean": clean, "variety": variety, "speed": speed}
    for aspect, ant in zip(ASPECTS, [food, clean, variety, speed]):
        for level in ("Low", "Medium", "High"):
            ant[level] = fuzz.trimf(ant.universe, mfs[aspect][level])
    for level, tri in RATING_MF.items():
        rating[level] = fuzz.trimf(rating.universe, tri)

    R = ctrl.Rule
    rules = [
        R(food["High"] & clean["High"] & variety["High"] & speed["High"], rating["High"]),   # 1
        R(food["High"] & clean["High"] & speed["High"], rating["High"]),                      # 2
        R(food["High"] & clean["High"] & variety["Medium"] & speed["High"], rating["High"]),  # 3
        R(food["High"] & variety["High"] & speed["High"], rating["High"]),                    # 4
        R(food["High"] & clean["Medium"] & variety["Medium"] & speed["Medium"], rating["High"]),  # 5
        R(food["Medium"] & clean["Medium"] & variety["Medium"] & speed["Medium"], rating["Medium"]),  # 6
        R(food["Medium"] & clean["High"] & variety["Medium"] & speed["Medium"], rating["Medium"]),    # 7
        R(food["High"] & speed["Low"], rating["Medium"]),                                     # 8
        R(food["High"] & clean["Medium"] & variety["High"] & speed["Low"], rating["Medium"]), # 9
        R(clean["High"] & variety["Low"] & speed["High"], rating["Medium"]),                  # 10
        R(food["High"] & variety["Low"] & speed["Low"], rating["Medium"]),                    # 11
        R(food["Medium"] & clean["Medium"] & variety["High"] & speed["High"], rating["Medium"]),  # 12
        R(food["Medium"] & clean["Medium"] & variety["Medium"] & speed["Low"], rating["Medium"]),  # 13
        R(clean["High"] & variety["Low"] & speed["Low"], rating["Medium"]),                   # 14
        R(food["Medium"] & clean["Medium"] & variety["Low"] & speed["Low"], rating["Low"]),   # 15
        R(food["Low"] | clean["Low"], rating["Low"]),                                         # 16 veto
    ]
    return ctrl.ControlSystem(rules), ants


def rate(vector, system, ants):
    sim = ctrl.ControlSystemSimulation(system)
    for aspect, key in KEY.items():
        sim.input[key] = vector[aspect]
    try:
        sim.compute()
        return round(float(sim.output["rating"]), 2)
    except Exception:
        return 3.0   # rule 17: default Medium if nothing fired


def label(score):
    return "Low" if score < 2.5 else ("High" if score >= 3.5 else "Medium")


if __name__ == "__main__":
    LEX = "Variable_and_keywords_refined.xlsx"
    CSV = "reviews_clean.csv"

    matching, vu = load_lexicon(LEX)
    sia = build_analyzer(vu)
    scored = score_dataframe(load_reviews_csv(CSV), sia, matching, vu)
    mfs = learn_membership_functions(scored)
    vectors, _ = cafeteria_vectors(scored)

    system, ants = build_fis(mfs)

    print("=== FINAL CAFETERIA RATINGS ===\n")
    for caf, vec in vectors.items():
        score = rate(vec, system, ants)
        print(f"{caf}")
        print(f"   inputs : {', '.join(f'{a.split()[0]}={vec[a]}' for a in ASPECTS)}")
        print(f"   RATING : {score} / 5.0   ({label(score)})\n")

    print("=== sanity check (face validity) ===")
    for name, v in {
        "all excellent": {a: 0.9 for a in ASPECTS},
        "bad food (veto)": {"Food Quality": 0.1, "Cleanliness": 0.8, "Menu Variety": 0.8, "Service Speed": 0.8},
        "all average": {a: 0.5 for a in ASPECTS},
    }.items():
        s = rate(v, system, ants)
        print(f"   {name:18}: {s} / 5.0 ({label(s)})")
