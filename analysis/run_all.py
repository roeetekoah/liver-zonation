#!/usr/bin/env python3
"""
run_all.py — prep-day driver / orchestrator.

Runs the baseline pipeline (primer Phases/Steps 2-8) in order, then optionally the
zone classifier (Step 4b). This is PLUMBING only: it wires the pieces together and
checks inputs. The scientific decisions — the Phase-5 validation gate, which collapse
metric to trust, and fixing the weak pericentral arm — are meant to happen LIVE during
the hackathon, not be pre-baked here.

Usage (from the Hackathon folder):   python analysis/run_all.py
Edit CONFIG below first.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- CONFIG ----------------
RUN_CLASSIFIER = False   # set True once the Paper-2 training set (Phase 0/1c) exists
# ----------------------------------------

REQUIRED = [
    "paper1/counts.mtx", "paper1/genes.txt", "paper1/barcodes.txt",
    "paper1/cell_metadata.csv", "paper1/metadata_all_cells.csv",
    "pericentral_genes.txt", "periportal_genes.txt",
]

def banner(t):
    print("\n" + "=" * 66 + f"\n  {t}\n" + "=" * 66, flush=True)

def check_inputs():
    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(HERE, f))]
    if missing:
        sys.exit("Missing required inputs:\n  " + "\n  ".join(missing))
    if RUN_CLASSIFIER and not os.path.exists(os.path.join(HERE, "paper2_train.npz")):
        print("WARNING: RUN_CLASSIFIER=True but paper2_train.npz not found — "
              "run Phase 0/1c (convert_paper2_mat + make_training_labels) first.")
    print("All required baseline inputs present.")

def main():
    t0 = time.time()
    sys.path.insert(0, HERE)

    banner("Phase 0 — checking inputs")
    check_inputs()

    banner("Phases 2-8 — baseline scoring pipeline (pipeline.py)")
    print("  Steps: load -> normalize -> score -> validate(5) -> ruler(5b) "
          "-> collapse(6) -> DE+FDR(7) -> plasticity(8)")
    print("  NOTE: Step 5 is a GATE — if healthy validation fails, stop and fix scoring.\n")
    import pipeline
    pipeline.main()

    if RUN_CLASSIFIER:
        banner("Phase 4b — zone classifier + entropy (classifier_step.py)")
        import classifier_step
        classifier_step.main()
    else:
        banner("Phase 4b — classifier SKIPPED (set RUN_CLASSIFIER=True to enable)")

    banner(f"DONE in {time.time() - t0:.0f}s")
    outdir = os.path.join(HERE, "out")
    if os.path.isdir(outdir):
        print("Artefacts written to analysis/out/:")
        for f in sorted(os.listdir(outdir)):
            print("  " + f)

if __name__ == "__main__":
    main()
