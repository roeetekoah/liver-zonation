# Git / GitHub setup — uni ↔ home, and working with a partner

> Run these on your **own PC** (not through this tool — GitHub needs your login).
> Data is **not** in the repo (too big / copyrighted); each machine downloads it
> locally — see PROJECT_MAP.md. Only code + docs + small figures are tracked.

## 1. One-time: create the repo and push (from the Hackathon folder)
```bash
cd D:\CS\Genomics\Hackathon
git init
git add .
git commit -m "Initial commit: primer, plan, pipeline scaffold, signatures"
git branch -M main
# create the empty repo on GitHub first (web UI) OR with the GitHub CLI:
#   gh repo create roeetekoah/liver-zonation --private --source . --remote origin
git remote add origin https://github.com/roeetekoah/liver-zonation.git
git push -u origin main
```
`.gitignore` already excludes `data/`, `papers/`, `analysis/paper1/`, and all `*.mat/*.mtx/*.npz/*.rds`.
Verify before pushing: `git status` should show **no** multi-GB files.

## 2. Branch model (2 people, 2 days)
Keep `main` always working. Each person works on a short branch, then merges to `main`
when a piece works. You edit mostly different files (A = stats/scoring, B = classifier/DE),
so conflicts will be rare.

Suggested starter branches (create them now so you're ready):
```bash
git checkout -b feat/pipeline-stats   # Person A: scoring, validation, collapse, stats
git push -u origin feat/pipeline-stats
git checkout main
git checkout -b feat/classifier-de    # Person B: classifier (4b) + zone DE (Step 7)
git push -u origin feat/classifier-de
git checkout main
```
Convention: branch name = `feat/<short-task>` (e.g. `feat/step6-collapse`, `feat/ruler-diagnostics`).
Merge via a Pull Request on GitHub (or `git merge` locally) once a step passes its acceptance check.

## 3. Daily uni ↔ home workflow
**Leaving a machine (save your work everywhere):**
```bash
git add -A && git commit -m "wip: <what you did>" && git push
```
**Arriving at the other machine (get the latest):**
```bash
git pull        # on your branch
# first time on a new machine: git clone https://github.com/roeetekoah/liver-zonation.git
```
Then re-create the local data (not in git): download per PROJECT_MAP.md, run
`01_extract_paper1_hepatocytes.R` and `convert_paper2_mat.py` once on that machine.

## 4. Working with your partner safely
```bash
git checkout main && git pull          # start from latest main
git checkout -b feat/my-task           # your own branch
# ...work, commit, push...
git push -u origin feat/my-task
# open a Pull Request on GitHub -> review -> merge into main
git checkout main && git pull          # everyone re-syncs main after a merge
```
If you both touch the same file, Git will flag a conflict on merge; resolve the marked
lines, `git add` them, and commit. Keeping tasks on separate files avoids this.

## 5. Tip: keep the repo out of any cloud-sync folder
Don't put the working git clone inside OneDrive/Dropbox — the sync client fighting `.git`
causes corruption. `D:\CS\Genomics` is fine if it isn't cloud-synced; otherwise clone to
e.g. `D:\dev\liver-zonation` and keep the big `data/` wherever you like (it's git-ignored).
