# Feasibility (2-day hackathon) + advance-prep plan

## Honest verdict

The full plan — Steps 1–9, **both** signature sets, classifier+entropy, the ruler battery,
pseudobulk DE with held-out circularity splits, plasticity, the bonus enrichment, plus figures,
write-up and the talk — is **too much to *build* during the two days**. It *is* achievable in two
days **only if the code is finished and dry-run on the real data beforehand**, so the hackathon is
*run → judge → interpret → present*, not *build → debug*. Walk in with today's stubs and it will not
finish.

So we do **not** shrink the science. We move all the *engineering* and de-risking to **now**, and
keep the **scientific judgment** for the live event.

## What "advance" vs "live" should mean

- **ADVANCE (now — hand to Claude Code):** every deterministic piece of plumbing — code-complete and
  tested on the *real* data so nothing crashes live.
- **LIVE (the two days):** the calls that actually need judgment — does the ruler validate? which
  set leads? is the weak arm real? what does the collapse mean? — plus robustness, interpretation,
  figures, write-up, talk.

> Norm check: if the course expects the *analysis itself* to be produced during the event, stop the
> advance work at "code complete + smoke-tested on a small subset" — don't commit the final result
> numbers ahead of time. The engineering de-risking is fair game either way.

## Component status (what's real vs stub)

| Component | Where | Status | Advance action |
|---|---|---|---|
| Paper 1 → `processed` (counts.mtx) | `data/processed/paper1/` | ✅ done | none |
| `paper2_train.npz` (union ~1700) | `prep/02_convert_paper2_mat.py` | code done, **not run** | **run once** (needs raw `.mat`); verify ~1700 feats |
| Step 2 load/QC | `pipeline.load` | done, smoke only | real-data run (watch ~8–12 GB `mmread`) |
| Step 3 harmonize | `steps/step3` | partial (pipeline inlines it) | confirm mapping ≥80% on real genes |
| Step 4a score (multi-set, per-arm std) | `pipeline.score` | ✅ just upgraded | test both sets run |
| Step 4b classifier + entropy | `classifier.py` | **scaffold**, `RUN_CLASSIFIER=False` | **INTEGRAL — finish + test** on Paper-2 split, calibrate, apply to P1 (entropy meter) |
| Step 5 validation gate (both sets) | `pipeline.validate` | basic | extend to both sets + entropy; **pre-run** so you know the ruler works |
| Step 5b ruler battery | — | **described only, not coded** | implement coherence / anti-corr / split-half + test |
| Step 6 collapse (H1) | `pipeline.collapse` | ✅ done, multi-set | test on real data |
| Step 7 zone-DE (H2) + held-out splits | `pipeline.de` | basic; **K-split loop not implemented** | implement repeated held-out split; test (heavy) |
| Step 8 plasticity (H3) | `pipeline.plasticity` | basic | test |
| Step 9 bonus enrichment | `steps/step9` | stub | **optional — cut first if short** |
| Plotting | `plotting/artefacts.py` | scaffold | make each fig fn run on real outputs |
| `run_all` driver | `run_all.py` | ready | wire multi-set loop + classifier flag |

## Advance-prep checklist (do NOW; this is the Claude Code task list)

1. **Run `prep/02_convert_paper2_mat.py`** → `paper2_train.npz` (union ~1700). Verify the printed
   feature count and zone-label balance.
2. **Full real-data dry-run of `pipeline.py` end-to-end, for BOTH sets.** Fix every crash and memory
   issue. *Biggest risks:* `scipy.io.mmread` memory on the real matrix, and the DE step's runtime.
3. **Pre-run and SAVE the Step 5 / 5b validation result for both sets** — so you walk in *knowing*
   the ruler works and which set validates better. This removes the single scariest live unknown.
4. **Implement + test the two real gaps:** Step 5b ruler battery, and Step 7's repeated held-out
   gene split (the H2 circularity guard).
5. **Finish + test the classifier+entropy — INTEGRAL, not optional.** Train on Paper-2 union
   features, calibrate, evaluate on a held-out Paper-2 split (must beat chance), apply to Paper 1,
   compute per-cell entropy. The entropy meter is an independent de-zonation signal central to the
   project — it ships in the headline, not as a cut-if-short extra.
6. **Make `plotting/artefacts.py` produce every figure** from real pipeline outputs.
7. **Smoke `run_all` on a cell subset** so the live "go" is a single command.

## Two-day live schedule (priority ladder)

- **Day 1 AM** — run the full pipeline (both sets) on real data; **pass the Step 5 gate**; resolve
  the weak arm if it shows.
- **Day 1 PM** — **H1 collapse** curve (coordinate spread + PC–PP anti-correlation **+ classifier
  entropy**) + Spearman/JT + donor bootstrap CI + permutation null. Lock the headline. *(MUST-HAVE.)*
- **Day 2 AM** — **H2 zone-DE** + held-out circularity. *(SHOULD-HAVE.)*
- **Day 2 PM** — **H3 plasticity** *(nice-to-have)* or the bonus; finalize figures; write-up + slides.

**Deliverable ladder — if time runs short, cut from the bottom:**
- **MUST:** H1 collapse on a *validated* ruler (both sets), **including the classifier+entropy
  de-zonation signal** — the classifier is integral, not droppable.
- **SHOULD:** H2 — which programs collapse.
- **NICE:** H3 plasticity, Step 9 bonus enrichment.

Labour split: see `docs/plan/WORK_DIVISION.md`. One person drives the run/validation/H1 spine; the other
builds H2/H3 + plotting in parallel against the smoke-tested pipeline.
