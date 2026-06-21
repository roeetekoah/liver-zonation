# Prompt for Claude Code — MINIMAL advance prep (data + environment only)

Copy everything below the line into a fresh Claude Code session at the repo root
(`D:\CS\Genomics\Hackathon`).

---

You are doing **minimal advance prep** for a 2-day computational-genomics hackathon. Scope is
deliberately small on purpose: get the **data cached** and the **environment proven to run**, so day 1
isn't lost to downloads, parsing, or dependency errors. **Do NOT do the analysis.** The substantive
work — completing the classifier, the validation gate, H1/H2/H3, plotting, and all interpretation —
happens **live during the hackathon** (we'll have Claude Code then too), and that's where the credit
is. Do not produce or commit result numbers.

**Read first (for context):** `CLAUDE.md`, `PROJECT_MAP.md`, `FEASIBILITY_AND_PREP.md`,
`docs/plan/IMPLEMENTATION_PLAN.pdf`, `data/README.md`, `src/config.py`, `src/pipeline.py`.

**Constraints to respect even in prep:** the **donor** is the unit of inference; the pipeline runs
**both sets** in `config.SETS_TO_COMPARE`; the classifier is **integral** (but you are NOT finishing
it now).

**Tasks — do these, then STOP:**

1. **Finish the repo-reorg housekeeping.** The assistant already moved planning prose to `docs/plan/`,
   archived superseded renders to `archive/`, and fixed cross-references. You only need to: delete the
   junk it couldn't (`src/__pycache__/`, `presentation/.~lock.*#`, any `~$*`); add those +
   `*.aux/.log/.out/.toc` + `counts.npz` to `.gitignore` if missing; then
   `git add -A && git commit -m "repo reorg + prep setup"`. *Acceptance:* `git status` clean,
   `import pipeline` works.

2. **Environment.** Create/confirm a Python env with `numpy scipy pandas scikit-learn statsmodels
   matplotlib h5py openpyxl`; R side `Seurat`, `Matrix`. Confirm `python -c "import pipeline"` runs
   from `src/`. Record Python + package versions in a new `PREP_LOG.md`.

3. **Build the data caches** (needs the raw files in `data/raw/` — download per `data/README.md`
   first if absent):
   - `Rscript src/prep/01_extract_paper1_hepatocytes.R`  → `data/processed/paper1/` (if absent)
   - `python src/prep/00_mtx_to_npz.py`                  → `counts.npz` (fast/low-memory loads)
   - `python src/prep/02_convert_paper2_mat.py`          → `paper2_train.npz` (union ~1,700 feats)
   *Acceptance:* `counts.npz` and `paper2_train.npz` exist; the npz step prints ~1,700 features and
   3 reasonably-balanced zone classes.

4. **Subset smoke test — "does it RUN," not "what does it find."** Run `pipeline.py` on a small
   subset (cap to ~20 donors or the first ~20k cells) end-to-end for BOTH sets. The ONLY goal is that
   it executes start→finish and writes `coordinates_*`/`collapse_*` outputs without crashing and
   within memory. Fix only crashes / memory / shape bugs. **Do not tune, interpret, or treat any
   number as a result; delete the subset outputs afterward.** Log peak memory + runtime in
   `PREP_LOG.md`.

5. **Report and STOP.** Summarize: what's cached, env versions, that the subset smoke passed, and any
   crash you fixed. Do **not** proceed to the validation gate, the classifier, H1/H2/H3, or plotting.

**Explicitly deferred to the hackathon** (do NOT do now): the real healthy-validation / go-no-go
feasibility check (pending the professor's OK), the classifier + entropy, Step 5/5b, H1/H2/H3, the
held-out DE splits, plotting, and all interpretation.
