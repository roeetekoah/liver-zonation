// 8-minute deck: critical snRNA-seq re-analysis of Gribben et al. Nature 2024.
// 8 main slides (one strong visual each) + backup appendix. Run: node build_deck.js
const pptxgen = require("pptxgenjs");
const A = __dirname + "/assets/";

// ---- palette (deck spec; hex, no '#') ----
const PC="1D4ED8", PP="EA580C", DUAL="7C3AED", NULL="9CA3AF",
      BIOPSY="0D9488", CONFOUND="BE123C", ENDSTAGE="86198F", STRESS="DC2626", BILIARY="7C3AED",
      INK="1E293B", MUTE="64748B", BG="FFFFFF", LIGHT="F1F5F9", DARK="0F172A", WHITE="FFFFFF";
const TITLE_FS=30, BODY_FS=20, SMALL_FS=15, FOOT_FS=11;
const W=13.3, H=7.5;
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});

const p=new pptxgen(); p.layout="LAYOUT_WIDE"; p.author="MASLD re-analysis";
p.title="Matched biopsies preserve hepatocyte zonation in MASLD";

function title(s,t,sub){
  s.addText(t,{x:0.5,y:0.30,w:12.3,h:0.85,fontSize:TITLE_FS,bold:true,color:INK,align:"left",valign:"middle",margin:0});
  if(sub) s.addText(sub,{x:0.5,y:1.12,w:12.3,h:0.4,fontSize:SMALL_FS,italic:true,color:MUTE,align:"left",margin:0});
}
function foot(s,n,tag){
  s.addText([{text:`${tag}`,options:{color:MUTE}},{text:`     ·     ${n}`,options:{color:MUTE}}],
    {x:0.5,y:7.08,w:12.3,h:0.32,fontSize:FOOT_FS,align:"left",margin:0});
}
function img(s,file,box){ s.addImage({path:A+file,x:box.x,y:box.y,w:box.w,h:box.h,sizing:{type:"contain",w:box.w,h:box.h}}); }
function chip(s,x,y,w,h,txt,fill,tcol){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.08,shadow:sh()});
  s.addText(txt,{x,y,w,h,fontSize:SMALL_FS,bold:true,color:tcol||WHITE,align:"center",valign:"middle",margin:2});
}

// ===================================================================== SLIDE 1
let s=p.addSlide(); s.background={color:DARK};
s.addText("Matched biopsies preserve hepatocyte zonation in MASLD",
  {x:0.7,y:0.7,w:11.9,h:1.5,fontSize:40,bold:true,color:WHITE,align:"left",valign:"top"});
s.addText("A critical re-analysis of Gribben et al., Nature 2024 — snRNA-seq, GSE202379",
  {x:0.7,y:2.15,w:11.9,h:0.5,fontSize:18,italic:true,color:"CBD5E1",align:"left"});
// schematic: original claim -> re-analysis
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:3.1,w:5.4,h:1.5,fill:{color:"3F1D2B"},line:{color:CONFOUND,width:1.5},rectRadius:0.1});
s.addText([{text:"Original claim\n",options:{bold:true,color:"FCA5A5",fontSize:16}},
  {text:"MASLD progression → zonation loss + hepatocyte→cholangiocyte plasticity",options:{color:"FECACA",fontSize:14}}],
  {x:0.9,y:3.25,w:5.0,h:1.2,align:"left",valign:"middle"});
s.addShape(p.shapes.RIGHT_TRIANGLE,{x:6.25,y:3.7,w:0.55,h:0.35,fill:{color:"94A3B8"},rotate:0});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.2,y:3.1,w:5.4,h:1.5,fill:{color:"0B3B38"},line:{color:BIOPSY,width:1.5},rectRadius:0.1});
s.addText([{text:"Our re-analysis (matched biopsies)\n",options:{bold:true,color:"5EEAD4",fontSize:16}},
  {text:"zonation preserved; biliary signal likely compositional",options:{color:"99F6E4",fontSize:14}}],
  {x:7.4,y:3.25,w:5.0,h:1.2,align:"left",valign:"middle"});
s.addText([
  {text:"Question  ",options:{bold:true,color:"93C5FD"}},{text:"is the snRNA-seq evidence for progressive de-zonation robust?\n",options:{color:"E2E8F0",breakLine:true}},
  {text:"Answer  ",options:{bold:true,color:"5EEAD4"}},{text:"not across matched biopsy F1–F4 tissue.\n",options:{color:"E2E8F0",breakLine:true}},
  {text:"Scope  ",options:{bold:true,color:"CBD5E1"}},{text:"transcriptomic re-analysis only; imaging / organoids not re-tested.",options:{color:"E2E8F0"}}],
  {x:0.7,y:5.0,w:11.9,h:1.7,fontSize:18,align:"left",valign:"top",paraSpaceAfter:8});
s.addNotes("Open: the paper's biological claim is exciting — chronic liver disease may make hepatocytes lose zonation and move toward a biliary/cholangiocyte state. We asked whether the single-nucleus EXPRESSION evidence supports that once acquisition differences between samples are controlled. One-line answer up front: in matched needle biopsies, zonation is preserved.");

// ===================================================================== SLIDE 2
s=p.addSlide(); s.background={color:BG};
title(s,"Zonation can fail in several different ways");
// lobule axis bar (blue -> orange) via two halves + labels
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.0,y:1.9,w:5.2,h:0.55,fill:{color:PC},rectRadius:0.05});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.2,y:1.9,w:5.2,h:0.55,fill:{color:PP},rectRadius:0.05});
s.addText("Central vein",{x:0.6,y:2.5,w:2.4,h:0.3,fontSize:13,color:MUTE,align:"left"});
s.addText("Portal tract",{x:9.4,y:2.5,w:2.4,h:0.3,fontSize:13,color:MUTE,align:"right"});
s.addText("Pericentral program",{x:1.0,y:1.9,w:5.2,h:0.55,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
s.addText("Periportal program",{x:6.2,y:1.9,w:5.2,h:0.55,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
s.addText([{text:"PC markers: ",options:{bold:true,color:PC}},{text:"GLUL, CYP3A4, CYP2E1 / detox",options:{color:INK}}],
  {x:1.0,y:2.85,w:5.2,h:0.4,fontSize:14,align:"center"});
s.addText([{text:"PP markers: ",options:{bold:true,color:PP}},{text:"ASS1, CPS1, PCK1, HAL, ALDOB / urea cycle",options:{color:INK}}],
  {x:6.2,y:2.85,w:5.2,h:0.4,fontSize:14,align:"center"});
// failure-mode chips
s.addText("De-zonation is not one mechanism — count signatures distinguish them:",
  {x:1.0,y:3.7,w:10.4,h:0.4,fontSize:17,bold:true,color:INK,align:"left"});
chip(s,1.0,4.25,2.5,1.1,"PC depletion\n(pericentral cells lost)",PC);
chip(s,3.75,4.25,2.5,1.1,"Co-expression\n(both poles on)",DUAL);
chip(s,6.5,4.25,2.5,1.1,"Turn-off\n(neither pole on)",NULL,INK);
chip(s,9.25,4.25,2.15,1.1,"Composition shift\n(PP : PC changes)",PP);
s.addText("A single anti-correlation or UMAP impression conflates these. We test each with absolute counts.",
  {x:1.0,y:5.7,w:10.4,h:0.5,fontSize:15,italic:true,color:MUTE,align:"left"});
foot(s,"2 / 8","Minimal context");
s.addNotes("Audience knows hepatocytes and snRNA-seq, so only what's needed: zonation = different hepatocytes run different programs by lobule position. It can break down several ways — cells disappear, turn markers off, co-express both poles, or shift composition. This matters because one correlation score or UMAP can conflate very different mechanisms, so we use count signatures tied to specific scenarios.");

// ===================================================================== SLIDE 3
s=p.addSlide(); s.background={color:BG};
title(s,"Disease stage is entangled with tissue acquisition");
const xs=[1.0,2.55,3.85,5.15,6.45,7.75,9.5], lab=["Healthy","F0","F1","F2","F3","F4","End-stage"];
const colb=[CONFOUND,BIOPSY,BIOPSY,BIOPSY,BIOPSY,BIOPSY,ENDSTAGE], wd=[1.4,1.2,1.2,1.2,1.2,1.2,2.2];
for(let i=0;i<lab.length;i++){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:xs[i],y:2.0,w:wd[i],h:0.7,fill:{color:colb[i]},rectRadius:0.06,shadow:sh()});
  s.addText(lab[i],{x:xs[i],y:2.0,w:wd[i],h:0.7,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
}
s.addShape(p.shapes.LINE,{x:1.0,y:1.78,w:10.7,h:0,line:{color:MUTE,width:1.5,endArrowType:"triangle"}});
s.addText("disease progression →",{x:8.6,y:1.45,w:3.0,h:0.3,fontSize:13,italic:true,color:MUTE,align:"right"});
// acquisition row
s.addText("deceased-donor\norgan cubes",{x:0.7,y:2.9,w:2.0,h:0.7,fontSize:13,color:CONFOUND,align:"center"});
s.addText("16-gauge needle biopsies, right lobe",{x:2.55,y:2.9,w:6.6,h:0.4,fontSize:14,bold:true,color:BIOPSY,align:"center"});
s.addText("explanted cirrhotic\norgans, multi-lobe",{x:9.5,y:2.9,w:2.2,h:0.7,fontSize:13,color:ENDSTAGE,align:"center"});
// red brackets
s.addShape(p.shapes.RECTANGLE,{x:0.95,y:1.95,w:1.5,h:1.75,fill:{type:"none"},line:{color:CONFOUND,width:2,dashType:"dash"}});
s.addShape(p.shapes.RECTANGLE,{x:9.45,y:1.95,w:2.3,h:1.75,fill:{type:"none"},line:{color:CONFOUND,width:2,dashType:"dash"}});
s.addText("not acquisition-matched",{x:8.8,y:3.75,w:3.0,h:0.3,fontSize:12,bold:true,color:CONFOUND,align:"center"});
// numbers + bullets
s.addText([{text:"47 donors   ·   biopsy axis F0/F1/F2/F3/F4 = 2 / 8 / 12 / 12 / 4   ·   end-stage = 5   ·   healthy = 4",options:{}}],
  {x:1.0,y:4.35,w:11.0,h:0.4,fontSize:16,bold:true,color:INK,align:"center"});
s.addText([
  {text:"The full trajectory is also an acquisition trajectory.",options:{bullet:true,breakLine:true}},
  {text:"So healthy / end-stage comparisons cannot cleanly isolate disease biology.",options:{bullet:true,breakLine:true}},
  {text:"Clean axis used here: biopsy-only F1–F4.",options:{bullet:true,bold:true,color:BIOPSY}}],
  {x:1.6,y:5.0,w:10.0,h:1.6,fontSize:19,color:INK,align:"left",paraSpaceAfter:6});
foot(s,"3 / 8","The load-bearing confound");
s.addNotes("This is the load-bearing slide. If stage and acquisition are collinear, a progressive trajectory can be manufactured by procurement, ischemia, dissociation, or batch — not biology. Healthy and end-stage are deceased-donor / explant organ tissue; the disease spectrum F0–F4 is fresh needle biopsies. So the first question is not biology, it is comparability. We restrict the disease axis to the matched biopsies, F1–F4.");

// ===================================================================== SLIDE 4
s=p.addSlide(); s.background={color:BG};
title(s,"Endpoint samples carry an organ-wide stress signature");
img(s,"fig_stress.png",{x:0.4,y:1.5,w:8.6,h:5.2});
s.addText([
  {text:"Stress genes: FOS, JUN(B/D), ATF3, DUSP1, HSPA1A/B.",options:{bullet:true,breakLine:true}},
  {text:"The same spike appears in non-zonated endothelial cells.",options:{bullet:true,breakLine:true,bold:true}},
  {text:"→ acquisition/procurement signal, not hepatocyte zonation biology.",options:{bullet:true,color:STRESS,bold:true}}],
  {x:9.2,y:2.3,w:3.8,h:3.0,fontSize:18,color:INK,align:"left",paraSpaceAfter:10});
foot(s,"4 / 8","Stress validates the confound  ·  donor-level, down-thinned to 1,500 UMIs");
s.addNotes("The decisive point is cross-lineage. Stress is ~22× higher in end-stage explants than biopsies — but if endothelial cells, which have no zonation program, show the SAME immediate-early spike (18.2× vs 18.5× in hepatocytes), then this is not a hepatocyte zonation program. It is organ-wide acute handling/procurement stress. That is why we exclude the deceased-donor and explant groups from the disease axis.");

// ===================================================================== SLIDE 5
s=p.addSlide(); s.background={color:BG};
title(s,"Raw-count anchor classification: biopsy zonation is preserved");
// mini pipeline strip
const steps=["raw UMIs","down-thin to 1,500","marker ON if ≥2 UMI","classify nucleus","fraction per donor"];
let px=0.5; for(let i=0;i<steps.length;i++){ const w=2.25;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:px,y:1.45,w:w,h:0.55,fill:{color:i==2?"EDE9FE":LIGHT},line:{color:i==2?DUAL:"CBD5E1",width:1},rectRadius:0.06});
  s.addText(steps[i],{x:px,y:1.45,w:w,h:0.55,fontSize:12.5,bold:i==2,color:i==2?DUAL:INK,align:"center",valign:"middle",margin:1});
  if(i<steps.length-1) s.addShape(p.shapes.LINE,{x:px+w+0.0,y:1.72,w:0.2,h:0,line:{color:MUTE,width:1.5,endArrowType:"triangle"}});
  px+=w+0.2; }
img(s,"fig_anchor2x2.png",{x:0.5,y:2.15,w:9.0,h:4.7});
s.addText([
  {text:"PC-anchor: PC on / PP off",options:{bullet:{code:"25CF"},color:PC,breakLine:true}},
  {text:"PP-anchor: PP on / PC off",options:{bullet:{code:"25CF"},color:PP,breakLine:true}},
  {text:"Dual: both on",options:{bullet:{code:"25CF"},color:DUAL,breakLine:true}},
  {text:"Null: neither on",options:{bullet:{code:"25CF"},color:"64748B",breakLine:true}}],
  {x:9.7,y:2.4,w:3.3,h:1.7,fontSize:15,align:"left",paraSpaceAfter:4});
s.addText([
  {text:"Unit = donor, not nucleus.\n",options:{bold:true,breakLine:true}},
  {text:"≥2-UMI cut suppresses single-molecule ambient RNA.\n",options:{breakLine:true}},
  {text:"Robust across the marker/threshold sensitivity grid.",options:{}}],
  {x:9.7,y:4.2,w:3.3,h:2.4,fontSize:14.5,color:INK,align:"left",valign:"top"});
foot(s,"5 / 8","Main result  ·  no large de-zonation route on the biopsy axis");
s.addNotes("Why raw counts: if a cell has one KRT19 or one GLUL molecule, that may be ambient RNA — for this question, absolute molecule detection matters, so SCT-normalized values are the wrong object. We down-thin every nucleus to a common 1,500-UMI budget, call a marker on only at ≥2 UMIs, classify each hepatocyte, and summarize per donor. The key is not that every number is identical — it's that none of the failure modes shows a monotone, large, biopsy-axis collapse. Dual co-expression stays ~0.4%, vs ~2.9% in the confounded explants.");

// ===================================================================== SLIDE 6
s=p.addSlide(); s.background={color:BG};
title(s,"Genome-wide pseudobulk finds one main signal: biliary markers");
img(s,"fig_volcano.png",{x:0.3,y:1.45,w:8.8,h:5.4});
s.addText([
  {text:"Pseudobulk per donor (sum raw hepatocyte UMIs); edgeR TMM + NB quasi-likelihood.\n",options:{breakLine:true}},
  {text:"64 genes at FDR<0.05 — mostly biliary/ductular.\n",options:{bold:true,breakLine:true}},
  {text:"Zonation markers not significant (GLUL FDR 0.80).\n",options:{color:PC,breakLine:true}},
  {text:"“No large single-gene hepatocyte program outside the biliary/ductular burden.”",options:{italic:true,color:BILIARY}}],
  {x:9.3,y:2.2,w:3.7,h:4.0,fontSize:17,color:INK,align:"left",valign:"top",paraSpaceAfter:10});
foot(s,"6 / 8","Discovery scan  ·  cirrhotic F4 vs F1");
s.addNotes("Pseudobulk in one sentence: we collapse thousands of nuclei back to one profile per donor, because donors — not cells — are the biological replicates. This scan was not the primary proof of zonation; it's an independent count-based check (zonation genes flat) plus a discovery layer. Of ~21,000 genes only 64 are significant, and they are biliary/ductular markers, not a broad metabolic/stress/detox program. Wording matters: we say no large single-gene program outside the biliary burden — gene-set testing is still owed for weak coordinated pathways.");

// ===================================================================== SLIDE 7
s=p.addSlide(); s.background={color:BG};
title(s,"The biliary signal is real — but likely not broad transdifferentiation");
img(s,"fig_compositional.png",{x:0.3,y:1.55,w:12.7,h:4.3});
s.addText([
  {text:"Ductular reaction enriches cholangiocyte ambient RNA exactly at F4;  true hepatocyte biliary co-expression is rare (~0.4%).",options:{bullet:true,breakLine:true}},
  {text:"CXCL10 is separated as a possible real inflammatory signal — it does not track the cholangiocyte fraction.",options:{bullet:true,color:STRESS}}],
  {x:0.7,y:6.05,w:12.0,h:1.1,fontSize:16.5,color:INK,align:"left",paraSpaceAfter:6});
foot(s,"7 / 8","Source attribution: consistent with ambient RNA + rare mixed nuclei (a lead, not closed)");
s.addNotes("Cautious wording: this does not prove every surviving gene is contamination. It says the dominant interpretation of the biliary burden should be compositional unless proven otherwise — the genes are 5–78× more abundant in cholangiocytes, cholangiocytes expand at F4, per-cell co-expression is ~0.4%, and decontX halves the hits and drops SOX4/SOX9. decontX is evidence, not a verdict: it can over- or under-correct. So source attribution is a lead, not a closed verdict.");

// ===================================================================== SLIDE 8
s=p.addSlide(); s.background={color:DARK};
s.addText("Matched biopsies support preservation, not progressive collapse",
  {x:0.7,y:0.5,w:11.9,h:0.9,fontSize:28,bold:true,color:WHITE,align:"left",valign:"middle"});
const cols=[
  {h:"Conclusions",c:"5EEAD4",items:["Full healthy→end-stage trajectory is source-confounded.","In biopsy F1–F4, hepatocyte transcriptional zonation is preserved.","Main DGE signal = biliary/ductular burden, likely compositional."]},
  {h:"Limits",c:"FCA5A5",items:["snRNA-seq ≠ lobule geometry / spatial architecture.","Imaging / protein / organoid evidence not re-analyzed.","F4 has only 4 biopsy donors.","Gene-level DGE can miss weak coordinated pathways."]},
  {h:"Next",c:"93C5FD",items:["CAMERA / ROAST gene-set tests.","Leave-one-F4-donor-out DGE.","Quantitative contamination model.","Spatial / independent biopsy validation."]}
];
let cx=0.7; for(const col of cols){ const cw=3.9;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:cx,y:1.65,w:cw,h:4.4,fill:{color:"1E293B"},rectRadius:0.08,shadow:sh()});
  s.addText(col.h,{x:cx,y:1.8,w:cw,h:0.5,fontSize:20,bold:true,color:col.c,align:"center"});
  s.addText(col.items.map((t,i)=>({text:t,options:{bullet:true,color:"E2E8F0",breakLine:true,paraSpaceAfter:10}})),
    {x:cx+0.25,y:2.45,w:cw-0.45,h:3.5,fontSize:14.5,align:"left",valign:"top"});
  cx+=cw+0.25; }
s.addText("The transcriptomic leg of progressive de-zonation does not survive matched-source re-analysis.",
  {x:0.7,y:6.35,w:11.9,h:0.7,fontSize:18,bold:true,italic:true,color:WHITE,align:"center"});
s.addNotes("Close on the methodological lesson, aligned with the assignment: the lesson is not only biological. In single-cell disease atlases, acquisition matching can dominate apparent disease trajectories. Our bottom line is narrow and honest: the transcriptomic leg of progressive de-zonation does not survive matched-source re-analysis; imaging/protein/organoid evidence is untouched.");

// ===================================================================== BACKUPS
function back(t){ const b=p.addSlide(); b.background={color:BG};
  b.addText("Backup",{x:0.5,y:0.28,w:3,h:0.4,fontSize:13,bold:true,color:BIOPSY});
  b.addText(t,{x:0.5,y:0.66,w:12.3,h:0.8,fontSize:26,bold:true,color:INK,align:"left"}); return b; }
function bbul(b,items,y){ b.addText(items.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:9}})),
  {x:0.8,y:y||1.7,w:11.6,h:5.0,fontSize:20,color:INK,align:"left",valign:"top"}); }

let b;
b=back("Are you overturning the paper? No — narrow scope");
bbul(b,["We re-tested only the snRNA-seq transcriptional zonation/plasticity evidence.",
  "We did NOT test imaging, protein staining, organoids, or 3D architecture.",
  "Claim: matched biopsy transcriptomes do not show progressive zonation loss.",
  "We agree with the paper that the strong signal is an end-stage phenomenon."]);

b=back("Maybe the caudate lobe caused it? Lobe-invariant");
img(b,"fig_lobe.png",{x:0.8,y:1.6,w:7.6,h:5.0});
b.addText([{text:"Detection rates match across Right / Caudate / Left.\n",options:{bold:true,breakLine:true}},
  {text:"Lobe does not explain the signal;\nexplant-vs-biopsy acquisition still does.",options:{}}],
  {x:8.7,y:2.6,w:4.0,h:2.5,fontSize:18,color:INK,align:"left"});

b=back("What happens in end-stage? Five organs, five phenotypes");
img(b,"fig_explant.png",{x:0.8,y:1.6,w:8.2,h:5.0});
b.addText([{text:"PC-anchor 3% → 50%;  PP:PC 0.13 → 20.\n",options:{bold:true,breakLine:true}},
  {text:"Dramatic but NOT one coherent program — pooling them manufactures a uniform “collapse.”",options:{}}],
  {x:9.2,y:2.6,w:3.6,h:2.6,fontSize:17,color:INK,align:"left"});

b=back("Why raw counts, not SCT?");
bbul(b,["SCT is great for clustering / visualization.",
  "But this question depends on molecule detection and ambient RNA.",
  "Raw counts + equal 1,500-UMI budget + ≥2-UMI threshold directly test marker co-detection.",
  "A single-UMI event can easily be ambient; ≥2 is more robust (not proof)."]);

b=back("Why pseudobulk, not per-cell DGE?");
bbul(b,["Cells from the same donor are not independent replicates (pseudoreplication).",
  "Pseudobulk sums raw counts per donor → one profile per donor.",
  "DGE then tests donor-level consistency (Squair et al. 2021).",
  "38 biopsy donors; F4 = 4 donors → F4-specific signals treated with caution."]);

b=back("Why abandon the relative correlation/spread ruler?");
bbul(b,["It was source-confounded (the collapse lived in the confounded endpoints).",
  "It was depth-sensitive (shallower F4 changes spread for non-biological reasons).",
  "It conflated co-expression, turn-off, noise, and composition shift.",
  "The count taxonomy separates these mechanisms; a Simpson/aggregation reversal confirmed the artifact."]);

b=back("Why not the 2D PC-vs-PP joint-count plot?");
bbul(b,["Broad metabolic program sums are ON in most normal hepatocytes.",
  "So “both programs high” is satisfied by normal cells — not a co-expression test.",
  "It is a pole-collapse visual (fuller in biopsy than explant).",
  "The clean metric is strict anchor dual at ≥2 UMI: ~0.4% biopsy vs ~2.9% explant."]);

b=back("DGE model details");
bbul(b,["Raw hepatocyte UMI counts summed per donor.",
  "filterByExpr retained 21,022 genes; TMM normalization.",
  "edgeR negative-binomial quasi-likelihood GLM, robust dispersion; common BCV 0.405.",
  "Primary contrast F4 vs F1; hits survive a run-covariate and a single-run sensitivity test."]);

b=back("Does decontX prove contamination? No");
bbul(b,["decontX models a native + ambient RNA mixture and subtracts the estimate.",
  "Hits 64 → 34; SOX4/SOX9 drop below significance → supports an ambient contribution.",
  "But it can remove true hybrid signal OR leave residual contamination.",
  "Therefore source attribution is a lead, not a closed verdict."]);

b=back("The one analysis still owed: gene-set testing");
bbul(b,["Gene-level FDR can miss a coordinated WEAK program (many genes, small shifts).",
  "CAMERA + ROAST on pre-specified sets: PC, PP, detox, urea cycle, bile-acid/lipid,",
  "mitochondrial, ER stress, interferon, hypoxia, EMT/fetal/progenitor, cholangiocyte/ductular.",
  "Closes the caveat behind “no other large hepatocyte program.”"]);

b=back("Robustness: sensitivity grid + equivalence bound");
img(b,"fig_tost.png",{x:6.6,y:1.7,w:6.4,h:4.0});
b.addText([{text:"Stable across every variant:\n",options:{bold:true,breakLine:true}},
  {text:"PC = GLUL-only / CYP3A4-only / both;  PP = 2-of-4 / 3-of-4;\nALDOB in/out;  CPS1-based;  threshold 1 vs 2 UMI.\n\n",options:{breakLine:true}},
  {text:"No PC depletion · no dual increase · no turn-off — in all.\n\n",options:{bold:true,color:BIOPSY,breakLine:true}},
  {text:"Bound: large shift (~20 pp) excluded; subtle drift ≤10 pp not excluded (F4 n=4).",options:{italic:true,color:MUTE}}],
  {x:0.7,y:1.9,w:5.7,h:4.2,fontSize:16,color:INK,align:"left",valign:"top"});

p.writeFile({fileName:__dirname+"/MASLD_zonation_reanalysis_8min.pptx"}).then(f=>console.log("WROTE",f));
