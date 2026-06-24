// Standalone add-on slides for MASLD_stages_computational_analysis_roee_shira.pptx
// Generates extra_slides.pptx (2 slides) styled to match the main deck.
// Copy the slides you want into the canonical .pptx. Run: node extra_slides.js
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const A = __dirname + "/assets/";
function pngSize(file){ const b=fs.readFileSync(file); return {w:b.readUInt32BE(16), h:b.readUInt32BE(20)}; }
function img(s,file,box){ const d=pngSize(A+file), ar=d.w/d.h; let w=box.w,h=w/ar; if(box.h&&h>box.h){h=box.h;w=h*ar;} const x=box.x+(box.w-w)/2; s.addImage({path:A+file,x,y:box.y,w,h}); }
function figcap(s,x,y,w,txt){ s.addText(txt,{x,y,w,h:0.4,fontSize:12,italic:true,color:MUTE,align:"center",margin:0}); }

// --- palette + fonts copied verbatim from build_deck.js ---
const PC="1D4ED8", PP="EA580C", DUAL="7C3AED", NULL="9CA3AF",
      BIOPSY="0D9488", CONFOUND="BE123C", ENDSTAGE="86198F", STRESS="DC2626",
      WHITE="FFFFFF", MUTE="5C6E73",
      INK="1B2B31", TEAL="1B6E78", TEALD="123F47", AMBER="C0561B",
      SLATE="123F47", ORANGE="C0561B", BG="F7F5F1", LIGHT="ECF1F1", DARK="16242B";
const SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});

const p=new pptxgen(); p.layout="LAYOUT_WIDE"; p.author="Roee Tekoah, Shira Gelbstein";

function head(s,kicker,headline,section){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:8.6,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  if(section) s.addText(section,{x:9.4,y:0.32,w:3.45,h:0.3,fontSize:11,bold:true,color:TEAL,charSpacing:2,align:"right",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.85,fontSize:28,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
// footer WITHOUT a page number (these slides get inserted at an arbitrary position)
function footC(s){ s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0}); }
function fcite(s,txt){
  s.addShape(p.shapes.LINE,{x:0.5,y:6.78,w:3.2,h:0,line:{color:"C9C0B2",width:0.75}});
  s.addText(txt,{x:0.5,y:6.84,w:12.3,h:0.26,fontSize:10,italic:true,color:"6B6256",align:"left",margin:0});
}
let s;
// full-bleed background rectangle: survives copy-paste into another deck (slide-level bg can be dropped by the destination theme)
const bleed=(s)=>s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:13.333,h:7.5,fill:{color:BG},line:{type:"none"}});

// ============================================================ ADD-ON 1 — DONOR VARIANCE  [BACKUP]
s=p.addSlide(); s.background={color:BG}; bleed(s);
head(s,"DONOR VARIANCE","Why a flat result is readable despite huge donor spread","BACKUP");
s.addText([{text:"Within each fibrosis stage the per-donor pericentral-anchor fraction spans ~25–35 pp (SD ≈ 12 pp). ",options:{color:INK}},
  {text:"Could that scatter be hiding a real trend? No — four reasons:",options:{bold:true,color:INK}}],
  {x:0.7,y:1.5,w:12.3,h:0.5,fontSize:15,align:"left"});
const dv=[
  ["1","The donor is the replicate — not the cell",
   "Inference is donor-level (F1–F4 = 8 / 12 / 12 / 4). A stage MEAN has standard error SE ≈ SD/√n ≈ 12/√10 ≈ 4 pp — we compare stage means (± 4 pp), not individual donors (± 12 pp).",PC],
  ["2","The spread is the same at every stage",
   "Variance is homoscedastic — as wide at F1 as at F4. A real progression would shift the mean monotonically beyond ± 4 pp; it doesn’t. This is noise around a flat line, not a trend buried in noise.",BIOPSY],
  ["3","We bound what is excluded (TOST)",
   "Not merely “no trend found”: a shift > ± 19 pp between F1 and F4 is positively rejected at the donor level. Only a subtle drift (≤ 10 pp) remains possible — limited by F4’s n = 4.",DUAL],
  ["4","Stable across marker sets & thresholds",
   "The flat result holds on 6 marker sets (2–1,637 genes, incl. Paper 2’s own) and the full ≥1 / ≥2 / ≥3-UMI grid — no setting-dependent signal hiding in the variance.",AMBER]];
for(let i=0;i<4;i++){ const col=i%2,row=Math.floor(i/2); const x=0.7+col*6.05, y=2.2+row*1.72;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:5.9,h:1.55,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w:0.1,h:1.55,fill:{color:dv[i][3]}});
  s.addText(dv[i][0],{x:x+0.28,y:y+0.12,w:0.6,h:0.6,fontSize:26,bold:true,color:dv[i][3],fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(dv[i][1],{x:x+0.9,y:y+0.16,w:4.85,h:0.5,fontSize:14.5,bold:true,color:INK,align:"left",valign:"top",margin:0});
  s.addText(dv[i][2],{x:x+0.9,y:y+0.62,w:4.85,h:0.85,fontSize:11.5,color:"334155",align:"left",valign:"top",margin:0});
}
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:5.75,w:11.95,h:0.72,fill:{color:"E7F0EE"},line:{color:TEAL,width:1},rectRadius:0.06});
s.addText([{text:"Bottom line:  ",options:{bold:true,color:TEALD}},
  {text:"large person-to-person variance ≠ an undetectable signal. With donor-level inference and an equivalence bound, a large progressive de-zonation is ",options:{color:INK}},
  {text:"excluded",options:{bold:true,color:TEALD}},{text:" (a subtle ≤10-pp drift is not).",options:{color:INK}}],
  {x:0.95,y:5.75,w:11.5,h:0.72,fontSize:13.5,align:"left",valign:"middle"});
footC(s);

// ============================================================ ADD-ON 2 — METHODS & SOFTWARE  [METHOD]
s=p.addSlide(); s.background={color:BG}; bleed(s);
head(s,"METHODS & SOFTWARE","The analysis stack, end to end","METHOD");
s.addText("Every quantitative claim runs at the donor level on raw molecule counts. The methods, grouped by step:",
  {x:0.7,y:1.5,w:12.3,h:0.4,fontSize:14.5,italic:true,color:MUTE,align:"left"});
const blocks=[
  ["COUNTS & DEPTH",PC,[
    ["Raw UMI extraction (not SCT)","absolute detection needs molecules, not normalized residuals — Seurat / Matrix (R)"],
    ["Binomial down-sampling → 1,500 UMIs / nucleus","removes sequencing depth as a confound (the depth-match)"]]],
  ["PER-GENE DGE",BIOPSY,[
    ["Pseudobulk, donor-level","sum each donor’s hepatocyte counts → one profile per donor (Squair 2021)"],
    ["edgeR — TMM + NB quasi-likelihood GLM","composition-robust normalization + per-gene fibrosis trend (filterByExpr gene filter)"]]],
  ["GENE-SET TESTS",DUAL,[
    ["GSEA pre-rank — gseapy","is a set enriched at one end of the ranked genome?"],
    ["CAMERA — competitive (limma)","set shifted more than the rest of the transcriptome? (Wu & Smyth 2012)"],
    ["ROAST / mroast — self-contained (limma)","does the set move against zero? rotation p-value (Wu 2010)"]]],
  ["SOURCE & STATISTICS",AMBER,[
    ["decontX — ambient-RNA removal","models native + ambient mixture, subtracts the estimate (celda; Yang 2020)"],
    ["TOST equivalence  ·  Cramér’s V  ·  Spearman / partial corr.","bound the null · test batch confounding · trend & covariate control"]]]];
for(let i=0;i<4;i++){ const col=i%2,row=Math.floor(i/2); const x=0.7+col*6.05, y=2.1+row*2.3;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:5.9,h:2.12,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w:5.9,h:0.06,fill:{color:blocks[i][1]}});
  s.addText(blocks[i][0],{x:x+0.25,y:y+0.16,w:5.4,h:0.3,fontSize:13,bold:true,color:blocks[i][1],charSpacing:1.5,align:"left",margin:0});
  let yy=y+0.55;
  for(const it of blocks[i][2]){
    s.addText([{text:"• "+it[0]+"  ",options:{bold:true,color:INK}},{text:"— "+it[1],options:{color:"475569"}}],
      {x:x+0.25,y:yy,w:5.45,h:0.5,fontSize:11,align:"left",valign:"top",margin:0});
    yy+=0.5;
  }
}
fcite(s,"Stack: R (edgeR, limma, decontX/celda, Seurat) · Python (numpy, scipy, pandas, gseapy).   Refs: edgeR / TMM — Robinson, McCarthy & Smyth 2010; Robinson & Oshlack 2010 · CAMERA — Wu & Smyth 2012 · ROAST — Wu et al. 2010 · decontX — Yang et al. 2020 · pseudobulk — Squair et al. 2021 · GSEA — Subramanian et al. 2005.");
footC(s);

// ============================================================ ADD-ON 3 — SOURCE (biliary, corrected)  [RESULTS]
s=p.addSlide(); s.background={color:BG}; bleed(s);
head(s,"SOURCE","The biliary signal: most likely compositional — a lead","RESULTS");
s.addText([{text:"What we see:  ",options:{bold:true,color:INK}},
  {text:"biliary / ductular genes (EPCAM, SOX9, GRHL2, B3GNT3, SPINT2) rise at F4 — exactly where cirrhosis’s ductular reaction floods the tissue with cholangiocytes.",options:{color:INK}}],
  {x:0.7,y:1.46,w:12.3,h:0.45,fontSize:14.5,align:"left"});
img(s,"fig_compositional.png",{x:0.4,y:1.95,w:12.55,h:2.0});
figcap(s,0.4,4.0,12.55,"Figure.  Source attribution — cross-lineage abundance, decontX ambient-RNA removal, and the F4 ductular reaction.");
// refined evidence ladder: the compositional mechanism, the class-imbalance caveat, and the residual that survives
const lad=[
 ["COMPOSITIONAL  (the lead)","065F46","E7F2ED","These are cholangiocyte genes. At F4 there are more cholangiocytes → more of their RNA in the ambient “soup” (plus the odd doublet) enters hepatocyte droplets → hepatocytes look biliary without transdifferentiating."],
 ["RARE PER CELL  (read it carefully)","B45309","FBF0E2","Only ~0.4% of hepatocyte nuclei co-detect biliary markers at ≥2 UMI — not population-wide. But that is prevalence over ALL hepatocytes: it argues against MASS transdifferentiation, not against a rare sub-population (class imbalance)."],
 ["OPEN  (a residual survives)","BE123C","FBEEE9","decontX removes about half the hits (64 → 34), but EPCAM / SPINT2 / B3GNT3 survive decontamination — ambient can’t explain all of it, so a rare intrinsic state is not excluded."]];
let ly=4.42;
for(const row of lad){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:ly,w:12.25,h:0.66,fill:{color:row[2]},rectRadius:0.05});
  s.addText(row[0],{x:0.78,y:ly,w:2.95,h:0.66,fontSize:11,bold:true,color:row[1],charSpacing:0.5,valign:"middle",margin:0});
  s.addText(row[3],{x:3.8,y:ly,w:8.9,h:0.66,fontSize:11,color:INK,valign:"middle",margin:0});
  ly+=0.72;
}
s.addText([{text:"Verdict:  ",options:{bold:true,color:TEALD}},
  {text:"most consistent with composition / ambient (the ductular reaction) — a lead, not a closed verdict.",options:{italic:true,color:INK}}],
  {x:0.6,y:6.66,w:12.3,h:0.35,fontSize:13,align:"left"});
footC(s);

p.writeFile({fileName:__dirname+"/extra_slides.pptx"}).then(f=>console.log("WROTE",f));
