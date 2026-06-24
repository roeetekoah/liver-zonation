// One-line reference / cheat-sheet for the MASLD re-analysis methods & concepts.
// Generates cheatsheet.pptx (4 pages) -> export to PDF separately. Run: node cheatsheet.js
const pptxgen = require("pptxgenjs");

const PC="1D4ED8", DUAL="7C3AED", BIOPSY="0D9488", AMBER="C0561B", CONFOUND="BE123C",
      WHITE="FFFFFF", MUTE="5C6E73", INK="1B2B31", TEAL="1B6E78", ORANGE="C0561B", BG="F7F5F1";
const SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon  —  methods & concepts reference";

const p=new pptxgen(); p.layout="LAYOUT_WIDE"; p.author="Roee Tekoah, Shira Gelbstein";
const bleed=(s)=>s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:13.333,h:7.5,fill:{color:BG},line:{type:"none"}});
function head(s,kicker,headline){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:11.0,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.7,fontSize:26,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
function footC(s){ s.addText(COURSE,{x:0.5,y:7.12,w:12.3,h:0.3,fontSize:10,color:MUTE,align:"left",margin:0}); }

// each page: a title, an accent colour for the term column, and rows of [term, one-sentence]
function page(kicker,headline,accent,rows){
  const s=p.addSlide(); s.background={color:BG}; bleed(s); head(s,kicker,headline);
  const body=rows.map(r=>[
    {text:r[0],options:{bold:true,color:accent,valign:"middle",fill:{color:WHITE}}},
    {text:r[1],options:{color:INK,valign:"middle",fill:{color:WHITE}}}]);
  s.addTable(body,{x:0.5,y:1.5,w:12.33,colW:[2.95,9.38],
    border:{type:"solid",pt:0.5,color:"E2DCCF"}, align:"left", valign:"middle",
    fontSize:11.5, rowH:0.3, margin:[3,6,3,6], autoPage:false});
  footC(s);
}

// ---------- PAGE 1 ----------
page("REFERENCE · 1 / 6","Counts, normalization & differential expression",BIOPSY,[
 ["Pseudobulk","Sum all of one donor's hepatocyte UMIs into a single profile, so the donor — not the cell — is the statistical unit (cells in a donor are not independent)."],
 ["CPM (counts per million)","Each gene as a share of the donor's total counts; simple but compositional — if a few genes surge, everyone else's share mechanically shrinks."],
 ["TMM (trimmed mean of M-values)","Pick one sample as reference, take each other sample's gene-wise log-ratios to it, trim the extreme movers, average the rest → the library's scaling factor, so surging genes can't distort it (composition-robust)."],
 ["edgeR","The R / Bioconductor package that runs our per-gene differential-expression test on the pseudobulk counts."],
 ["GLM (generalized linear model)","A regression linking a predictor (here: fibrosis stage) to a response that isn't normally distributed — for counts, through a negative-binomial noise model."],
 ["NB quasi-likelihood GLM","edgeR's engine: model each gene's counts as negative-binomial (mean + overdispersion) and fit a quasi-likelihood GLM that estimates the extra variability robustly → calibrated p-values with few replicates."],
 ["filterByExpr","edgeR's pre-filter: keep a gene only if it has enough reads in enough samples of the smallest stage group, else drop it (≈21,000 of ~36k kept). Low-count genes carry no statistical power and only inflate the multiple-testing burden, so removing them sharpens the real hits."],
 ["Binomial down-sampling","Randomly thin every nucleus to a common 1,500 UMIs (each molecule kept with equal probability) so sequencing depth can't drive detection."],
]);

// ---------- PAGE 2 ----------
page("REFERENCE · 2 / 6","Gene-set tests & statistics",DUAL,[
 ["GSEA (pre-rank)","Rank every gene by its fibrosis-trend statistic, then test whether a gene set clusters near one end of that ranking instead of being scattered."],
 ["CAMERA","A competitive set test: is this set shifted more than the rest of the genome? — and it corrects for correlation between the set's genes."],
 ["ROAST / mroast","A self-contained set test: does the set move away from zero on its own (p-value from rotations)? — ignores the rest of the genome, more conservative."],
 ["competitive vs self-contained","Competitive asks “more shifted than other genes?”; self-contained asks “different from no change at all?” — a set can pass one and fail the other."],
 ["TOST (two one-sided tests)","An equivalence test: not “is there a difference?” but “is the difference small enough to rule out anything bigger than a set bound?” — lets us say “no large change,” not just “nothing significant.”"],
 ["Cramer's V","A 0–1 score of association between two categorical variables (e.g. sequencing run vs tissue source): 0 = independent, 1 = perfectly confounded."],
 ["Spearman correlation","Correlation of ranks — captures any monotonic trend, robust to outliers and non-linear scaling (used for donor-level fibrosis trends)."],
 ["Partial correlation","Correlation between two variables after removing a third's effect (e.g. detox vs fibrosis, controlling for age)."],
]);

// ---------- PAGE 3 ----------
page("REFERENCE · 3 / 6","Tools & data terms",AMBER,[
 ["decontX","Models each droplet as native RNA + a shared ambient “soup,” estimates each cell's ambient fraction, and subtracts it → a decontaminated count matrix."],
 ["SCT (SCTransform) — why we dropped it","Seurat normalization that swaps raw UMIs for model-smoothed values. Our two core questions are defined on integer molecules, which SCT destroys: (a) marker co-detection asks “does this nucleus carry ≥ 2 real molecules of marker X?” — a “≥ 2 UMI” call is meaningless on smoothed residuals; (b) ambient sensitivity must tell 0 vs 1 vs 2 true molecules apart, but SCT pools / imputes across cells and would manufacture apparent co-expression. So we work on raw counts."],
 ["Ambient RNA (“soup”)","Cell-free RNA from lysed cells floating in the droplet suspension; every droplet absorbs some, so genes from abundant cell types leak into other cells."],
 ["Ductular reaction","The expansion of bile-duct / cholangiocyte cells in cirrhosis — it makes the soup richer in biliary RNA exactly at F4."],
 ["Doublets","Two nuclei captured in one droplet and read as a single “cell” — a hepatocyte + cholangiocyte doublet fakes co-expression."],
 ["BCV / dispersion","Biological coefficient of variation — how much a gene's counts vary beyond Poisson noise; edgeR estimates it to avoid false positives."],
 ["Anchor classification","A yes/no detection call: a nucleus is “PC” if it detects GLUL/CYP3A4 at ≥ 2 UMI — robust to a level drop, which is why the fraction can stay flat while the program dims."],
]);

// ---------- PAGE 4 — CONFOUNDER BATTERY (1/2) ----------
// each sentence decodes all three columns of the audit table: what the confounder is (why it could fool us) · what we did + what the numbers mean · the verdict
page("REFERENCE · 4 / 6","The confounder battery, explained (1 / 2)",CONFOUND,[
 ["Tissue source","Could fool us because disease stage is tangled with how the tissue was obtained — healthy & end-stage are deceased-donor organ cubes / explants while F0–F4 are needle biopsies; since the ends aren't acquisition-matched, the verdict is to exclude them and analyze biopsy-only F1–F4."],
 ["Procurement stress","Tissue handling switches on stress genes that could masquerade as disease; we measured immediate-early + heat-shock genes across 6 cell lineages — hepatocytes spike ~18× but endothelium (which has no zonation program) spikes the same ~18×, so the verdict is organ-wide handling stress, not a zonation change."],
 ["Sequencing batch","If sequencing runs line up with stage, batch effects could mimic disease; the run↔source association is high (Cramér's V = 0.84) but run↔fibrosis within biopsies is only 0.40 — so batch is fully confounded at the ends, yet the biopsy axis stays estimable."],
 ["Lobe (R / C / L)","Explants sample several liver lobes (right / caudate / left) and lobe differences could skew detection; comparing marker detection across the three lobes shows it is lobe-invariant, so lobe is not the driver."],
 ["Sequencing depth","Deeper-sequenced nuclei detect more genes, so depth alone can fake “more zonation”; we binomially down-thinned every nucleus to a common budget (1,000 / 1,500 / 3,000 UMIs) and the PC-share stayed flat at every budget (SD only 0.006–0.010), so depth is not driving it."],
]);

// ---------- PAGE 5 — CONFOUNDER BATTERY (2/2) ----------
page("REFERENCE · 5 / 6","The confounder battery, explained (2 / 2)",CONFOUND,[
 ["Ambient RNA (“soup”)","Ambient RNA from abundant genes (e.g. albumin / ALB) could create fake co-expression; across 38 donors the correlation between a donor's ALB ambient share and their dual (co-expression) fraction is +0.04 — essentially zero — so ambient does not drive co-expression."],
 ["Cholangiocyte mis-annotation","If some “hepatocytes” are actually mislabeled cholangiocytes they would fake a biliary signal; within every anchor class the cholangiocyte markers are near-absent (KRT19⁺ ≤ 0.1%, EPCAM⁺ ≤ 0.3%), so the anchor cells are not contaminating cholangiocytes."],
 ["Ploidy / complexity","Cells of different complexity (number of genes detected, nFeatures) could track stage and bias detection; mean nFeatures by stage is non-monotone (2218 / 3063 / 3169 / 2641 / 1984), so complexity does not track stage."],
 ["Depth-match discard","Down-thinning discards nuclei that fall below the UMI budget, and if those discards were pericentral-biased it would skew the result; the 3.5–7.8% dropped are uniformly lower-detection cells — depth-driven, not PC-biased."],
 ["Clinical covariates","Demographics like age correlate with fibrosis and could explain the detox trend; the partial correlation of detox with fibrosis controlling for age is −0.32 (age–fibrosis = +0.43), so demographics do not explain the trend."],
]);

// ---------- PAGE 6 ----------
page("REFERENCE · 6 / 6","Distinctions we kept confusing",PC,[
 ["Dimming vs de-zonation","De-zonation = cells change identity (refuted); dimming = cells keep identity but the program's level drops (the one real change). Radio: genre change vs volume down."],
 ["Anchor genes vs detox genes","Identity is a detection call on GLUL + CYP3A4; the detox dimming is measured on separate genes (CYP2E1, CYP1A2 …), so identity stays flat while the module's level falls."],
 ["Depletion vs turn-off","Depletion = an anchor (pole) box shrinks; turn-off = the null (double-negative) box grows — different boxes, opposite directions, neither implies the other."],
 ["Compression vs dimming","Compression = the gradient's shape flattens (cells drift to the middle); dimming = the level drops with the shape kept."],
 ["Relative vs absolute metric","A z-score / correlation reads the gradient's shape (scale-free); only counting molecules reads how many cells sit where."],
 ["Donor as the replicate","The ~47 donors are the independent units; cells within a donor are pseudoreplicates → summarize per donor, or you fake significance (SE ≈ SD/√n)."],
 ["Biliary = compositional confounder","At F4 a ductular reaction adds cholangiocytes whose ambient RNA enriches hepatocyte droplets — so a “hepatocyte biliary” signal can rise from tissue composition, not transdifferentiation. decontX removes most hits; EPCAM/SPINT2/B3GNT3 survive → a rare real state not excluded."],
 ["Equivalence bound vs proof","TOST excludes shifts > ±19 pp; a ≤ 10-pp drift stays possible — “no large change,” not “exactly zero.”"],
]);

p.writeFile({fileName:__dirname+"/cheatsheet.pptx"}).then(f=>console.log("WROTE",f));
