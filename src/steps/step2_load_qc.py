"""Step 2 — load Paper 1 hepatocytes + donor + libsize + QC gate (Artefact A2)."""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd, scipy.io, scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, _is_na, OUT, STAGE_ORDER, DONOR_COLS


def load_qc(paper1_dir=None, donor_cols=tuple(DONOR_COLS)):
    """Load the Paper 1 hepatocyte count matrix, metadata, donor IDs and library sizes,
    and write the A2 per-(stage,donor) cell-count table — failing loudly if the donor
    column (the unit of inference) is missing or unusable.

    Inputs
      paper1_dir : data/processed/paper1/ (default config.PAPER1).
      donor_cols : candidate donor/patient-ID column names (first hit wins).
    Outputs
      M (genes x cells CSC), genes[], barcodes[], stage[], donor[], libsize[].
    Artefact A2
      results/tables/qc_counts.csv with columns {stage, donor, n_cells}.
    Gates (hard)
      donor column must exist, not be all-NA, and resolve >=2 donors; unknown stage
      labels (outside STAGE_ORDER) are warned about.
    """
    P1 = str(paper1_dir or config.PAPER1)
    log("Step 2: load Paper 1 hepatocytes + QC gate ...")
    # Prefer the compact binary cache (prep/00_mtx_to_npz.py) — fast load, low peak memory.
    npz = os.path.join(P1, "counts.npz")
    if os.path.exists(npz):
        M = sp.load_npz(npz).tocsc()
    else:
        log("  (counts.npz not found — parsing counts.mtx; run prep/00_mtx_to_npz.py to speed this up)")
        M = scipy.io.mmread(os.path.join(P1, "counts.mtx")).tocsc()
    genes = np.array([g.strip() for g in open(os.path.join(P1, "genes.txt"))])
    bars  = np.array([b.strip() for b in open(os.path.join(P1, "barcodes.txt"))])
    meta  = pd.read_csv(os.path.join(P1, "cell_metadata.csv")).set_index("cell_id").reindex(bars)
    stage = meta["stage"].astype(str).values
    # metadata_all_cells.csv has mixed-type columns (Patient.ID etc.) -> low_memory=False
    allm  = pd.read_csv(os.path.join(P1, "metadata_all_cells.csv"), low_memory=False).set_index("cell_id")
    dcol  = next((c for c in donor_cols if c in allm.columns), None)
    # ---- donor gate: a valid donor column is REQUIRED (unit of inference = donor) ----
    if dcol is None:
        raise SystemExit(
            "Step 2 FAILED: no donor column found in metadata_all_cells.csv. "
            f"Looked for {list(donor_cols)}. Donor is the unit of inference — cannot proceed.")
    donor = allm[dcol].astype(str).reindex(bars).values
    na_donor = _is_na(donor)
    n_donor = int(pd.unique(donor[~na_donor.values]).size)
    if na_donor.all():
        raise SystemExit(f"Step 2 FAILED: donor column '{dcol}' is all-NA for hepatocyte cells.")
    if n_donor < 2:
        raise SystemExit(f"Step 2 FAILED: only {n_donor} donor(s) resolved from '{dcol}'; "
                         "donor-level inference needs >=2 donors.")
    if na_donor.any():
        log(f"  WARNING: {int(na_donor.sum())} cells have NA donor (will be dropped downstream).")
    # ---- stage gate: warn loudly on labels outside STAGE_ORDER ----
    unknown = sorted(set(np.unique(stage)) - set(STAGE_ORDER))
    if unknown:
        log(f"  WARNING: stage labels not in STAGE_ORDER (excluded from ranked trends): {unknown}")
    # ---- QC counts (A2): per-(stage, donor) ----
    qc = pd.DataFrame({"stage": stage, "donor": donor})
    qc = qc[~_is_na(qc["donor"]).values]
    per = (qc.groupby(["stage", "donor"]).size().reset_index(name="n_cells")
             .sort_values(["stage", "donor"]))
    per.to_csv(os.path.join(OUT, "qc_counts.csv"), index=False)
    log(f"  donor column = {dcol}; {n_donor} donors, {len(bars)} cells")
    log(f"  cells / stage : { {s: int((stage==s).sum()) for s in np.unique(stage)} }")
    log(f"  donors / stage: { qc.groupby('stage')['donor'].nunique().to_dict() }")
    log(f"  wrote {os.path.join(OUT, 'qc_counts.csv')} ({len(per)} donor x stage rows)")
    libsize = np.asarray(M.sum(0)).ravel()
    return M, genes, bars, stage, donor, libsize
