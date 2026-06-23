# MASLD hepatocyte zonation & plasticity — re-analysis

A graduate-hackathon re-analysis of the single-nucleus RNA-seq evidence in **Gribben et al., Nature 2024**
("Acquisition of epithelial plasticity in human chronic liver disease"; GSE202379), which reported that
hepatocytes progressively lose zonation and transdifferentiate toward cholangiocytes in MASLD.

**Conclusion in one line:** in acquisition-matched needle-biopsy tissue, hepatocyte transcriptional zonation
is *preserved*; the apparent progressive de-zonation is largely a tissue-source/sampling confound, and the only
other genome-wide signal is a small biliary-marker burden most consistent with cholangiocyte ambient RNA +
rare mixed/doublet nuclei, not widespread transdifferentiation.

## Start here
- **[`reports/FULL_STORY.txt`](reports/FULL_STORY.txt)** — the full narrative, end to end.
- **[`FINDINGS.md`](FINDINGS.md)** — the story-ordered summary with key numbers and links to each finding.
- **[`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md)** — the audited, claim-by-claim trail with decisions and the
  future-work queue (read its "Story map" to navigate in story order).

## Repository layout (one area per leg)
| Area | What |
|---|---|
| [`src/`](src/README.md) | All current code, grouped by leg: `prep/` `confound/` `census/` `dge/` `legacy/` `plotting/` (+ `config.py`). |
| [`findings/`](findings/README.md) | The findings store — one folder per finding, each with its data file(s) + a README of numbers/method/caveats. Ordered by the story. |
| [`reports/`](reports/) | Written outputs: `FULL_STORY.txt`, `SYNTHESIS.md`, `finding_stories.md`, `DGE.md`. |
| `results/` | Generated `figures/` and donor-level / per-gene `tables/` + provenance (`object_schema.txt`). |
| `data/` | Local raw + processed data (gitignored — each machine downloads it; see `scripts/`). |
| `papers/` | The source papers (gitignored — copyrighted). |
| `signatures/` | Gene-set lists (pericentral/periportal marker tiers, etc.). |
| `scripts/` | `download_data.sh` — fetch the raw data locally. |
| `archive/` | Everything stale/legacy: the pre-reanalysis pipeline & figures, old plans, the rejected manuscript and frozen deck, and prior code backups. Not part of the current story. |

Top-level docs: `README.md` (this), `FINDINGS.md`, `CLAIMS_LEDGER.md`, and the course brief PDF.

## Scope
We correct **only** the single-nucleus transcriptomic de-zonation leg, in matched biopsy tissue. We do not
address the paper's imaging / protein / organoid / spatial-architecture evidence, and we agree the strong
zonation/transdifferentiation signal is an end-stage phenomenon. All quantitative claims are on raw RNA UMI
counts; the unit of inference is the donor (~47), never the cell.
