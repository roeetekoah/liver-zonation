// MASLD snRNA-seq hackathon deck. Kicker style (ALL-CAPS kicker + short headline), per
// the project's Zonation_Reanalysis.pptx. Run from here: node build_deck.js
const pptxgen = require("pptxgenjs");
const A = __dirname + "/assets/";

const PC="1D4ED8", PP="EA580C", DUAL="7C3AED", NULL="9CA3AF",
      BIOPSY="0D9488", CONFOUND="BE123C", ENDSTAGE="86198F", STRESS="DC2626", BILIARY="7C3AED",
      INK="1E293B", MUTE="6B6256", WHITE="FFFFFF",
      SLATE="1F3A3D", ORANGE="C0562B", CREAM="F7F3EB",
      KICK="C0562B", BG="F7F3EB", LIGHT="ECE6DA", DARK="14292C";
const SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});

const p=new pptxgen(); p.layout="LAYOUT_WIDE"; p.author="Roee Tekoah, Shira Gelbstein";
p.title="Matched biopsies preserve hepatocyte transcriptional zonation in MASLD";

// --- helpers: kicker + short headline; footer; figure caption; classification chip ---
function head(s,kicker,headline){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:12.0,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.85,fontSize:28,bold:true,color:SLATE,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
function foot(s,n){
  s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});
  s.addText(String(n),{x:12.2,y:7.12,w:0.6,h:0.3,fontSize:10.5,color:MUTE,align:"right",margin:0});
}
function img(s,file,box){ s.addImage({path:A+file,x:box.x,y:box.y,w:box.w,h:box.h,sizing:{type:"contain",w:box.w,h:box.h}}); }
function figcap(s,x,y,w,txt){ s.addText(txt,{x,y,w,h:0.4,fontSize:12,italic:true,color:MUTE,align:"center",margin:0}); }
function chip(s,x,y,w,h,txt,fill,tcol){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.08,shadow:sh()});
  s.addText(txt,{x,y,w,h,fontSize:14.5,bold:true,color:tcol||WHITE,align:"center",valign:"middle",margin:2});
}

// ============================================================ SLIDE 1 — TITLE
let s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:7.5,fill:{color:ORANGE}});
s.addText("LIVER GENOMICS  ·  SINGLE-NUCLEUS RE-ANALYSIS",
  {x:0.85,y:1.15,w:11.9,h:0.4,fontSize:15,bold:true,color:"9CB0AC",charSpacing:3,align:"left"});
s.addText("Matched biopsies preserve hepatocyte transcriptional zonation in MASLD",
  {x:0.85,y:1.7,w:11.6,h:1.7,fontSize:38,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"top"});
s.addText("A critical re-analysis of the single-nucleus RNA-seq in Gribben et al., Nature 2024 (GSE202379)",
  {x:0.85,y:3.55,w:11.6,h:0.5,fontSize:18,italic:true,color:"C9D6D3",align:"left"});
s.addShape(p.shapes.LINE,{x:0.85,y:4.55,w:5.0,h:0,line:{color:ORANGE,width:1.5}});
s.addText([{text:"Roee Tekoah",options:{bold:true}},{text:"   ·   ",options:{color:"7E8F8B"}},{text:"Shira Gelbstein",options:{bold:true}}],
  {x:0.85,y:4.75,w:11.6,h:0.45,fontSize:20,color:"EDE7DB",align:"left"});
s.addText("Computational Genomics (76553)  ·  Hebrew University of Jerusalem  ·  Hackathon",
  {x:0.85,y:5.3,w:11.6,h:0.4,fontSize:15,color:"9CB0AC",align:"left"});
s.addText("47 donors  ·  ~99,809 nuclei  ·  69,426 hepatocytes  ·  raw-count, donor-level analysis",
  {x:0.85,y:6.35,w:11.6,h:0.4,fontSize:13,color:"7E8F8B",align:"left"});
s.addNotes("Title slide. We are Roee Tekoah and Shira Gelbstein; this is our hackathon re-analysis of the single-nucleus RNA-seq in Gribben et al., Nature 2024, asking whether the evidence for progressive hepatocyte de-zonation in MASLD survives once tissue acquisition is controlled. One-line answer in the title: matched biopsies preserve transcriptional zonation.");

// ============================================================ SLIDE 2 — BACKGROUND
s=p.addSlide(); s.background={color:BG};
head(s,"BACKGROUND","Hepatocytes are transcriptionally zonated");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.0,y:1.85,w:5.2,h:0.55,fill:{color:PC},rectRadius:0.05});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.2,y:1.85,w:5.2,h:0.55,fill:{color:PP},rectRadius:0.05});
s.addText("Pericentral (zone 3)",{x:1.0,y:1.85,w:5.2,h:0.55,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
s.addText("Periportal (zone 1)",{x:6.2,y:1.85,w:5.2,h:0.55,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
s.addText("Central vein",{x:0.6,y:2.45,w:2.4,h:0.3,fontSize:12.5,color:MUTE,align:"left"});
s.addText("Portal tract",{x:9.4,y:2.45,w:2.4,h:0.3,fontSize:12.5,color:MUTE,align:"right"});
s.addText([{text:"GLUL, CYP3A4, CYP2E1 ",options:{bold:true,color:PC}},{text:"— drug metabolism (Wnt-driven)",options:{color:INK}}],
  {x:1.0,y:2.8,w:5.2,h:0.35,fontSize:14,align:"center"});
s.addText([{text:"ASS1, CPS1, PCK1, HAL, ALDOB ",options:{bold:true,color:PP}},{text:"— urea cycle",options:{color:INK}}],
  {x:6.2,y:2.8,w:5.2,h:0.35,fontSize:14,align:"center"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.0,y:3.75,w:10.4,h:1.9,fill:{color:"FEF2F2"},rectRadius:0.08,shadow:sh()});
s.addText("THE PUBLISHED CLAIM",{x:1.25,y:3.95,w:9.9,h:0.35,fontSize:13,bold:true,color:CONFOUND,charSpacing:2,align:"left"});
s.addText([{text:"“Hepatocytes lose their zonation.”  ",options:{bold:true,fontSize:19,color:INK}},
  {text:"Gribben et al. report that, as human MASLD progresses, hepatocytes co-express pericentral + periportal markers and transdifferentiate toward cholangiocytes (epithelial plasticity).",options:{fontSize:15,color:"334155"}}],
  {x:1.25,y:4.35,w:9.9,h:1.2,align:"left",valign:"top"});
foot(s,2);
s.addNotes("Minimal background: the liver lobule is zonated — pericentral hepatocytes (near the central vein) run one program (GLUL, CYP3A4, the CYP/detox genes), periportal hepatocytes (near the portal tract) run another (ASS1, CPS1, PCK1, urea cycle). Gribben et al.'s claim is that in MASLD hepatocytes lose this zonation and acquire cholangiocyte-like identity. That is what we test.");

// ============================================================ SLIDE 3 — THE QUESTION + PIVOT
s=p.addSlide(); s.background={color:BG};
head(s,"THE QUESTION","Disease — or how the tissue was taken?");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.0,y:1.85,w:10.4,h:1.5,fill:{color:LIGHT},rectRadius:0.08});
s.addText("Our research question",{x:1.25,y:2.0,w:9.9,h:0.35,fontSize:13,bold:true,color:KICK,charSpacing:2,align:"left"});
s.addText("Does hepatocyte zonation degrade across MASLD progression — and is that degradation linked to the hepatocyte→cholangiocyte transdifferentiation Paper 1 reported?",
  {x:1.25,y:2.4,w:9.9,h:0.9,fontSize:18,italic:true,color:INK,align:"left",valign:"top"});
s.addText("The pivot — how we test it",{x:1.0,y:3.75,w:10.4,h:0.35,fontSize:13,bold:true,color:KICK,charSpacing:2,align:"left"});
s.addText([
  {text:"Earlier, a relative / correlation ruler suggested a collapse — but it conflates sequencing depth, tissue source and biology.",options:{bullet:true,breakLine:true}},
  {text:"We instead count molecules: raw UMI counts, depth-normalized, with the donor (~47) as the unit of inference.",options:{bullet:true,breakLine:true,bold:true,color:BIOPSY}},
  {text:"And we test on the acquisition-matched needle-biopsy axis only (next slide explains why).",options:{bullet:true}}],
  {x:1.4,y:4.25,w:10.0,h:2.0,fontSize:18,color:INK,align:"left",paraSpaceAfter:8});
foot(s,3);
s.addNotes("The research question, posed as in our own project framing: does hepatocyte zonation degrade across MASLD, and is that linked to the transdifferentiation Paper 1 reported? The pivot is methodological — we abandoned a relative/correlation ruler (which conflates depth, tissue and biology) for raw molecule counts at the donor level, and we restrict to the acquisition-matched biopsy axis, which the next slide motivates.");

// ============================================================ SLIDE 4 — FAILURE MODES
s=p.addSlide(); s.background={color:BG};
head(s,"WHAT WE TEST","Zonation loss is not one mechanism");
s.addText("If the zonation expression signal breaks down, it can do so in distinct ways — each has its own count signature, which we test separately:",
  {x:0.7,y:1.6,w:12.0,h:0.7,fontSize:17,color:INK,align:"left"});
chip(s,1.0,2.6,2.6,1.2,"Depletion\n(a pole's cells lost)",PC);
chip(s,3.85,2.6,2.6,1.2,"Co-expression\n(both poles on)",DUAL);
chip(s,6.7,2.6,2.6,1.2,"Turn-off\n(neither pole on)",NULL,INK);
chip(s,9.55,2.6,2.85,1.2,"Composition shift\n(PP : PC ratio moves)",PP);
s.addText([{text:"We suspected pericentral depletion specifically — but ",options:{}},
  {text:"“depletion” is general",options:{bold:true}},
  {text:" (either pole, or both). We test each mechanism, not just the one we expected.",options:{}}],
  {x:1.0,y:4.2,w:11.0,h:0.6,fontSize:15,color:"334155",align:"left"});
s.addText("A single anti-correlation or UMAP impression conflates these — which is exactly the trap we avoid with absolute counts.",
  {x:1.0,y:5.1,w:11.0,h:0.6,fontSize:15,italic:true,color:MUTE,align:"left"});
foot(s,4);
s.addNotes("De-zonation is not one thing. Pericentral OR periportal cells could deplete; cells could co-express both poles; cells could turn both off; or the periportal-to-pericentral ratio could shift. We deliberately say 'depletion' generally — we suspected pericentral depletion and will show it is absent, but depletion is the general confounder and we test each mechanism. A single correlation score conflates them; counts separate them.");

// ============================================================ SLIDE 5 — THE CONFOUND
s=p.addSlide(); s.background={color:BG};
head(s,"THE CONFOUND","Stage is entangled with acquisition");
const xs=[1.0,2.55,3.85,5.15,6.45,7.75,9.5], lab=["Healthy","F0","F1","F2","F3","F4","End-stage"];
const colb=[CONFOUND,BIOPSY,BIOPSY,BIOPSY,BIOPSY,BIOPSY,ENDSTAGE], wd=[1.4,1.2,1.2,1.2,1.2,1.2,2.2];
for(let i=0;i<lab.length;i++){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:xs[i],y:1.95,w:wd[i],h:0.7,fill:{color:colb[i]},rectRadius:0.06,shadow:sh()});
  s.addText(lab[i],{x:xs[i],y:1.95,w:wd[i],h:0.7,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
}
s.addShape(p.shapes.LINE,{x:1.0,y:1.73,w:10.7,h:0,line:{color:MUTE,width:1.5,endArrowType:"triangle"}});
s.addText("deceased-donor\norgan cubes",{x:0.7,y:2.85,w:2.0,h:0.7,fontSize:13,color:CONFOUND,align:"center"});
s.addText("16-gauge needle biopsies, right lobe",{x:2.55,y:2.85,w:6.6,h:0.4,fontSize:14,bold:true,color:BIOPSY,align:"center"});
s.addText("explanted cirrhotic\norgans, multi-lobe",{x:9.5,y:2.85,w:2.2,h:0.7,fontSize:13,color:ENDSTAGE,align:"center"});
s.addShape(p.shapes.RECTANGLE,{x:0.95,y:1.9,w:1.5,h:1.75,fill:{type:"none"},line:{color:CONFOUND,width:2,dashType:"dash"}});
s.addShape(p.shapes.RECTANGLE,{x:9.45,y:1.9,w:2.3,h:1.75,fill:{type:"none"},line:{color:CONFOUND,width:2,dashType:"dash"}});
s.addText("not acquisition-matched",{x:8.8,y:3.7,w:3.0,h:0.3,fontSize:12,bold:true,color:CONFOUND,align:"center"});
s.addText("47 donors   ·   biopsy axis F0/F1/F2/F3/F4 = 2 / 8 / 12 / 12 / 4   ·   end-stage = 5   ·   healthy = 4",
  {x:1.0,y:4.25,w:11.0,h:0.4,fontSize:16,bold:true,color:INK,align:"center"});
s.addText("Primary inference: biopsy F1–F4 (F0 n=2 shown for context).",
  {x:1.0,y:4.72,w:11.0,h:0.35,fontSize:14,italic:true,color:BIOPSY,align:"center"});
s.addText([
  {text:"The full trajectory is also an acquisition trajectory.",options:{bullet:true,breakLine:true}},
  {text:"So healthy / end-stage comparisons cannot cleanly isolate disease biology — we use biopsy-only F1–F4.",options:{bullet:true,bold:true,color:BIOPSY}}],
  {x:1.7,y:5.25,w:10.0,h:1.2,fontSize:18,color:INK,align:"left",paraSpaceAfter:5});
foot(s,5);
s.addNotes("The load-bearing point. Disease stage is collinear with how the tissue was obtained: healthy and end-stage are deceased-donor organ tissue and explants; F0–F4 are needle biopsies. So a 'progressive' trajectory can be manufactured by procurement, ischemia, dissociation or batch. We restrict the disease axis to the matched biopsies, F1–F4.");

// ============================================================ SLIDE 6 — STRESS
s=p.addSlide(); s.background={color:BG};
head(s,"WHY IT MATTERS","Endpoints carry organ-wide stress");
img(s,"fig_stress.png",{x:0.3,y:1.5,w:9.0,h:4.3});
figcap(s,0.3,5.85,9.0,"Figure 1.  Procurement-stress module by tissue source (donor-level); the same immediate-early spike appears in non-zonated endothelium.");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.5,y:1.65,w:3.5,h:1.45,fill:{color:"FEF2F2"},rectRadius:0.08,shadow:sh()});
s.addText("Same stress spike in hepatocytes AND endothelium",
  {x:9.6,y:1.72,w:3.3,h:1.3,fontSize:16,bold:true,color:STRESS,align:"left",valign:"middle"});
s.addText([
  {text:"FOS, JUN, JUNB, JUND, ATF3, DUSP1, HSPA1A/B.",options:{bullet:true,breakLine:true}},
  {text:"Endothelium has no zonation program.",options:{bullet:true,breakLine:true,bold:true}},
  {text:"→ acquisition / procurement signal, not zonation biology.",options:{bullet:true,color:STRESS,bold:true}}],
  {x:9.55,y:3.35,w:3.45,h:2.6,fontSize:15.5,color:INK,align:"left",paraSpaceAfter:8});
foot(s,6);
s.addNotes("The decisive cross-lineage control: stress is ~22x higher in end-stage explants than biopsies — but endothelial cells, which have no zonation program, show the same ~18x immediate-early spike as hepatocytes. So this is organ-wide acute handling stress, not a hepatocyte zonation program — which justifies excluding the deceased-donor and explant endpoints.");

// ============================================================ SLIDE 7 — METHOD
s=p.addSlide(); s.background={color:BG};
head(s,"HOW WE MEASURE","Raw-count anchor classification");
const steps=["raw UMI counts","down-thin to 1,500","marker ON if ≥ 2 UMI","classify nucleus","fraction per donor"];
let px=0.6; for(let i=0;i<steps.length;i++){ const w=2.35;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:px,y:1.7,w:w,h:0.8,fill:{color:i==2?"EDE9FE":LIGHT},line:{color:i==2?DUAL:"CBD5E1",width:1.2},rectRadius:0.07});
  s.addText(steps[i],{x:px,y:1.7,w:w,h:0.8,fontSize:14,bold:i==2,color:i==2?DUAL:INK,align:"center",valign:"middle",margin:3});
  if(i<steps.length-1) s.addShape(p.shapes.LINE,{x:px+w,y:2.1,w:0.22,h:0,line:{color:MUTE,width:1.6,endArrowType:"triangle"}});
  px+=w+0.22; }
chip(s,1.0,3.1,2.7,1.0,"PC-anchor\nPC on / PP off",PC);
chip(s,4.0,3.1,2.7,1.0,"PP-anchor\nPP on / PC off",PP);
chip(s,7.0,3.1,2.7,1.0,"Dual\nboth programs on",DUAL);
chip(s,10.0,3.1,2.3,1.0,"Null\nneither on",NULL,INK);
s.addText([
  {text:"Why raw counts: ",options:{bold:true}},{text:"a single KRT19 or GLUL molecule may be ambient — absolute detection matters, so SCT-normalized values are the wrong object.\n",options:{breakLine:true}},
  {text:"≥2-UMI threshold ",options:{bold:true,color:DUAL}},{text:"suppresses single-molecule ambient.    ",options:{}},
  {text:"Unit = donor (~47), never the nucleus ",options:{bold:true,color:BIOPSY}},{text:"→ no pseudoreplication.\n",options:{breakLine:true}},
  {text:"Robust across the sensitivity grid ",options:{bold:true}},{text:"(anchor genes, periportal rule, ALDOB in/out, 1 vs 2 UMI).",options:{}}],
  {x:1.0,y:4.5,w:11.6,h:1.9,fontSize:16,color:INK,align:"left",valign:"top",paraSpaceAfter:7});
foot(s,7);
s.addNotes("Why raw counts: a single marker molecule may be ambient, so absolute molecule detection matters and SCT-normalized values are the wrong object. We down-thin every nucleus to a common 1,500-UMI budget, call a marker on only at >=2 UMIs, classify each hepatocyte PC/PP/dual/null, and infer at the donor level (~47) to avoid pseudoreplication. Robust across the marker/threshold sensitivity grid.");

// ============================================================ SLIDE 8 — RESULT
s=p.addSlide(); s.background={color:BG};
head(s,"THE RESULT","Matched biopsies stay zonated");
img(s,"fig_result3.png",{x:0.2,y:1.55,w:9.1,h:4.1});
figcap(s,0.2,5.75,9.1,"Figure 2.  Pericentral and periportal depletion and dual co-expression across matched biopsy F1–F4 (donor=point, value-labelled; F0 n=2 in backup).");
s.addText([
  {text:"The other two mechanisms (F1→F4 donor-median):\n",options:{bold:true,color:SLATE,breakLine:true}},
  {text:"Null (turn-off): ",options:{bold:true,color:"475569"}},{text:"44 / 36 / 39 / 39% — stable.\n",options:{breakLine:true}},
  {text:"PP : PC ratio: ",options:{bold:true,color:PP}},{text:"1.16 / 1.01 / 1.10 / 1.18 — flat.\n\n",options:{breakLine:true}},
  {text:"Bound: ",options:{bold:true,color:PC}},{text:"a large shift (~20 pp) is excluded; a subtle drift ≤10 pp is not (F4 n=4).",options:{italic:true,color:MUTE}}],
  {x:9.45,y:1.65,w:3.65,h:3.5,fontSize:15,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.45,y:5.35,w:3.65,h:0.95,fill:{color:SLATE},rectRadius:0.08,shadow:sh()});
s.addText("Anchor fractions do not support large biopsy-axis de-zonation.",
  {x:9.6,y:5.4,w:3.35,h:0.85,fontSize:15,bold:true,color:"FFFFFF",align:"left",valign:"middle"});
foot(s,8);
s.addNotes("The core result. Pericentral-anchor fraction is flat/non-monotone across F0-F4 — no depletion. Dual co-expression at the ambient-robust >=2-UMI cut stays ~0.4% and does not trend (vs ~2.9% in the confounded explants). Null and PP:PC are also flat. The equivalence bound excludes a large ~20-percentage-point shift but cannot exclude subtle drift below ~10 points (F4 n=4).");

// ============================================================ SLIDE 9 — GENOME-WIDE
s=p.addSlide(); s.background={color:BG};
head(s,"GENOME-WIDE","One signal: biliary markers");
img(s,"fig_volcano.png",{x:0.3,y:1.5,w:8.7,h:4.5});
figcap(s,0.3,6.05,8.7,"Figure 3.  Genome-wide pseudobulk differential expression, cirrhotic F4 vs F1 (edgeR).");
s.addText([
  {text:"Pseudobulk per donor; edgeR TMM + NB quasi-likelihood.\n",options:{breakLine:true}},
  {text:"64 genes FDR<0.05 — mostly biliary/ductular.\n",options:{bold:true,breakLine:true}},
  {text:"Zonation genes not significant (GLUL FDR 0.80).\n",options:{color:PC,breakLine:true}},
  {text:"“No large single-gene program outside the biliary burden.”",options:{italic:true,color:BILIARY}}],
  {x:9.2,y:1.8,w:3.8,h:3.4,fontSize:16,color:INK,align:"left",valign:"top",paraSpaceAfter:8});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.2,y:5.5,w:3.8,h:0.8,fill:{color:LIGHT},rectRadius:0.06});
s.addText("Caveat: weak coordinated pathways still need gene-set testing.",
  {x:9.35,y:5.55,w:3.5,h:0.7,fontSize:13,italic:true,color:MUTE,align:"left",valign:"middle"});
foot(s,9);
s.addNotes("Pseudobulk per donor — donors, not cells, are the replicates. This is an independent count-based check (zonation genes flat, GLUL FDR 0.80) plus a discovery layer: only 64 of ~21,000 genes are significant, and they are biliary/ductular markers, not a broad program. Careful wording: no large single-GENE program outside the biliary burden — gene-set testing is still owed for weak coordinated pathways.");

// ============================================================ SLIDE 10 — SOURCE
s=p.addSlide(); s.background={color:BG};
head(s,"SOURCE","The biliary burden looks compositional");
img(s,"fig_compositional.png",{x:0.3,y:1.5,w:12.7,h:3.9});
figcap(s,0.3,5.45,12.7,"Figure 4.  Source attribution — cross-lineage abundance, decontX ambient removal, and the F4 ductular reaction.");
s.addText([
  {text:"Strong: ",options:{bold:true,color:"065F46"}},{text:"biliary genes far more abundant in cholangiocytes; hepatocyte co-expression rare (~0.4%).   ",options:{}},
  {text:"Suggestive: ",options:{bold:true,color:"B45309"}},{text:"decontX halves the hits (ambient contribution — not proof).   ",options:{}},
  {text:"Open: ",options:{bold:true,color:CONFOUND}},{text:"EPCAM/SPINT2/B3GNT3 survive.  ",options:{}},
  {text:"CXCL10 = possible real inflammation (does not track cholangiocytes).",options:{color:STRESS,bold:true}}],
  {x:0.6,y:5.95,w:12.2,h:1.0,fontSize:15,color:INK,align:"left"});
foot(s,10);
s.addNotes("Distinguish evidence levels. Strong: the genes are 5-78x more abundant in cholangiocytes and per-cell hepatocyte co-expression is ~0.4%. Suggestive: decontX halves the hits and drops SOX4/SOX9 — supports an ambient contribution but is not proof. Open: EPCAM/SPINT2/B3GNT3 survive. So the dominant evidence points to composition/ambient RNA, but a rare intrinsic state is not excluded; CXCL10 is set aside as a candidate real inflammatory signal.");

// ============================================================ SLIDE 11 — CONCLUSION
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:7.5,fill:{color:ORANGE}});
s.addShape(p.shapes.RECTANGLE,{x:0.85,y:0.5,w:0.16,h:0.26,fill:{color:ORANGE}});
s.addText("CONCLUSION",{x:1.08,y:0.46,w:11.5,h:0.4,fontSize:14,bold:true,color:ORANGE,charSpacing:3,align:"left"});
s.addText("Preservation, not progressive collapse",
  {x:0.85,y:0.85,w:11.6,h:0.8,fontSize:30,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
const cols=[
  {h:"Conclusions",c:"F0B27A",items:["Full healthy→end-stage trajectory is source-confounded.","In biopsy F1–F4, hepatocyte transcriptional zonation is preserved.","Main DGE signal = biliary/ductular burden, most consistent with composition / ambient RNA."]},
  {h:"Limits",c:"FCA5A5",items:["snRNA-seq ≠ lobule geometry / spatial architecture.","Imaging / protein / organoid evidence not re-analyzed.","F4 has only 4 biopsy donors.","Gene-level DGE can miss weak coordinated pathways."]},
  {h:"Next",c:"9CC6CC",items:["CAMERA / ROAST gene-set tests.","Leave-one-F4-donor-out DGE.","Quantitative contamination model.","Spatial / independent biopsy validation."]}
];
let cx=0.85; for(const col of cols){ const cw=3.85;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:cx,y:1.75,w:cw,h:4.3,fill:{color:"1E3A3D"},rectRadius:0.08,shadow:sh()});
  s.addText(col.h,{x:cx,y:1.9,w:cw,h:0.5,fontSize:20,bold:true,color:col.c,fontFace:SERIF,align:"center"});
  s.addText(col.items.map(t=>({text:t,options:{bullet:true,color:"E2E8F0",breakLine:true,paraSpaceAfter:9}})),
    {x:cx+0.25,y:2.5,w:cw-0.45,h:3.4,fontSize:14.5,align:"left",valign:"top"});
  cx+=cw+0.25; }
s.addText("The snRNA-seq transcriptomic evidence for progressive de-zonation does not survive matched-source re-analysis.",
  {x:0.7,y:6.4,w:11.9,h:0.65,fontSize:17,bold:true,italic:true,color:WHITE,align:"center"});
foot(s,11);
s.addNotes("Close on the methodological lesson: in single-cell disease atlases, acquisition matching can dominate apparent disease trajectories. Bottom line, narrow and honest: the snRNA-seq transcriptomic evidence for progressive de-zonation does not survive matched-source re-analysis; imaging/protein/organoid evidence is untouched; the biliary burden is most consistent with composition/ambient RNA, a rare intrinsic state not excluded.");

// ============================================================ BACKUPS
function back(kicker,t){ const b=p.addSlide(); b.background={color:BG};
  b.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  b.addText("BACKUP  ·  "+kicker,{x:0.74,y:0.30,w:12.0,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3});
  b.addText(t,{x:0.48,y:0.64,w:12.4,h:0.8,fontSize:26,bold:true,color:SLATE,fontFace:SERIF,align:"left"}); return b; }
function bbul(b,items,y){ b.addText(items.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:9}})),
  {x:0.8,y:y||1.6,w:11.6,h:5.0,fontSize:20,color:INK,align:"left",valign:"top"}); }
let b;

b=back("DE-ZONATION MECHANISMS","Full four-mechanism panel (F0–F4)");
img(b,"fig_anchor2x2.png",{x:1.3,y:1.5,w:9.2,h:5.0});
figcap(b,1.3,6.5,9.2,"Figure 5.  Depletion, co-expression, turn-off and composition across biopsy fibrosis — none shows a large monotone change.");
b.addText([{text:"None of the four routes shows a large monotone biopsy-axis change.\n\n",options:{bold:true,breakLine:true}},
  {text:"Confounded explants: dual ≈ 2.9% (~7×).",options:{color:CONFOUND}}],
  {x:10.7,y:2.6,w:2.4,h:3.0,fontSize:15,color:INK,align:"left"});

b=back("SCOPE","Are you overturning the paper? No");
bbul(b,["We re-tested only the snRNA-seq transcriptional zonation/plasticity evidence.",
  "We did NOT test imaging, protein staining, organoids, or 3D architecture.",
  "Claim: matched biopsy transcriptomes do not show progressive zonation loss.",
  "We agree the strong signal is an end-stage phenomenon."]);

b=back("LOBE","Caudate lobe? Lobe-invariant");
img(b,"fig_lobe.png",{x:0.8,y:1.5,w:7.6,h:5.0});
figcap(b,0.8,6.5,7.6,"Figure 6.  Zonation-marker detection across Right / Caudate / Left lobes in end-stage explants.");
b.addText([{text:"Detection matches across lobes.\n",options:{bold:true,breakLine:true}},
  {text:"Lobe does not explain the signal; explant-vs-biopsy acquisition still does.",options:{}}],
  {x:8.7,y:2.6,w:4.0,h:2.5,fontSize:18,color:INK,align:"left"});

b=back("END-STAGE","Five organs, five phenotypes");
img(b,"fig_explant.png",{x:0.8,y:1.5,w:8.2,h:5.0});
figcap(b,0.8,6.5,8.2,"Figure 7.  Per-explant anchor fractions — end-stage is heterogeneous, not one coherent program.");
b.addText([{text:"PC-anchor 3% → 50%;  PP:PC 0.13 → 20.\n",options:{bold:true,breakLine:true}},
  {text:"Dramatic but NOT one program — pooling manufactures a uniform “collapse.”",options:{}}],
  {x:9.2,y:2.6,w:3.6,h:2.6,fontSize:17,color:INK,align:"left"});

b=back("ROBUSTNESS","Sensitivity grid + equivalence bound");
img(b,"fig_tost.png",{x:6.6,y:1.6,w:6.4,h:4.0});
figcap(b,6.6,5.65,6.4,"Figure 8.  Equivalence bound on the F4-vs-F1 pericentral-anchor change.");
b.addText([{text:"Stable across every variant:\n",options:{bold:true,breakLine:true}},
  {text:"anchor genes, periportal rule, ALDOB in/out, CPS1-based, 1 vs 2 UMI.\n\n",options:{breakLine:true}},
  {text:"No depletion · no dual rise · no turn-off — in all.\n\n",options:{bold:true,color:BIOPSY,breakLine:true}},
  {text:"Bound: large shift (~20 pp) excluded; subtle drift ≤10 pp not (F4 n=4).",options:{italic:true,color:MUTE}}],
  {x:0.7,y:1.8,w:5.7,h:4.2,fontSize:16,color:INK,align:"left",valign:"top"});

b=back("METHODS","Why raw counts, why pseudobulk");
bbul(b,["Raw counts: marker co-detection + ambient sensitivity need molecules, not SCT residuals.",
  "Pseudobulk: cells from one donor are not independent — sum per donor, then edgeR (Squair 2021).",
  "edgeR: filterByExpr → 21,022 genes; TMM; NB quasi-likelihood GLM, robust dispersion; common BCV 0.405.",
  "Primary signal persists in DIRECTION with a run covariate and within a single run; significance attenuates with n (not a batch artifact)."]);

b=back("AMBIENT","Does decontX prove contamination? No");
bbul(b,["decontX models a native + ambient RNA mixture and subtracts the estimate.",
  "Hits 64 → 34; SOX4/SOX9 drop below significance → supports an ambient contribution.",
  "But it can remove true hybrid signal OR leave residual contamination.",
  "Source attribution is a lead, not a closed verdict; CXCL10 is a separate candidate inflammatory signal."]);

b=back("NEXT","The one analysis still owed: gene-set testing");
bbul(b,["Gene-level FDR can miss a coordinated WEAK program (many genes, small shifts).",
  "CAMERA + ROAST on pre-specified sets: PC, PP, detox, urea cycle, bile-acid/lipid,",
  "mitochondrial, ER stress, interferon, hypoxia, EMT/fetal/progenitor, cholangiocyte/ductular.",
  "Closes the caveat behind “no other large hepatocyte program.”"]);

p.writeFile({fileName:__dirname+"/MASLD_zonation.pptx"}).then(f=>console.log("WROTE",f));
