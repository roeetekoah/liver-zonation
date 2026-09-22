"""Run the bounded, portfolio-facing analysis route in a fresh output tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_INPUTS = (
    "processed/paper1/raw_panel_counts.csv",
    "processed/paper1/metadata_all_cells.csv",
    "processed/paper1/counts.npz",
    "processed/paper1/genes.txt",
    "processed/paper1/barcodes.txt",
    "processed/paper1/pseudobulk_hep_by_donor.csv",
    "processed/paper1/donor_meta.csv",
)

STEPS = (
    ("01_raw_count_sanity", (sys.executable, "src/prep/06_sanity_raw.py")),
    ("02_batch_inventory", (sys.executable, "src/confound/batch_qc.py")),
    ("03_donor_metrics", (sys.executable, "src/census/load_bearing.py")),
    ("04_equivalence", (sys.executable, "src/confound/equivalence_bound.py")),
    ("05_detection_limits", (sys.executable, "src/confound/mde.py")),
    ("06_genomewide_trend", (sys.executable, "src/dge/dge_genomewide.py")),
    ("07_plan_a", ("Rscript", "src/dge/plan_a_genomewide.R")),
    ("08_camera", ("Rscript", "src/dge/geneset_camera.R")),
    ("09_geneset_controls", ("Rscript", "src/dge/geneset_verify.R")),
    ("10_within_pc_detox", (sys.executable, "src/dge/geneset_verify_test4.py")),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True,
                        help="Directory containing raw/ and processed/ (large files stay outside Git).")
    parser.add_argument("--output-root", type=Path, required=True,
                        help="New or empty directory for this run. Existing outputs are rejected.")
    args = parser.parse_args()
    data_root = args.data_root.expanduser().resolve()
    output_root = args.output_root.expanduser().resolve()

    missing = [str(data_root / rel) for rel in REQUIRED_INPUTS if not (data_root / rel).is_file()]
    if missing:
        raise SystemExit("Missing required processed inputs:\n  " + "\n  ".join(missing))
    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"Output directory is not empty: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    log_dir = output_root / "logs"
    log_dir.mkdir()

    env = os.environ.copy()
    env["LIVER_ZONATION_DATA_ROOT"] = str(data_root)
    env["LIVER_ZONATION_RESULTS_ROOT"] = str(output_root)
    records = []
    for label, command in STEPS:
        print(f"[{label}] {' '.join(command)}", flush=True)
        run = subprocess.run(command, cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (log_dir / f"{label}.log").write_text(run.stdout, encoding="utf-8")
        records.append({"step": label, "command": list(command), "exit_code": run.returncode})
        if run.returncode:
            print(run.stdout)
            raise SystemExit(f"Step failed: {label}; see {log_dir / (label + '.log')}")

    head = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(("git", "status", "--porcelain"), cwd=ROOT))
    manifest = {
        "repository": str(ROOT),
        "git_head": head,
        "working_tree_dirty": dirty,
        "python": platform.python_version(),
        "data_root": str(data_root),
        "output_root": str(output_root),
        "inputs": {rel: sha256(data_root / rel) for rel in REQUIRED_INPUTS},
        "steps": records,
    }
    manifest["outputs"] = {
        str(path.relative_to(output_root)): sha256(path)
        for path in sorted(output_root.rglob("*")) if path.is_file()
    }
    (output_root / "run-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Verified route completed. Manifest: {output_root / 'run-manifest.json'}")


if __name__ == "__main__":
    main()
