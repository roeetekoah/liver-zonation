// Builds presentation/Zonation_Final_Presentation.pptx (the ~15-min results talk).
// Reproducible: run from the repo with pptxgenjs installed.
//   npm install pptxgenjs && node src/tools/build_final_presentation.js
// Figure assets are expected in presentation/assets/ (rendered from the primer's SVGs +
// the real results/figures/p2_validation.png). See presentation/PRESENTATION_PLAN.md for
// the slide map (which slides are pre-made vs placeholders).
const path = require("path");
const pptxgen = require("pptxgenjs");
const ROOT = path.join(__dirname, "..", "..");
const A = path.join(ROOT, "presentation", "assets") + path.sep;
const OUT = path.join(ROOT, "presentation", "Zonation_Final_Presentation.pptx");

const p = new pptxgen(); p.defineLayout({ name: "W", width: 13.333, height: 7.5 }); p.layout = "W";
const DARK="0E3A40",TEAL="16545C",MID="1B6E78",ICE="CFE6E9",ORANGE="C05621",INK="1F2733",MUTED="5A6472",WHITE="FFFFFF",LIGHT="F4F8F9",GREEN="2F855A";
const HF="Georgia",BF="Calibri",W=13.333,H=7.5;
function blend(a,b,t){const A=parseInt(a,16),B=parseInt(b,16);const ar=(A>>16)&255,ag=(A>>8)&255,ab=A&255,br=(B>>16)&255,bg=(B>>8)&255,bb=B&255;const r=Math.round(ar+(br-ar)*t),g=Math.round(ag+(bg-ag)*t),bl=Math.round(ab+(bb-ab)*t);return((1<<24)+(r<<16)+(g<<8)+bl).toString(16).slice(1).toUpperCase();}
function header(s,title,kicker){s.background={color:WHITE};s.addShape(p.ShapeType.rect,{x:0,y:0,w:0.28,h:H,fill:{color:TEAL}});
  if(kicker)s.addText(kicker.toUpperCase(),{x:0.6,y:0.34,w:8.5,h:0.3,fontFace:BF,fontSize:11,bold:true,color:MID,charSpacing:2});
  s.addText(title,{x:0.6,y:kicker?0.62:0.5,w:8.6,h:0.9,fontFace:HF,fontSize:28,bold:true,color:DARK});}
function pill(s,txt,color){color=color||ORANGE;s.addShape(p.ShapeType.roundRect,{x:9.55,y:0.42,w:3.2,h:0.42,rectRadius:0.21,fill:{color}});
  s.addText(txt,{x:9.55,y:0.42,w:3.2,h:0.42,align:"center",valign:"middle",fontFace:BF,fontSize:11,bold:true,color:WHITE});}
function placeholder(s,x,y,w,h,label,sub){s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{color:"EDF1F3"},line:{color:ORANGE,width:1.75,dashType:"dash"}});
  s.addText([{text:"FIGURE GOES HERE\n",options:{fontSize:15,bold:true,color:ORANGE,fontFace:BF}},{text:label+"\n",options:{fontSize:13,color:INK,fontFace:BF}},{text:sub||"",options:{fontSize:11,italic:true,color:MUTED,fontFace:BF}}],{x,y,w,h,align:"center",valign:"middle"});}
function card(s,x,y,w,h,head,body,accent){accent=accent||TEAL;s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.07,fill:{color:LIGHT},line:{color:"D7DDE3",width:1}});
  s.addShape(p.ShapeType.rect,{x,y,w:0.09,h,fill:{color:accent}});s.addText(head,{x:x+0.22,y:y+0.14,w:w-0.36,h:0.4,fontFace:BF,fontSize:14.5,bold:true,color:DARK});
  s.addText(body,{x:x+0.22,y:y+0.6,w:w-0.36,h:h-0.72,fontFace:BF,fontSize:12,color:INK,valign:"top",lineSpacingMultiple:1.05});}
function img(s,p2,x,y,w,h){s.addImage({path:p2,x,y,w,h,sizing:{type:"contain",w,h}});}

let s=p.addSlide();s.background={color:DARK};
s.addShape(p.ShapeType.rect,{x:0,y:6.7,w:W,h:0.12,fill:{color:ORANGE}});
for(let i=0;i<12;i++){const c=blend("F0C247","3B7FD1",i/11);s.addShape(p.ShapeType.rect,{x:0.9+i*0.42,y:5.55,w:0.42,h:0.16,fill:{color:c},line:{color:c}});}
s.addText("portal",{x:0.9,y:5.74,w:1.2,h:0.25,fontFace:BF,fontSize:9,color:ICE});
s.addText("central",{x:4.7,y:5.74,w:1.2,h:0.25,fontFace:BF,fontSize:9,color:ICE,align:"right"});
s.addText("Spatial Degradation of Hepatocyte Zonation",{x:0.9,y:1.9,w:11.5,h:1.8,fontFace:HF,fontSize:42,bold:true,color:WHITE});
s.addText("Decoding the collapse of liver cell identity across the fatty-liver disease course",{x:0.9,y:3.7,w:11,h:0.8,fontFace:BF,fontSize:18,italic:true,color:ICE});
s.addText("Roee  ·  Shira      |      Computational Genomics 76553 — Final Hackathon",{x:0.9,y:6.95,w:11.5,h:0.4,fontFace:BF,fontSize:13,color:ICE});

s=p.addSlide();header(s,"What the liver does — and the zonation gradient","The biology");
s.addText([{text:"The liver is a metabolic factory: it buffers blood sugar, makes plasma proteins (albumin), produces bile acids, converts nitrogen waste to urea, and detoxifies drugs.\n\n"},{text:"Two epithelial cells: ",options:{bold:true,color:DARK}},{text:"hepatocytes (the bulk factory) and cholangiocytes (bile-duct lining).\n\n"},{text:"Blood flows portal → central, so a cell's environment — and the genes it switches on — depends on where it sits:\n"},{text:"•  Periportal: ",options:{bold:true,color:TEAL}},{text:"urea cycle, gluconeogenesis (ASS1, PCK1).\n"},{text:"•  Pericentral: ",options:{bold:true,color:ORANGE}},{text:"drug metabolism, glutamine (CYP2E1, GLUL).\n\n"},{text:"Zonation = this position-dependent gene gradient. The hinge: position is encoded in expression, so it can be decoded back out.",options:{bold:true,color:DARK}}],{x:0.6,y:1.6,w:6.1,h:5.4,fontFace:BF,fontSize:13.5,color:INK,valign:"top",lineSpacingMultiple:1.05});
img(s,A+"fig2.png",6.95,1.9,5.9,4.9);

s=p.addSlide();header(s,"Two ways identity breaks: de-zonation vs plasticity","What we measure");
s.addText("Both look like 'a cell expressing two opposite things at once' — the difference is WHICH boundary is crossed.",{x:0.6,y:1.55,w:12.1,h:0.5,fontFace:BF,fontSize:14,italic:true,color:MUTED});
card(s,0.6,2.25,6.0,2.75,"De-zonation","Loses its POSITION on the portal↔central axis (still a hepatocyte).\n\nCo-expresses opposite zonal programs (e.g. CYP2E1 + ASS1).\n\nSignature: the pericentral / periportal zonation genes.",TEAL);
card(s,6.75,2.25,6.0,2.75,"Plasticity","Loses its CELL-TYPE identity (hepatocyte → bile-duct).\n\nCo-expresses hepatocyte + duct programs (e.g. ALB + KRT7).\n\nSignature: KRT7, KRT19, SOX9 … (from Paper 1).",ORANGE);
s.addText([{text:"Analogy: ",options:{bold:true,color:DARK}},{text:"a worker who forgets which station they man (de-zonation) is still a factory worker; one who forgets they work in the factory at all (plasticity) is something else.  "},{text:"H3 asks whether these are the same cells — does losing your address predict losing your job?",options:{bold:true,color:DARK}}],{x:0.6,y:5.3,w:12.2,h:1.6,fontFace:BF,fontSize:13.5,color:INK,valign:"top",lineSpacingMultiple:1.05});

s=p.addSlide();header(s,"Two datasets, one gap","The opportunity");
img(s,A+"fig3.png",3.0,1.65,7.3,3.05);
card(s,0.6,4.95,5.95,1.9,"Paper 2 — the ruler","Healthy human liver with spatial coordinates KEPT → a quantitative porto-central zone index. But healthy only.",TEAL);
card(s,6.75,4.95,5.95,1.9,"Paper 1 — the cells","69k disease nuclei across all stages, but snRNA-seq THREW AWAY position.",ORANGE);
s.addText("Our move: use the healthy ruler to assign each diseased cell a pseudo-zonal coordinate. Neither paper did this.",{x:0.6,y:6.95,w:12.1,h:0.4,fontFace:BF,fontSize:12.5,bold:true,color:DARK,align:"center"});

s=p.addSlide();header(s,"Research question & hypotheses","What we test");
s.addShape(p.ShapeType.roundRect,{x:0.6,y:1.5,w:12.13,h:1.1,rectRadius:0.08,fill:{color:"EAFAF1"},line:{color:GREEN,width:1.25}});
s.addText([{text:"Q   ",options:{bold:true,color:GREEN,fontSize:17}},{text:"Using the healthy zonation ruler, can we measure how — and how much — hepatocyte zonation degrades as MASLD advances from healthy to end-stage, and is that degradation linked to plasticity?",options:{fontSize:14,color:DARK}}],{x:0.85,y:1.58,w:11.7,h:0.95,fontFace:BF,valign:"middle",lineSpacingMultiple:1.0});
card(s,0.6,2.85,3.95,3.4,"H1 — Erosion","A de-zonation score rises monotonically Healthy → end-stage.\n\nTest: ordered trend on per-donor values.",TEAL);
card(s,4.7,2.85,3.95,3.4,"H2 — Which programs","Specific programs (e.g. pericentral CYP detox) collapse earliest.\n\nTest: pseudobulk donor×zone DE + FDR.",ORANGE);
card(s,8.8,2.85,3.95,3.4,"H3 — Plasticity link","The most de-zonated cells are the ones gaining bile-duct identity.\n\nTest: within-donor correlation.",TEAL);
s.addShape(p.ShapeType.roundRect,{x:0.6,y:6.5,w:12.13,h:0.62,rectRadius:0.31,fill:{color:LIGHT},line:{color:"D7DDE3",width:1}});
s.addText([{text:"Why it matters:  ",options:{bold:true,color:ORANGE}},{text:"drug dosing (pericentral CYP) · ammonia/encephalopathy (periportal urea) · finer-than-histology staging · cancer/de-differentiation link · a reusable decoder for spatially-blind atlases.",options:{color:INK}}],{x:0.85,y:6.52,w:11.7,h:0.58,fontFace:BF,fontSize:10.5,valign:"middle"});

s=p.addSlide();header(s,"How we decode position","The method");
const steps=[["1","Signatures","pericentral & periportal gene sets from the healthy atlas"],["2","Coordinate","score = mean_z(PC) − mean_z(PP) per cell"],["3","Classifier","zone probabilities → entropy = confusion = de-zonation"],["4","Collapse","one metric per donor, tested across stages"]];
let x=0.6;steps.forEach((st,i)=>{s.addShape(p.ShapeType.roundRect,{x,y:1.7,w:2.85,h:1.7,rectRadius:0.07,fill:{color:LIGHT},line:{color:"D7DDE3",width:1}});
s.addShape(p.ShapeType.ellipse,{x:x+0.2,y:1.88,w:0.5,h:0.5,fill:{color:i%2?ORANGE:TEAL}});
s.addText(st[0],{x:x+0.2,y:1.88,w:0.5,h:0.5,align:"center",valign:"middle",fontFace:BF,fontSize:18,bold:true,color:WHITE});
s.addText(st[1],{x:x+0.8,y:1.92,w:1.95,h:0.45,fontFace:BF,fontSize:14,bold:true,color:DARK});
s.addText(st[2],{x:x+0.2,y:2.5,w:2.5,h:0.8,fontFace:BF,fontSize:10.5,color:INK,valign:"top"});
if(i<3)s.addText("▶",{x:x+2.78,y:2.3,w:0.4,h:0.5,align:"center",valign:"middle",fontSize:14,bold:true,color:MID});x+=3.07;});
img(s,A+"fig5.png",0.7,3.75,5.9,3.4);img(s,A+"fig6.png",6.9,3.9,6.0,3.0);

s=p.addSlide();header(s,"Doing it honestly","Why it holds up");
card(s,0.6,1.8,3.95,2.4,"Donor-level","Aggregate to one value per donor before testing — cell-level p-values are pseudoreplication and invalid.",TEAL);
card(s,4.7,1.8,3.95,2.4,"No circularity","Genes that build the coordinate are excluded from 'driver' claims; held-out gene split + interaction test for H2.",ORANGE);
card(s,8.8,1.8,3.95,2.4,"Controls","Positive control (healthy must recover zonation) + negative control (shuffle stage labels → trend vanishes).",TEAL);
s.addText("What de-zonation is — and isn't:",{x:0.6,y:4.45,w:6,h:0.4,fontFace:BF,fontSize:14,bold:true,color:DARK});
s.addText([{text:"IS",options:{bold:true,color:GREEN}},{text:" — loss of the expression program (mutual exclusivity weakens, spread narrows).\n"},{text:"ISN'T",options:{bold:true,color:ORANGE}},{text:" — physical spatial scrambling with intact expression; dissociated data can't see that (honest scope)."}],{x:0.6,y:4.85,w:7.6,h:1.6,fontFace:BF,fontSize:13,color:INK,valign:"top",lineSpacingMultiple:1.1});
img(s,A+"fig7.png",8.4,4.5,4.4,2.6);

s=p.addSlide();header(s,"The ruler works on healthy liver","Positive control — already validated");
pill(s,"✓ DONE — REAL DATA",GREEN);
img(s,A+"p2_validation.png",0.7,2.0,12.0,3.7);
s.addText([{text:"On real Paper 2 healthy hepatocytes the coordinate recovers zonation: ",options:{bold:true,color:DARK}},{text:"pericentral CYP2E1 rises with it and periportal ASS1 falls."}],{x:0.7,y:5.85,w:12,h:0.5,fontFace:BF,fontSize:14,color:INK});
s.addText("A single broad central hump is exactly what a continuum looks like — the proof of zonation is the marker slopes, not two peaks. We validated before trusting it on disease.",{x:0.7,y:6.35,w:12,h:0.7,fontFace:BF,fontSize:12.5,italic:true,color:MUTED});

s=p.addSlide();header(s,"H1 — Does zonation collapse across stages?","Result");
pill(s,"TO FILL AFTER HACKATHON");
img(s,A+"fig4.png",0.7,2.0,7.2,4.4);
s.addShape(p.ShapeType.roundRect,{x:0.7,y:6.5,w:3.4,h:0.4,rectRadius:0.2,fill:{color:ORANGE}});
s.addText("EXPECTED SHAPE — swap for real A6",{x:0.7,y:6.5,w:3.4,h:0.4,align:"center",valign:"middle",fontFace:BF,fontSize:10,bold:true,color:WHITE});
card(s,8.2,2.0,4.55,2.05,"What to look for","Coordinate spread NARROWS and pericentral–periportal anti-correlation weakens toward 0 across stages.",TEAL);
card(s,8.2,4.25,4.55,2.4,"We found: ___","[fill: ρ, donor-bootstrap 95% CI, permutation p]\n\nplot_a6_collapse · pipeline.py:collapse",ORANGE);

s=p.addSlide();header(s,"H2 — Which programs collapse, and where?","Result");
pill(s,"TO FILL AFTER HACKATHON");
placeholder(s,0.7,2.0,7.2,4.6,"Volcano per zone (portal / central): effect vs −log10 q","plot_a7_volcano  ·  signature genes flagged");
card(s,8.2,2.0,4.55,2.05,"What to look for","A coherent set of genes at q<0.05 — surviving EXCLUSION of the signature genes — concentrated in one zone first.",TEAL);
card(s,8.2,4.25,4.55,2.4,"We found: ___","[fill: # genes q<0.05 per zone; name the 3–5 earliest-collapsing programs]\n\npipeline.py:de",ORANGE);

s=p.addSlide();header(s,"H3 — Are de-zonated cells the plastic ones?","Result");
pill(s,"TO FILL AFTER HACKATHON");
placeholder(s,0.7,2.0,7.2,4.6,"Stage-stratified scatter: de-zonation vs plasticity score","plot_a8_plasticity  ·  WITHIN donor/stage");
card(s,8.2,2.0,4.55,2.05,"What to look for","A positive within-donor link — not a pooled one (late disease trivially has more of both).",TEAL);
card(s,8.2,4.25,4.55,2.4,"We found: ___","[fill: mean per-donor ρ; OLS dez coefficient controlling stage+donor]\n\npipeline.py:plasticity",ORANGE);

s=p.addSlide();header(s,"Limitations & honest scope","What we can't claim");
img(s,A+"fig7.png",0.7,1.8,6.6,3.6);
s.addText([{text:"• Blind to pure spatial scrambling",options:{bold:true,color:DARK}},{text:" — if cells keep identity but move, dissociated data sees nothing.\n\n"},{text:"• Pseudo-zonal, not (x,y)",options:{bold:true,color:DARK}},{text:" — a 1-D reconstructed coordinate, never a true position.\n\n"},{text:"• Ruler-validity matters",options:{bold:true,color:DARK}},{text:" — disease may corrupt the marker genes; Step 5b checks whether the ruler still holds.\n\n"},{text:"• Associational",options:{bold:true,color:DARK}},{text:" — we measure collapse, not its cause."}],{x:7.6,y:1.9,w:5.1,h:5.0,fontFace:BF,fontSize:13.5,color:INK,valign:"top",lineSpacingMultiple:1.05});

s=p.addSlide();s.background={color:DARK};
s.addText("Conclusions",{x:0.7,y:0.5,w:8.6,h:0.9,fontFace:HF,fontSize:30,bold:true,color:WHITE});
pill(s,"TO FILL AFTER HACKATHON");
function dc(y,h,b){s.addText([{text:h+"  ",options:{bold:true,color:ORANGE}},{text:b,options:{color:ICE}}],{x:0.9,y,w:11.5,h:0.9,fontFace:BF,fontSize:17,valign:"top",lineSpacingMultiple:1.05});}
dc(1.9,"H1 —","[did zonation collapse, and how monotonically? ___]");
dc(2.95,"H2 —","[which programs eroded first, and in which zone? ___]");
dc(4.0,"H3 —","[did de-zonation track plasticity, within donors? ___]");
s.addShape(p.ShapeType.rect,{x:0.9,y:5.2,w:11.5,h:0.02,fill:{color:MID}});
s.addText("One-line takeaway: a reference-decoder turns the many spatially-blind disease atlases into a quantitative readout of how liver identity disintegrates. [refine with results]",{x:0.9,y:5.45,w:11.5,h:1.2,fontFace:BF,fontSize:15,italic:true,color:WHITE,valign:"top"});

s=p.addSlide();s.background={color:DARK};
s.addShape(p.ShapeType.rect,{x:0,y:6.7,w:W,h:0.12,fill:{color:ORANGE}});
s.addText("Thank you — questions?",{x:0.9,y:2.7,w:11.5,h:1.2,fontFace:HF,fontSize:40,bold:true,color:WHITE});
s.addText("Roee · Shira   |   Computational Genomics 76553         (backup slides follow)",{x:0.9,y:4.0,w:11.5,h:0.5,fontFace:BF,fontSize:15,color:ICE});

function bk(t){let s=p.addSlide();header(s,t,"Backup");return s;}
s=bk("Is the ruler still a ruler? (validity battery)");pill(s,"TO FILL AFTER HACKATHON");
placeholder(s,0.7,1.9,12.0,4.8,"Per-stage: internal coherence · cross-program anti-corr · split-half · program-off vs restriction-lost","plot_a5b_ruler  (Step 5b)");
s=bk("Classifier — held-out confusion matrix (Paper 2)");pill(s,"TO FILL AFTER HACKATHON");
placeholder(s,0.7,1.9,12.0,4.8,"Confusion matrix + held-out accuracy on Paper 2 before applying to Paper 1","Step 4b · calibrated multinomial logistic regression");
s=bk("Statistical rigor — the checklist");
const items=["BH-FDR q<0.05, never raw p","Ordered trend test, not pairwise only","Donor-level resampling (never 69k cells as independent)","Pseudobulk donor×zone DE; H2 via coordinate×stage interaction on held-out genes","Positive + negative controls","Effect sizes beside p/q"];
let yy=1.9;items.forEach((it,i)=>{s.addShape(p.ShapeType.ellipse,{x:0.7,y:yy+0.04,w:0.28,h:0.28,fill:{color:i%2?ORANGE:TEAL}});s.addText(it,{x:1.15,y:yy,w:11.4,h:0.5,fontFace:BF,fontSize:15,color:INK,valign:"middle"});yy+=0.78;});
s=bk("Bonus — collapse vs inherited risk (Paper 3)");pill(s,"OPTIONAL — IF IT RAN");
placeholder(s,0.7,1.9,12.0,4.8,"Hypergeometric overlap: Step-7 collapse drivers vs Paper-3 risk-variant targets, expression-matched background","step9_bonus_enrichment.py · report fold + BH q");
s=bk("Data & reproducibility");
s.addText([{text:"Raw → processed: ",options:{bold:true,color:DARK}},{text:"Seurat .rds → counts.mtx; MATLAB .mat → paper2_train.npz. Pipeline reads only data/processed/.\n\n"},{text:"Repo: ",options:{bold:true,color:DARK}},{text:"src/{prep,steps,plotting,tools}, signatures/{paper2_landmark,core,expanded,sensitivity}, results/. run_all.py reproduces every figure on a clean checkout.\n\n"},{text:"Signatures: ",options:{bold:true,color:DARK}},{text:"baseline = EXACT Paper 2 landmark set (paper2_landmark); expanded from the ranked snRNA table; core = curated."}],{x:0.7,y:1.9,w:12.0,h:4.5,fontFace:BF,fontSize:15,color:INK,valign:"top",lineSpacingMultiple:1.1});

p.writeFile({ fileName: OUT }).then(() => console.log("WROTE", OUT)).catch(e => console.log("ERR", e));
