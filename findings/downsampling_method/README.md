# Methods — the binomial down-thinning depth control (definition, citations, limitations)

**Status: LIVE (methods documentation).** This is the depth control used throughout; previously written
with the vague shorthand "depth-matched" — that shorthand is **banned in findings/figures**; use the
precise definition below.

## Precise definition
Each nucleus has a raw library size `E_raw` (total RNA-assay UMIs, ~920–49,854). A deeper-sequenced
nucleus detects more genes purely by sampling more molecules, so "fraction expressing" or "co-expression"
rises with depth as a pure artifact. To remove it we **down-thin every nucleus to a common budget B**:
- pick budget **B = 1,500 UMIs**;
- for each nucleus with `E_raw ≥ B`, retain each observed molecule independently with probability
  **p = B / E_raw** (a **binomial** draw per gene: `Binom(count, p)`);
- nuclei with `E_raw < B` are **dropped** (~5%);
- repeat over **8 independent draws** and average (Monte-Carlo, to reduce draw variance).
After this every kept nucleus has ~the same total, so detection/count differences reflect biology, not
depth. It is purely count-based — **no ratios, no normalization**. Robustness: re-run at **B ∈ {1000,1500,3000}**
(conclusions unchanged).

## Citations (verified)
- **DropletUtils** `downsampleMatrix` — Lun ATL, McCarthy DJ, et al., Bioconductor (binomial downsampling
  of counts to equalize depth).
- **Amezquita RA, Lun ATL, Becht E, et al.** "Orchestrating single-cell analysis with Bioconductor."
  *Nature Methods* 17, 137–145 (2020) — downsampling for depth normalization (OSCA).
- **10x Genomics** `cellranger aggr --normalize=mapped` — standard production subsampling to equal median
  reads/cell before comparison. (Zheng et al., *Nat Commun* 2017 — 10x platform — to be exact-cited via web.)

## Limitations / possible biases it introduces (for Methods)
1. **Data loss / discard bias:** ~5% of nuclei (those below B) are dropped; they are systematically the
   lowest-depth nuclei. We checked the discard is depth-driven and not PC-biased (`load_bearing.py` §4), but
   if depth correlated with a cell STATE the dropped subset could carry residual confounding.
2. **Information loss / floor:** thinning to a low B discards molecules, lowering detection power for sparse
   genes (e.g. GLUL becomes even sparser) — a detection floor that can mask subtle within-cell changes.
3. **Does NOT fix ambient RNA:** thinning equalizes depth, not soup; ambient contamination is a separate
   control (the ≥2-UMI ambient-robust threshold; F8).
4. **Model assumption:** binomial thinning treats observed UMIs as a fair subsample of a fixed latent total
   (technical sampling); it does not model biological overdispersion or per-gene capture-efficiency
   differences.
5. **Averaged draws are not integers:** the 8-draw mean is a smoothed quantity, not a literal count.
6. **B is a tradeoff:** lower B keeps more cells but less signal; higher B the reverse. B=1500 is below the
   lowest per-donor median depth (keeps most cells).
