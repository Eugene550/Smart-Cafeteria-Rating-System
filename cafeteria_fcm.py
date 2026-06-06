"""
Smart Cafeteria Rating System — Stage 2 (data-driven): pooling + Fuzzy C-Means

Two jobs:
  (A) Pool each cafeteria's review scores into one averaged vector  ->  the inputs
      the FIS will rate.  An aspect mentioned by NO review falls back to Medium (0.5).
  (B) Run FCM (per aspect, 1-D) across ALL reviews to learn where Low/Medium/High
      sit. The three cluster centres become the PEAKS of that aspect's triangular
      membership functions. This is the data-driven half of the hybrid.

FCM runs on all reviews pooled (not per cafeteria) so the Low/Medium/High scale is
learned once and shared by every cafeteria. Lestari's 6 reviews are too few to
cluster alone, but fine when the scale is learned from all 41.
"""

import numpy as np
import skfuzzy as fuzz
from cafeteria_frontend import (
    load_lexicon, build_analyzer, load_reviews_csv, score_dataframe, ASPECTS,
)

SEED = 42          # fixed seed -> reproducible clusters (important for the viva)
N_CLUSTERS = 3     # Low / Medium / High


def learn_membership_functions(scored):
    """Per aspect: 1-D FCM on all review scores -> 3 sorted centres -> triangular MFs.
    Returns {aspect: {"peaks": [c0,c1,c2], "Low":(a,b,c), "Medium":..., "High":..., "fpc": x}}."""
    result = {}
    for a in ASPECTS:
        data = scored[a].dropna().to_numpy(dtype=float)
        cntr, u, _, _, _, _, fpc = fuzz.cluster.cmeans(
            data.reshape(1, -1), c=N_CLUSTERS, m=2.0,
            error=0.005, maxiter=1000, seed=SEED)
        c0, c1, c2 = sorted(cntr.ravel())
        result[a] = {
            "peaks": [round(c0, 3), round(c1, 3), round(c2, 3)],
            "Low":    (0.0, c0, c1),     # left shoulder at the lowest centre
            "Medium": (c0, c1, c2),      # middle triangle
            "High":   (c1, c2, 1.0),     # right shoulder at the highest centre
            "fpc":    round(fpc, 3),     # cluster-validity (closer to 1 = cleaner)
            "n":      len(data),
        }
    return result


def cafeteria_vectors(scored):
    """Average each cafeteria's reviews per aspect. Returns {cafeteria: {aspect: score, ...}}
    plus a record of which aspects fell back to Medium (no mentions at all)."""
    vectors, fallbacks = {}, {}
    for caf, grp in scored.groupby("cafeteria"):
        vec, miss = {}, []
        for a in ASPECTS:
            vals = grp[a].dropna()
            if len(vals) == 0:
                vec[a] = 0.5          # Medium fallback only when nobody mentioned it
                miss.append(a)
            else:
                vec[a] = round(float(vals.mean()), 3)
        vectors[caf] = vec
        fallbacks[caf] = miss
    return vectors, fallbacks


if __name__ == "__main__":
    LEX = "Variable_and_keywords_refined.xlsx"
    CSV = "reviews_clean.csv"

    matching, vu = load_lexicon(LEX)
    sia = build_analyzer(vu)
    scored = score_dataframe(load_reviews_csv(CSV), sia, matching, vu)

    print("=== (B) Membership functions learned by FCM (per aspect) ===")
    mfs = learn_membership_functions(scored)
    for a, m in mfs.items():
        print(f"\n{a}  (n={m['n']} reviews, FPC={m['fpc']})")
        print(f"   Low / Medium / High centres : {m['peaks']}")
        print(f"   Low    triangle : ({m['Low'][0]:.2f}, {m['Low'][1]:.3f}, {m['Low'][2]:.3f})")
        print(f"   Medium triangle : ({m['Medium'][0]:.3f}, {m['Medium'][1]:.3f}, {m['Medium'][2]:.3f})")
        print(f"   High   triangle : ({m['High'][0]:.3f}, {m['High'][1]:.3f}, {m['High'][2]:.2f})")

    print("\n=== (A) Per-cafeteria averaged input vectors (go into the FIS) ===")
    vectors, fallbacks = cafeteria_vectors(scored)
    for caf, vec in vectors.items():
        print(f"\n{caf}")
        for a in ASPECTS:
            print(f"   {a:14}: {vec[a]}")
        if fallbacks[caf]:
            print(f"   (Medium fallback, no mentions: {', '.join(fallbacks[caf])})")
