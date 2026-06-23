# F12 — Why the z-scored relative ruler is abandoned, even biopsy-only (the meta-analysis)

**Status: LIVE (methodological finding).** This was discussed but never written down — closing the gap.
There are **two separate** reasons the legacy z-scored zonation ruler (z(PC)−z(PP) coordinate; collapse read
off its spread / anti-correlation) was replaced by the count-based scenario taxonomy. Dropping healthy +
end-stage fixes only the first.

## Reason 1 — the tissue-source confound (fixed by exclusion)
Pooling healthy (deceased-donor) + end-stage (explant) with biopsies put the dramatic "collapse" signal in
the confounded explant tissue. **Dropping those groups removes most of the apparent collapse** (this is the
single biggest fix; it is also a Simpson/aggregation effect — see `legacy_simpson.py`, the pooled
anti-correlation that reverses sign on aggregation).

## Reason 2 — the ruler has an INTRINSIC problem that survives the exclusion
Even biopsy-only, the z-scored relative ruler is **strictly weaker**, for two reasons:
1. **Depth- and cell-number-sensitive.** Each program is standardized to mean-0/unit-variance *across the
   cells in the dataset*, and "collapse" is read off the **spread / anti-correlation** of the resulting
   coordinate. F4 biopsies run shallower and donors have different cell counts — both change the spread for
   **non-biological** reasons. So a biopsy-only ruler can still show a "spread change" that is depth, not
   de-zonation.
2. **It conflates mechanisms.** Turn-off, de-zonation (co-expression), *and* noise all shrink the
   coordinate's spread — the ruler **cannot tell them apart**. This is the whole reason we replaced it with
   the **scenario taxonomy**, which *does* separate depletion vs dimming vs co-expression vs turn-off (F9).

## Empirical confirmation
The biopsy-only relative view gave a weak apparent "detox drift" (66 → 49 on the relative metric) that, when
checked, was **within-donor spread noise** and **did not survive the count anchor-classification** (the same biopsy donors
show nothing structural; and the detox story is dropped — D2). So you would have to validate any ruler
signal with count-based numbers anyway.

## Conclusion
The biopsy-only z-ruler is **not invalid — just indirect, depth-sensitive, and mechanism-conflating**. The
trustworthy, mechanism-specific instrument is the **count anchor-classification on down-thinned-to-B counts**, not the
relative ruler. (This is the "we changed the measurement" point, made precise.)
