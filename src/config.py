"""Central path config. Import as: from config import PAPER1, SIGNATURES, ...
Run scripts from the src/ directory, or ensure src/ is on sys.path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root (Hackathon/)
DATA_RAW   = ROOT / "data" / "raw"
DATA_PROC  = ROOT / "data" / "processed"
PAPER1     = DATA_PROC / "paper1"                        # counts.mtx, genes.txt, barcodes.txt, *_metadata.csv
PAPER2_TRAIN = DATA_PROC / "paper2_train.npz"
SIGNATURES = ROOT / "signatures"
# ---- signature sets (pericentral, periportal) ----------------------------------------
# PRIMARY = "full": the transcriptome-wide zonation program (~1,640 significantly-zonated
# hepatocyte genes from Paper 2, q<0.05). This matches the project's motivation — read
# position from the WHOLE program, not a few markers. The smaller sets are alternatives:
#   full           ~1273 + 364   transcriptome-wide PRIMARY (default)
#   expanded       ~102 + 91      mid-size (landmark + core + top-ranked)
#   core           13 + 8         curated, biology-informed anchors
#   paper2_landmark 20 + 20       EXACT Paper 2 landmark set (sanity baseline)
#   sensitivity    (PP only, 7)   core periportal minus inflammation genes
SIGNATURE_SETS = {
    name: (SIGNATURES / f"pericentral_{name}.txt", SIGNATURES / f"periportal_{name}.txt")
    for name in ("full", "expanded", "core", "paper2_landmark")
}
DEFAULT_SET = "full"
# The analysis REPORTS BOTH as a comparison (decision): the exact Paper 2 landmark set
# (faithful to the original plan) and the full transcriptome-wide program. Run every result
# for both and present them side by side; agreement is itself evidence the signal is robust.
SETS_TO_COMPARE = ["paper2_landmark", "full"]
def signature_files(which: str = DEFAULT_SET):
    """Return (pericentral_path, periportal_path) for a named set; default = transcriptome-wide 'full'."""
    return SIGNATURE_SETS[which]
PC_GENES, PP_GENES = SIGNATURE_SETS[DEFAULT_SET]   # transcriptome-wide by default
RESULTS    = ROOT / "results"
FIGURES    = RESULTS / "figures"
TABLES     = RESULTS / "tables"
for _d in (FIGURES, TABLES):
    _d.mkdir(parents=True, exist_ok=True)
