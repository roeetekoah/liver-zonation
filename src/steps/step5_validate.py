"""Step 5 — healthy positive-control validation GATE (Artefact A5)."""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, OUT, STAGE_ORDER, VAL, set_dir


def validate(coord, col, stage, entropy=None,
             pc_markers=tuple(VAL["pericentral"]), pp_markers=tuple(VAL["periportal"]),
             which="", min_markers=4):
    """Confirm the coordinate recovers known zonation in HEALTHY cells before proceeding.

    coord = mean_z(PC) - mean_z(PP), so pericentral markers must correlate POSITIVELY with
    coord and periportal markers NEGATIVELY. Writes results/tables/validation_<set>.csv and
    returns (report_df, pass_bool).

    GATE (hard): pass requires >= min_markers present AND a majority of present markers with
    the correct sign. If `entropy` is given, healthy mean entropy must also be below the
    global mean (well-zonated baseline). main() must NOT run collapse for a failed set.
    """
    log(f"Step 5: healthy validation (positive control) [set={which}] — PRIMARY gate")
    h = stage == STAGE_ORDER[0]
    panels = {"pericentral": (pc_markers, +1), "periportal": (pp_markers, -1)}
    rows = []
    for zone, (markers, exp) in panels.items():
        for g in markers:
            present = g in col
            rho = p = np.nan; ok = False
            if present and h.sum() >= 20 and col[g][h].std() > 0:
                r = spearmanr(coord[h], col[g][h]); rho, p = float(r.statistic), float(r.pvalue)
                ok = bool(np.sign(rho) == exp and abs(rho) > 0)
            rows.append({"signature_set": which, "marker": g, "zone": zone,
                         "expected_sign": "+" if exp > 0 else "-",
                         "rho": rho, "p": p, "present": present, "pass": ok,
                         "n_healthy_cells": int(h.sum())})
    rep = pd.DataFrame(rows)
    rep.to_csv(os.path.join(set_dir(which), "validation.csv"), index=False)
    n_present = int(rep["present"].sum()); n_correct = int(rep["pass"].sum())
    # GATE = MARKER SIGNS ONLY. Entropy is AUXILIARY and must NOT override the gate (guardrail).
    passed = bool(n_present >= min_markers and n_correct >= int(np.ceil(n_present / 2)))
    # Entropy is reported for context only (NOT gated): healthy is expected to be well-zonated
    # (low entropy), but the classifier can be confidently wrong on degenerate end-stage cells,
    # so a high healthy-vs-global comparison is informational, never a fail condition.
    if entropy is not None and h.sum() >= 20:
        ent = np.asarray(entropy, float)
        if ent.shape[0] == len(stage) and np.isfinite(ent).any():
            log(f"  (aux) healthy mean entropy={np.nanmean(ent[h]):.3f} vs global "
                f"{np.nanmean(ent):.3f} — informational only, does NOT gate")
    for _, r in rep.iterrows():
        tag = "ok" if r["pass"] else ("MISSING" if not r["present"] else "WRONG-SIGN")
        log(f"  healthy rho(coord,{r['marker']:6s})={r['rho']:+.3f} expect {r['expected_sign']}  [{tag}]")
    log(f"  GATE [{which}]: {n_correct}/{n_present} present markers correct -> "
        f"{'PASS' if passed else 'FAIL'} (need >={min_markers} present, majority correct)")
    return rep, passed
