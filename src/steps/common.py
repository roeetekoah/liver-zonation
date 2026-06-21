"""Shared helpers + analysis constants for the step modules (Steps 2-8).

This is the single home for the small utilities and project-wide constants the steps
share, so no step module re-defines them. Paths still come from config.py; this module
only adds the *analysis* vocabulary (stage order, marker sets) and stats helpers.
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
import config

# Windows consoles default to cp1252 and crash on non-ASCII log output (arrows, em-dashes).
# Force UTF-8 so a print() never kills the pipeline mid-run during the live event.
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

try:
    from statsmodels.stats.multitest import multipletests
    import statsmodels.formula.api as smf
except Exception:
    multipletests = None; smf = None

OUT = str(config.TABLES); os.makedirs(OUT, exist_ok=True)


def set_dir(which):
    """Per-set output subdir results/tables/<which>/ (created on demand). Per-set result
    tables live here (validation.csv, ruler_diagnostics.csv, ...); global tables stay in OUT."""
    d = os.path.join(OUT, str(which))
    os.makedirs(d, exist_ok=True)
    return d

# ---- analysis vocabulary (the disease axis + the marker / plasticity panels) ----
STAGE_ORDER = ["Healthy control", "NAFLD", "NASH w/o cirrhosis", "NASH with cirrhosis", "end stage"]
SHORT = ["Healthy", "NAFLD", "NASH", "Cirrhosis", "End-stage"]
S2R = {s: i for i, s in enumerate(STAGE_ORDER)}          # stage label -> ordinal rank
PLAST = ["KRT7", "KRT19", "SOX9", "SOX4", "KRT23", "NCAM1"]
VAL = {"pericentral": ["CYP2E1", "CYP1A2", "GLUL", "PCK2"],   # PCK2 is pericentral in HUMANS
       "periportal":  ["ASS1", "ALDOB", "PCK1", "HAL"]}
DONOR_COLS = ["Patient.ID", "patient", "donor", "orig.ident", "sample"]


def log(m):
    """Flush-on-write print so live logs appear immediately."""
    print(m, flush=True)


def bh(p):
    """Benjamini-Hochberg FDR. Uses statsmodels if available, else a pure-numpy fallback."""
    p = np.asarray(p, float)
    if multipletests is not None:
        return multipletests(np.nan_to_num(p, nan=1.0), method="fdr_bh")[1]
    n = len(p); o = np.argsort(p); q = np.empty(n)
    q[o] = np.minimum.accumulate((p[o] * n / np.arange(n, 0, -1))[::-1])[::-1]
    return np.clip(q, 0, 1)


def _is_na(v):
    """True where a donor/stage string is missing-like ('nan','NA','None','')."""
    s = pd.Series(v).astype(str).str.strip()
    return s.isin(["", "nan", "NaN", "NA", "None", "<NA>"])
