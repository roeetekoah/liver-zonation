"""Central path config. Import as: from config import PAPER1, SIGNATURES, ...
Run scripts from the src/ directory, or ensure src/ is on sys.path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root (Hackathon/)
DATA_RAW   = ROOT / "data" / "raw"
DATA_PROC  = ROOT / "data" / "processed"
PAPER1     = DATA_PROC / "paper1"                        # counts.mtx, genes.txt, barcodes.txt, *_metadata.csv
PAPER2_TRAIN = DATA_PROC / "paper2_train.npz"
SIGNATURES = ROOT / "signatures"
# BASELINE = the EXACT Paper 2 hepatocyte landmark set (the genes Paper 2 used to anchor
# the porto-central axis). This is the default the pipeline scores with. Swap to
# *_core.txt (curated), *_expanded.txt (ranked), or *_sensitivity.txt for robustness.
PC_GENES   = SIGNATURES / "pericentral_paper2_landmark.txt"
PP_GENES   = SIGNATURES / "periportal_paper2_landmark.txt"
RESULTS    = ROOT / "results"
FIGURES    = RESULTS / "figures"
TABLES     = RESULTS / "tables"
for _d in (FIGURES, TABLES):
    _d.mkdir(parents=True, exist_ok=True)
