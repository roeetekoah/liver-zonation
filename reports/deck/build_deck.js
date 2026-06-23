// 8-minute deck: critical snRNA-seq re-analysis of Gribben et al. Nature 2024.
// 9 main slides (one focus each) + backup appendix. Run from repo root or here: node build_deck.js
const pptxgen = require("pptxgenjs");
const A = __dirname + "/assets/";

const PC="1D4ED8", PP="EA580C", DUAL="7C3AED", NULL="9CA3AF",
      BIOPSY="0D9488", CONFOUND="BE123C", ENDSTAGE="86198F", STRESS="DC2626", BILIARY="7C3AED",
      INK="1E293B", MUTE="64748B", BG="FFFFFF", LIGHT="F1F5F9", DARK="0F172A", WHITE="FFFFFF";
const TITLE_FS=30, SMALL_FS=15, FOOT_FS=11, NMAIN=9;
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});

const p=new pptxgen(); p.layout="LAYOUT_WIDE"; p.author="MASLD re-analysis";
p.title="Matched biopsies preserve hepatocyte transcriptional zonation in MASLD";

function title(s,t,sub){
  s.addText(t,{x:0.5,y:0.30,w:12.3,h:0.85,fontSize:TITLE_FS,bold:true,color:INK,align:"left",valign:"middle",margin:0});
  if(sub) s.addText(sub,{x:0.5,y:1.12,w:12.3,h:0.4,fontSize:SMALL_FS,italic:true,color:MUTE,align:"left",margin:0});
}
function foot(s,n,tag){ s.addText(`${tag}     ·     ${n}`,{x:0.5,y:7.08,w:12.3,h:0.32,fontSize:FOOT_FS,color:MUTE,align:"left",margin:0}); }
function img(s,file,box){ s.addImage({path:A+file,x:box.x,y:box.y,w:box.w,h:box.h,sizing:{type:"contain",w:box.w,h:box.h}}); }
function chip(s,x,y,w,h,txt,fill,tcol){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.08,shadow:sh()});
  s.addText(txt,{x,y,w,h,fontSize:SMALL_FS,bold:true,color:tcol||WHITE,align:"center",valign:"middle",margin:2});
}

// ===================================================================== SLIDE 1
let s=p.addSlide(); s.background={color:DARK};
s.addText("Matched biopsies preserve hepatocyte transcriptional zonation in MASLD",
  {x:0.7,y:0.6,w:11.9,h:1.6,fontSize:38,bold:true,color:WHITE,align:"left",valign:"top"});
s.addText("A critical re-analysis of Gribben et al., Nature 2024 — snRNA-seq, GSE202379",
  {x:0.7,y:2.2,w:11.9,h:0.5,fontSize:18,italic:true,color:"CBD5E1",align:"left"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:3.0,w:5.5,h:1.7,fill:{color:"3F1D2B"},line:{color:CONFOUND,width:1.5},rectRadius:0.1});
s.addText([{text:"The research question (Gribben et al., Nature 2024)\n",options:{bold:true,color:"FCA5A5",fontSize:14.5}},
  {text:"Published claim: “Hepatocytes lose their zonation.”  Does hepatocyte zonation degrade across MASLD — and is that degradation linked to the hepatocyte→cholangiocyte transdifferentiation Paper 1 reported?",options:{color:"FECACA",fontSize:13}}],
  {x:0.9,y:3.1,w:5.1,h:1.5,align:"left",valign:"middle"});
s.addShape(p.shapes.RIGHT_TRIANGLE,{x:6.35,y:3.65,w:0.55,h:0.35,fill:{color:"94A3B8"}});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.1,y:3.0,w:5.5,h:1.7,fill:{color:"0B3B38"},line:{color:BIOPSY,width:1.5},rectRadius:0.1});
s.addText([{text:"Our answer — matched biopsies\n",options:{bold:true,color:"5EEAD4",fontSize:14.5}},
  {text:"No detectable biopsy-stage degradation (F1→cirrhotic F4); the “healthy→end-stage” drop is the tissue-acquisition axis; the transdifferentiation link can’t be established (biliary markers rise only in explants).",options:{color:"99F6E4",fontSize:13}}],
  {x:7.3,y:3.1,w:5.1,h:1.5,align:"left",valign:"middle"});
s.addText([
  {text:"In one line  ",options:{bold:true,color:"5EEAD4"}},{text:"the apparent de-zonation is a tissue-acquisition artifact; matched biopsies stay transcriptionally zonated.\n",options:{color:"E2E8F0",breakLine:true}},
  {text:"Scope  ",options:{bold:true,color:"CBD5E1"}},{text:"transcriptomic re-analysis only; imaging / organoids not re-tested.",options:{color:"E2E8F0"}}],
  {x:0.7,y:5.15,w:11.9,h:1.5,fontSize:18,align:"left",valign:"top",paraSpaceAfter:10});
s.addNotes("Frame it as the project's research question (from the Zonation_Reanalysis framing): the published claim is 'hepatocytes lose their zonation,' and our formal question was whether we can measure how much hepatocyte zonation degrades across MASLD and whether that is linked to the transdifferentiation Paper 1 reported. Answer, clause by clause: the relative ruler is the wrong instrument; there is no detectable biopsy-stage degradation (F1→cirrhotic F4); the healthy→end-stage drop is the tissue-acquisition axis, not disease; and the transdifferentiation link can't be established because biliary markers stay ~0 across biopsy disease and rise only in explants — the same confound.");

// ===================================================================== SLIDE 2
s=p.addSlide(); s.background={color:BG};
title(s,"Loss of the zonation expression signal is not one mechanism");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.0,y:1.75,w:5.2,h:0.55,fill:{color:PC},rectRadius:0.05});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.2,y:1.75,w:5.2,h:0.55,fill:{color:PP},rectRadius:0.05});
s.addText("Central vein",{x:0.6,y:2.35,w:2.4,h:0.3,fontSize:13,color:MUTE,align:"left"});
s.addText("Portal tract",{x:9.4,y:2.35,w:2.4,h:0.3,fontSize:13,color:MUTE,align:"right"});
s.addText("Pericentral program",{x:1.0,y:1.75,w:5.2,h:0.55,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
s.addText("Periportal program",{x:6.2,y:1.75,w:5.2,h:0.55,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle"});
s.addText([{text:"Example PC markers: ",options:{bold:true,color:PC}},{text:"GLUL, CYP3A4, CYP2E1 / detox",options:{color:INK}},
  {text:"     (anchor markers used: GLUL, CYP3A4)",options:{italic:true,color:MUTE,fontSize:12}}],
  {x:1.0,y:2.62,w:10.4,h:0.35,fontSize:14,align:"left"});
s.addText([{text:"Example PP markers: ",options:{bold:true,color:PP}},{text:"ASS1, CPS1, PCK1, HAL, ALDOB / urea cycle, gluconeogenesis",options:{color:INK}}],
  {x:1.0,y:2.97,w:10.4,h:0.35,fontSize:14,align:"left"});
s.addText("De-zonation (within hepatocytes) can take several forms — count signatures distinguish them:",
  {x:1.0,y:3.6,w:10.6,h:0.4,fontSize:17,bold:true,color:INK,align:"left"});
chip(s,1.0,4.15,2.5,1.1,"PC depletion\n(pericentral cells lost)",PC);
chip(s,3.75,4.15,2.5,1.1,"Co-expression\n(both poles on)",DUAL);
chip(s,6.5,4.15,2.5,1.1,"Turn-off\n(neither pole on)",NULL,INK);
chip(s,9.25,4.15,2.15,1.1,"Composition shift\n(PP : PC changes)",PP);
s.addText("A single anti-correlation or UMAP impression conflates these. We test each with absolute counts. (Transdifferentiation — a different, cross-cell-type axis — is on slide 8.)",
  {x:1.0,y:5.55,w:10.6,h:0.7,fontSize:14.5,italic:true,color:MUTE,align:"left"});
foot(s,`2 / ${NMAIN}`,"Minimal context");
s.addNotes("Only what's needed: zonation = different hepatocytes run different programs by lobule position. The zonation EXPRESSION signal can break down several ways — cells disappear, turn markers off, co-express both poles, or shift composition. We list CYP2E1 as a familiar pericentral marker, but the strict ANCHOR classification uses GLUL and CYP3A4 only. A single correlation score or UMAP conflates these mechanisms, so we use count signatures tied to each.");

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
s.addText("deceased-donor\norgan cubes",{x:0.7,y:2.9,w:2.0,h:0.7,fontSize:13,color:CONFOUND,align:"center"});
s.addText("16-gauge needle biopsies, right lobe",{x:2.55,y:2.9,w:6.6,h:0.4,fontSize:14,bold:true,color:BIOPSY,align:"center"});
s.addText("explanted cirrhotic\norgans, multi-lobe",{x:9.5,y:2.9,w:2.2,h:0.7,fontSize:13,color:ENDSTAGE,align:"center"});
s.addShape(p.shapes.RECTANGLE,{x:0.95,y:1.95,w:1.5,h:1.75,fill:{type:"none"},line:{color:CONFOUND,width:2,dashType:"dash"}});
s.addShape(p.shapes.RECTANGLE,{x:9.45,y:1.95,w:2.3,h:1.75,fill:{type:"none"},line:{color:CONFOUND,width:2,dashType:"dash"}});
s.addText("not acquisition-matched",{x:8.8,y:3.75,w:3.0,h:0.3,fontSize:12,bold:true,color:CONFOUND,align:"center"});
s.addText("47 donors   ·   biopsy axis F0/F1/F2/F3/F4 = 2 / 8 / 12 / 12 / 4   ·   end-stage = 5   ·   healthy = 4",
  {x:1.0,y:4.3,w:11.0,h:0.4,fontSize:16,bold:true,color:INK,align:"center"});
s.addText("Primary inference: biopsy F1–F4.  F0 (n=2) shown for context.",
  {x:1.0,y:4.78,w:11.0,h:0.35,fontSize:14,italic:true,color:BIOPSY,align:"center"});
s.addText([
  {text:"The full trajectory is also an acquisition trajectory.",options:{bullet:true,breakLine:true}},
  {text:"Healthy / end-stage comparisons cannot cleanly isolate disease biology.",options:{bullet:true,breakLine:true}},
  {text:"Clean axis used here: biopsy-only F1–F4.",options:{bullet:true,bold:true,color:BIOPSY}}],
  {x:1.7,y:5.3,w:10.0,h:1.4,fontSize:18,color:INK,align:"left",paraSpaceAfter:5});
foot(s,`3 / ${NMAIN}`,"The load-bearing confound");
s.addNotes("This is the load-bearing slide. If stage and acquisition are collinear, a progressive trajectory can be manufactured by procurement, ischemia, dissociation, or batch — not biology. Healthy and end-stage are deceased-donor / explant organ tissue; the disease spectrum F0–F4 is fresh needle biopsies. We restrict the disease axis to matched biopsies. On F0 vs F1–F4: F0 has only 2 donors, so primary inference is F1–F4; we show F0 descriptively.");

// ===================================================================== SLIDE 4
s=p.addSlide(); s.background={color:BG};
title(s,"Endpoint samples carry an organ-wide stress signature");
img(s,"fig_stress.png",{x:0.3,y:1.55,w:9.0,h:4.5});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.4,y:1.7,w:3.6,h:1.5,fill:{color:"FEF2F2"},rectRadius:0.08,shadow:sh()});
s.addText("Same immediate-early stress spike in hepatocytes AND endothelial cells",
  {x:9.5,y:1.78,w:3.4,h:1.35,fontSize:16,bold:true,color:STRESS,align:"left",valign:"middle"});
s.addText([
  {text:"Stress genes: FOS, JUN, JUNB, JUND, ATF3, DUSP1, HSPA1A/B.",options:{bullet:true,breakLine:true}},
  {text:"Endothelial cells have no zonation program.",options:{bullet:true,breakLine:true,bold:true}},
  {text:"→ acquisition / procurement signal, not hepatocyte zonation biology.",options:{bullet:true,color:STRESS,bold:true}}],
  {x:9.45,y:3.45,w:3.7,h:2.8,fontSize:16,color:INK,align:"left",paraSpaceAfter:9});
foot(s,`4 / ${NMAIN}`,"Stress validates the confound  ·  donor-level, down-thinned to 1,500 UMIs");
s.addNotes("The decisive point is cross-lineage. Stress is ~22× higher in end-stage explants than biopsies — but if endothelial cells, which have NO zonation program, show the same immediate-early spike (18.2× vs 18.5× in hepatocytes), this cannot be a hepatocyte zonation program. It is organ-wide acute handling/procurement stress. That justifies excluding the deceased-donor and explant groups from the disease axis.");

// ===================================================================== SLIDE 5 (methods)
s=p.addSlide(); s.background={color:BG};
title(s,"We test zonation with raw counts at the donor level, not a relative ruler");
const steps=["raw UMI counts","down-thin every nucleus to 1,500","marker ON only if ≥ 2 UMI","classify each nucleus","fraction per donor"];
let px=0.6; for(let i=0;i<steps.length;i++){ const w=2.35;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:px,y:1.75,w:w,h:0.85,fill:{color:i==2?"EDE9FE":LIGHT},line:{color:i==2?DUAL:"CBD5E1",width:1.2},rectRadius:0.07});
  s.addText(steps[i],{x:px,y:1.75,w:w,h:0.85,fontSize:14,bold:i==2,color:i==2?DUAL:INK,align:"center",valign:"middle",margin:3});
  if(i<steps.length-1) s.addShape(p.shapes.LINE,{x:px+w,y:2.17,w:0.22,h:0,line:{color:MUTE,width:1.6,endArrowType:"triangle"}});
  px+=w+0.22; }
// classification chips
chip(s,1.0,3.2,2.7,1.0,"PC-anchor\nPC on / PP off",PC);
chip(s,4.0,3.2,2.7,1.0,"PP-anchor\nPP on / PC off",PP);
chip(s,7.0,3.2,2.7,1.0,"Dual\nboth programs on",DUAL);
chip(s,10.0,3.2,2.3,1.0,"Null\nneither on",NULL,INK);
s.addText([
  {text:"Why raw counts: ",options:{bold:true}},{text:"a single KRT19 or GLUL molecule may be ambient RNA — absolute detection matters, so SCT-normalized values are the wrong object.\n",options:{breakLine:true}},
  {text:"≥2-UMI threshold ",options:{bold:true,color:DUAL}},{text:"suppresses single-molecule ambient artifacts.   ",options:{}},
  {text:"Unit = donor (~47), never the nucleus ",options:{bold:true,color:BIOPSY}},{text:"→ no pseudoreplication.\n",options:{breakLine:true}},
  {text:"Robust across the sensitivity grid ",options:{bold:true}},{text:"(anchor genes, periportal rule, ALDOB in/out, CPS1-based, 1 vs 2 UMI).",options:{}}],
  {x:1.0,y:4.55,w:11.6,h:1.9,fontSize:16,color:INK,align:"left",valign:"top",paraSpaceAfter:7});
foot(s,`5 / ${NMAIN}`,"Method  ·  count-based anchor classification");
s.addNotes("Why we changed the measurement: the legacy approach used a z-scored relative ruler and marker correlations, which are depth-sensitive and conflate mechanisms. We instead count molecules: extract raw RNA-assay counts, down-thin every nucleus to a common 1,500-UMI budget so detection reflects biology not depth, call a marker on only at ≥2 UMIs to suppress ambient, classify each hepatocyte PC/PP/dual/null, and summarize per donor — the donor is the unit of inference, never the cell.");

// ===================================================================== SLIDE 6 (result)
s=p.addSlide(); s.background={color:BG};
title(s,"Matched biopsies do not show PC loss or robust co-expression");
img(s,"fig_result2.png",{x:0.3,y:1.5,w:8.7,h:4.6});
s.addText([
  {text:"Null fraction (turn-off): ",options:{bold:true,color:"475569"}},{text:"stable across F1–F4.\n\n",options:{breakLine:true}},
  {text:"PP : PC ratio (composition): ",options:{bold:true,color:PP}},{text:"non-monotone, no drift.\n\n",options:{breakLine:true}},
  {text:"Equivalence bound: ",options:{bold:true,color:PC}},{text:"a large shift (~20 pp) is excluded; a subtle drift ≤10 pp is not (F4 n=4).",options:{italic:true,color:MUTE}}],
  {x:9.2,y:1.9,w:3.9,h:3.6,fontSize:17,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.2,y:5.05,w:3.9,h:1.15,fill:{color:"ECFDF5"},rectRadius:0.08,shadow:sh()});
s.addText("Donor-level anchor fractions do not support large biopsy-axis de-zonation.",
  {x:9.35,y:5.12,w:3.6,h:1.0,fontSize:16,bold:true,color:"065F46",align:"left",valign:"middle"});
foot(s,`6 / ${NMAIN}`,"Main result  ·  donor = point, line = median  ·  full 4-mechanism panel in backup");
s.addNotes("Two enlarged plots carry the result. Pericentral-anchor fraction is flat/non-monotone across F0–F4 — no depletion. Dual co-expression at the ambient-robust ≥2-UMI cut stays ~0.4% and does not trend — vs ~2.9% in the confounded explants. The other two mechanisms (null turn-off, PP:PC composition) are also flat — shown as callouts here, full four-panel in backup. And the equivalence bound: we exclude a large ~20-percentage-point shift, but cannot exclude subtle drift below ~10 points, because F4 has only 4 donors. Bottom line: donor-level anchor fractions do not support large biopsy-axis de-zonation.");

// ===================================================================== SLIDE 7 (volcano)
s=p.addSlide(); s.background={color:BG};
title(s,"Genome-wide pseudobulk finds one main signal: biliary markers");
img(s,"fig_volcano.png",{x:0.3,y:1.45,w:8.8,h:5.0});
s.addText([
  {text:"Pseudobulk per donor (sum raw hepatocyte UMIs); edgeR TMM + NB quasi-likelihood.\n",options:{breakLine:true}},
  {text:"64 genes at FDR<0.05 — mostly biliary/ductular.\n",options:{bold:true,breakLine:true}},
  {text:"Zonation markers not significant (GLUL FDR 0.80).\n",options:{color:PC,breakLine:true}},
  {text:"“No large single-gene hepatocyte program outside the biliary/ductular burden.”",options:{italic:true,color:BILIARY}}],
  {x:9.3,y:2.0,w:3.7,h:3.6,fontSize:17,color:INK,align:"left",valign:"top",paraSpaceAfter:9});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.3,y:5.7,w:3.7,h:0.8,fill:{color:LIGHT},rectRadius:0.06});
s.addText("Caveat: weak coordinated pathways still require gene-set testing (backup).",
  {x:9.45,y:5.75,w:3.4,h:0.7,fontSize:13,italic:true,color:MUTE,align:"left",valign:"middle"});
foot(s,`7 / ${NMAIN}`,"Discovery scan  ·  cirrhotic F4 vs F1");
s.addNotes("Pseudobulk in one sentence: we collapse thousands of nuclei to one profile per donor, because donors — not cells — are the biological replicates. This is an independent count-based check (zonation genes flat, GLUL FDR 0.80) plus a discovery layer. Only 64 of ~21,000 genes are significant, and they are biliary/ductular markers, not a broad metabolic/stress program. Careful wording: no large single-GENE program outside the biliary burden — and I flag on the slide that gene-LEVEL FDR can miss a weak coordinated pathway, which needs gene-set testing. I show them I know that limitation.");

// ===================================================================== SLIDE 8 (compositional)
s=p.addSlide(); s.background={color:BG};
title(s,"The biliary signal is real — but likely not broad transdifferentiation");
img(s,"fig_compositional.png",{x:0.3,y:1.5,w:12.7,h:4.0});
s.addText([
  {text:"Strong: ",options:{bold:true,color:"065F46"}},{text:"biliary genes are far more abundant in cholangiocytes;  true hepatocyte co-expression is rare (~0.4%).  ",options:{}},
  {text:"Suggestive: ",options:{bold:true,color:"B45309"}},{text:"decontX halves the hits (supports an ambient contribution — not proof).  ",options:{}},
  {text:"Open: ",options:{bold:true,color:CONFOUND}},{text:"EPCAM / SPINT2 / B3GNT3 survive.",options:{}}],
  {x:0.6,y:5.7,w:12.2,h:0.7,fontSize:15.5,color:INK,align:"left"});
s.addText([{text:"F4 cholangiocyte expansion is a plausible ambient-RNA source.   ",options:{color:INK}},
  {text:"CXCL10 is separated as a possible real inflammatory signal — it does not track the cholangiocyte fraction.",options:{color:STRESS,bold:true}}],
  {x:0.6,y:6.4,w:12.2,h:0.6,fontSize:15.5,align:"left"});
foot(s,`8 / ${NMAIN}`,"Source attribution: most consistent with ambient RNA + rare mixed nuclei (a lead, not closed)");
s.addNotes("Cautious wording — distinguish evidence levels. STRONG: the genes are 5–78× more abundant in cholangiocytes, and per-cell hepatocyte co-expression is only ~0.4%. SUGGESTIVE: decontX halves the hits and drops SOX4/SOX9 — this supports an ambient contribution but is not proof; decontX can over- or under-correct. OPEN: EPCAM/SPINT2/B3GNT3 survive. So the dominant evidence points to composition/ambient RNA, but a rare intrinsic state is not excluded — say that, do not say 'we proved contamination.' CXCL10 is set aside as a candidate real inflammatory signal.");

// ===================================================================== SLIDE 9 (conclusions)
s=p.addSlide(); s.background={color:DARK};
s.addText("Matched biopsies support preservation, not progressive collapse",
  {x:0.7,y:0.5,w:11.9,h:0.9,fontSize:28,bold:true,color:WHITE,align:"left",valign:"middle"});
const cols=[
  {h:"Conclusions",c:"5EEAD4",items:["Full healthy→end-stage trajectory is source-confounded.","In biopsy F1–F4, hepatocyte transcriptional zonation is preserved.","Main DGE signal = biliary/ductular burden, most consistent with composition / ambient RNA."]},
  {h:"Limits",c:"FCA5A5",items:["snRNA-seq ≠ lobule geometry / spatial architecture.","Imaging / protein / organoid evidence not re-analyzed.","F4 has only 4 biopsy donors.","Gene-level DGE can miss weak coordinated pathways."]},
  {h:"Next",c:"93C5FD",items:["CAMERA / ROAST gene-set tests.","Leave-one-F4-donor-out DGE.","Quantitative contamination model.","Spatial / independent biopsy validation."]}
];
let cx=0.7; for(const col of cols){ const cw=3.9;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:cx,y:1.65,w:cw,h:4.4,fill:{color:"1E293B"},rectRadius:0.08,shadow:sh()});
  s.addText(col.h,{x:cx,y:1.8,w:cw,h:0.5,fontSize:20,bold:true,color:col.c,align:"center"});
  s.addText(col.items.map(t=>({text:t,options:{bullet:true,color:"E2E8F0",breakLine:true,paraSpaceAfter:10}})),
    {x:cx+0.25,y:2.45,w:cw-0.45,h:3.5,fontSize:14.5,align:"left",valign:"top"});
  cx+=cw+0.25; }
s.addText("The snRNA-seq transcriptomic evidence for progressive de-zonation does not survive matched-source re-analysis.",
  {x:0.7,y:6.35,w:11.9,h:0.7,fontSize:18,bold:true,italic:true,color:WHITE,align:"center"});
s.addNotes("Close on the methodological lesson: in single-cell disease atlases, acquisition matching can dominate apparent disease trajectories. The bottom line is narrow and honest: the snRNA-seq transcriptomic evidence for progressive de-zonation does not survive matched-source re-analysis; imaging/protein/organoid evidence is untouched. And keep the biliary claim careful — most consistent with composition/ambient RNA, a rare intrinsic state not excluded.");

// ===================================================================== BACKUPS
function back(t){ const b=p.addSlide(); b.background={color:BG};
  b.addText("Backup",{x:0.5,y:0.28,w:3,h:0.4,fontSize:13,bold:true,color:BIOPSY});
  b.addText(t,{x:0.5,y:0.66,w:12.3,h:0.8,fontSize:26,bold:true,color:INK,align:"left"}); return b; }
function bbul(b,items,y){ b.addText(items.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:9}})),
  {x:0.8,y:y||1.7,w:11.6,h:5.0,fontSize:20,color:INK,align:"left",valign:"top"}); }
let b;

b=back("Full four-mechanism panel (all F0–F4)");
img(b,"fig_anchor2x2.png",{x:1.3,y:1.55,w:9.2,h:5.1});
b.addText([{text:"None of the four de-zonation routes shows a large monotone biopsy-axis change.\n\n",options:{bold:true,breakLine:true}},
  {text:"Confounded explants for contrast: dual ≈ 2.9% (~7×).",options:{color:CONFOUND}}],
  {x:10.6,y:2.6,w:2.5,h:3.0,fontSize:15,color:INK,align:"left"});

b=back("Are you overturning the paper? No — narrow scope");
bbul(b,["We re-tested only the snRNA-seq transcriptional zonation/plasticity evidence.",
  "We did NOT test imaging, protein staining, organoids, or 3D architecture.",
  "Claim: matched biopsy transcriptomes do not show progressive zonation loss.",
  "We agree the strong signal is an end-stage phenomenon."]);

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

b=back("Robustness: sensitivity grid + equivalence bound");
img(b,"fig_tost.png",{x:6.6,y:1.7,w:6.4,h:4.0});
b.addText([{text:"Stable across every variant:\n",options:{bold:true,breakLine:true}},
  {text:"PC = GLUL-only / CYP3A4-only / both;  PP = 2-of-4 / 3-of-4;\nALDOB in/out;  CPS1-based;  threshold 1 vs 2 UMI.\n\n",options:{breakLine:true}},
  {text:"No PC depletion · no dual increase · no turn-off — in all.\n\n",options:{bold:true,color:BIOPSY,breakLine:true}},
  {text:"Bound: large shift (~20 pp) excluded; subtle drift ≤10 pp not excluded (F4 n=4).",options:{italic:true,color:MUTE}}],
  {x:0.7,y:1.9,w:5.7,h:4.2,fontSize:16,color:INK,align:"left",valign:"top"});

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
  "A Simpson/aggregation sign-reversal confirmed the artifact; count taxonomy separates mechanisms."]);

b=back("Why not the 2D PC-vs-PP joint-count plot?");
bbul(b,["Broad metabolic program sums are ON in most normal hepatocytes.",
  "So “both programs high” is satisfied by normal cells — not a co-expression test.",
  "It is a pole-collapse visual (fuller in biopsy than explant).",
  "The clean metric is strict anchor dual at ≥2 UMI: ~0.4% biopsy vs ~2.9% explant."]);

b=back("DGE model details");
bbul(b,["Raw hepatocyte UMI counts summed per donor.",
  "filterByExpr retained 21,022 genes; TMM normalization.",
  "edgeR negative-binomial quasi-likelihood GLM, robust dispersion; common BCV 0.405.",
  "Primary contrast F4 vs F1.",
  "Primary signal persists in DIRECTION with a run covariate and within a single run; significance attenuates with the smaller n (not a batch artifact)."]);

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

p.writeFile({fileName:__dirname+"/MASLD_zonation_reanalysis_8min.pptx"}).then(f=>console.log("WROTE",f));
