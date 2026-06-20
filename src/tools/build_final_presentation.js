// Builds presentation/Zonation_Final_Presentation.pptx — the ~15-min results talk.
// Bold, readable theme: dark title band per slide, filled colored card headers, large type.
//   npm install pptxgenjs && node src/tools/build_final_presentation.js
// Figure assets in presentation/assets/. Slide plan: presentation/PRESENTATION_PLAN.md.
const path = require("path");
const pptxgen = require("pptxgenjs");
const ROOT = path.join(__dirname, "..", "..");
const A = path.join(ROOT, "presentation", "assets") + path.sep;
const OUT = path.join(ROOT, "presentation", "Zonation_Final_Presentation.pptx");
const p = new pptxgen(); p.defineLayout({ name: "W", width: 13.333, height: 7.5 }); p.layout = "W";

const DARK="0E3A40",TEAL="16545C",MID="1B6E78",ORANGE="C05621",GREEN="2F855A",
      ICE="CFE6E9",INK="1F2733",MUTED="5A6472",WHITE="FFFFFF",
      TEALT="E7F2F3",ORANGET="FBE7D8",GREENT="E6F2EC",LIGHT="F4F8F9";
const HF="Georgia",BF="Calibri",W=13.333,H=7.5;
const NS=()=>({}); // noop

function blend(a,b,t){const A=parseInt(a,16),B=parseInt(b,16);const ar=(A>>16)&255,ag=(A>>8)&255,ab=A&255,br=(B>>16)&255,bg=(B>>8)&255,bb=B&255;const r=Math.round(ar+(br-ar)*t),g=Math.round(ag+(bg-ag)*t),bl=Math.round(ab+(bb-ab)*t);return((1<<24)+(r<<16)+(g<<8)+bl).toString(16).slice(1).toUpperCase();}
function rrect(s,x,y,w,h,fill,opt={}){const o=s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:opt.rad||0.09,fill:{color:fill},line:opt.line?{color:opt.line,width:opt.lw||1}:{type:"none"}});return o;}
function rect(s,x,y,w,h,fill){s.addShape(p.ShapeType.rect,{x,y,w,h,fill:{color:fill},line:{type:"none"}});}
function ell(s,x,y,w,h,fill){s.addShape(p.ShapeType.ellipse,{x,y,w,h,fill:{color:fill},line:{type:"none"}});}
function T(s,x,y,w,h,runs,o={}){s.addText(runs,{x,y,w,h,align:o.align||"left",valign:o.valign||"top",fontFace:o.font||BF,lineSpacingMultiple:o.sp||1.0,margin:o.margin==null?2:o.margin});}
function img(s,f,x,y,w,h){s.addImage({path:A+f,x,y,w,h,sizing:{type:"contain",w,h}});}

// dark title band + orange underline + kicker + white title; returns content-top y
function band(s,kicker,title){
  s.background={color:WHITE};
  rect(s,0,0,W,1.18,DARK); rect(s,0,1.18,W,0.07,ORANGE);
  T(s,0.55,0.26,9,0.3,[{text:kicker.toUpperCase(),options:{fontSize:11,bold:true,color:ICE,charSpacing:3}}]);
  T(s,0.55,0.54,11.0,0.62,[{text:title,options:{fontSize:25,bold:true,color:WHITE,fontFace:HF}}],{valign:"middle"});
  return 1.5;
}
function pill(s,txt,color){
  rrect(s,9.7,0.36,3.05,0.46,color,{rad:0.23});
  T(s,9.7,0.36,3.05,0.46,[{text:txt,options:{fontSize:11,bold:true,color:WHITE}}],{align:"center",valign:"middle",margin:0});
}
// card with FILLED colored header
function card(s,x,y,w,h,title,bodyRuns,accent,tint){
  rrect(s,x,y,w,h,tint||WHITE,{line:"D7DDE3",lw:1,rad:0.07});
  rrect(s,x,y,w,0.52,accent,{rad:0.07});
  rect(s,x,y+0.26,w,0.26,accent); // square off bottom of header
  T(s,x+0.22,y,w-0.4,0.52,[{text:title,options:{fontSize:14.5,bold:true,color:WHITE}}],{valign:"middle",margin:0});
  T(s,x+0.22,y+0.66,w-0.42,h-0.82,bodyRuns,{valign:"top",sp:1.06});
}
function placeholder(s,x,y,w,h,label,sub){
  rrect(s,x,y,w,h,"EDF1F3",{line:ORANGE,lw:1.75,rad:0.08});
  s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{type:"none"},line:{color:ORANGE,width:1.75,dashType:"dash"}});
  T(s,x,y,w,h,[{text:"FIGURE GOES HERE\n",options:{fontSize:15,bold:true,color:ORANGE}},{text:label+"\n",options:{fontSize:13,color:INK}},{text:sub||"",options:{fontSize:11,italic:true,color:MUTED}}],{align:"center",valign:"middle"});
}
function darkbg(s){s.background={color:DARK}; rect(s,0,6.86,W,0.14,ORANGE);}

/* ---------- 1 TITLE ---------- */
let s=p.addSlide(); darkbg(s);
for(let i=0;i<12;i++){const c=blend("F0C247","3B7FD1",i/11);rect(s,0.9+i*0.42,5.5,0.42,0.16,c);}
T(s,0.9,5.69,1.4,0.25,[{text:"portal",options:{fontSize:9,color:ICE}}]);
T(s,4.7,5.69,1.4,0.25,[{text:"central",options:{fontSize:9,color:ICE}}],{align:"right"});
T(s,0.9,1.75,11.5,1.9,[{text:"Spatial Degradation of Hepatocyte Zonation",options:{fontSize:42,bold:true,color:WHITE,fontFace:HF}}]);
T(s,0.9,3.65,11,0.8,[{text:"Decoding the collapse of liver cell identity across the fatty-liver disease course",options:{fontSize:18,italic:true,color:ICE}}]);
T(s,0.9,6.95,11.5,0.4,[{text:"Roee  ·  Shira      |      Computational Genomics 76553 — Final Hackathon",options:{fontSize:13,color:ICE}}]);

/* ---------- 2 BIOLOGY ---------- */
s=p.addSlide(); band(s,"The biology","What the liver does — and the zonation gradient");
T(s,0.6,1.6,6.15,5.4,[
 {text:"The liver is a metabolic factory: ",options:{bold:true,color:DARK,fontSize:14}},
 {text:"it buffers blood sugar, makes plasma proteins (albumin), produces bile acids, turns nitrogen waste into urea, and detoxifies drugs.\n\n",options:{fontSize:14}},
 {text:"Two epithelial cells: ",options:{bold:true,color:DARK,fontSize:14}},
 {text:"hepatocytes (the bulk factory) and cholangiocytes (bile-duct lining).\n\n",options:{fontSize:14}},
 {text:"Blood flows portal → central, so a cell's environment — and the genes it switches on — depends on where it sits:\n",options:{fontSize:14}},
 {text:"•  Periportal: ",options:{bold:true,color:TEAL,fontSize:14}},{text:"urea cycle, gluconeogenesis (ASS1, PCK1).\n",options:{fontSize:14}},
 {text:"•  Pericentral: ",options:{bold:true,color:ORANGE,fontSize:14}},{text:"drug metabolism, glutamine (CYP2E1, GLUL).\n\n",options:{fontSize:14}},
 {text:"The hinge: ",options:{bold:true,color:DARK,fontSize:14}},{text:"position is encoded in expression, so it can be decoded back out.",options:{fontSize:14}}],{sp:1.05});
img(s,"fig2.png",7.0,1.7,5.85,5.0);

/* ---------- 3 DE-ZONATION vs PLASTICITY ---------- */
s=p.addSlide(); band(s,"What we measure","Two ways identity breaks: de-zonation vs plasticity");
T(s,0.6,1.55,12.1,0.5,[{text:"Both look like 'a cell expressing two opposite things at once' — the difference is WHICH boundary is crossed.",options:{fontSize:14,italic:true,color:MUTED}}]);
card(s,0.6,2.3,6.0,2.7,"De-zonation",[
 {text:"Loses its POSITION on the portal↔central axis (still a hepatocyte).\n",options:{fontSize:13.5,color:INK}},
 {text:"Co-expresses opposite zonal programs (CYP2E1 + ASS1).\n",options:{fontSize:13.5,color:INK}},
 {text:"Signature: the pericentral / periportal zonation genes.",options:{fontSize:13.5,color:INK}}],TEAL,TEALT);
card(s,6.73,2.3,6.0,2.7,"Plasticity",[
 {text:"Loses its CELL-TYPE identity (hepatocyte → bile-duct).\n",options:{fontSize:13.5,color:INK}},
 {text:"Co-expresses hepatocyte + duct programs (ALB + KRT7).\n",options:{fontSize:13.5,color:INK}},
 {text:"Signature: KRT7, KRT19, SOX9 … (from Paper 1).",options:{fontSize:13.5,color:INK}}],ORANGE,ORANGET);
rrect(s,0.6,5.3,12.13,1.55,LIGHT,{line:"D7DDE3",lw:1,rad:0.08});
T(s,0.85,5.42,11.6,1.35,[
 {text:"Analogy:  ",options:{bold:true,color:DARK,fontSize:13.5}},
 {text:"a worker who forgets which station they man (de-zonation) is still a factory worker; one who forgets they work in the factory at all (plasticity) is something else.  ",options:{fontSize:13.5,color:INK}},
 {text:"H3 asks whether these are the same cells — does losing your address predict losing your job?",options:{bold:true,color:DARK,fontSize:13.5}}],{valign:"middle",sp:1.05});

/* ---------- 4 GAP ---------- */
s=p.addSlide(); band(s,"The opportunity","Two datasets, one gap");
img(s,"fig3.png",3.05,1.5,7.2,3.0);
card(s,0.6,4.75,6.0,1.95,"Paper 2 — the ruler",[{text:"Healthy human liver with spatial coordinates KEPT → a quantitative porto-central zone index. But healthy only.",options:{fontSize:13.5,color:INK}}],TEAL,TEALT);
card(s,6.73,4.75,6.0,1.95,"Paper 1 — the cells",[{text:"69k disease nuclei across all stages — but snRNA-seq THREW AWAY position.",options:{fontSize:13.5,color:INK}}],ORANGE,ORANGET);
T(s,0.6,6.85,12.13,0.45,[{text:"Our move: use the healthy ruler to assign each diseased cell a pseudo-zonal coordinate. Neither paper did this.",options:{fontSize:13,bold:true,color:DARK}}],{align:"center"});

/* ---------- 5 QUESTION + HYPOTHESES ---------- */
s=p.addSlide(); band(s,"What we test","Research question & hypotheses");
rrect(s,0.6,1.5,12.13,1.18,GREENT,{line:GREEN,lw:1.3,rad:0.07});
T(s,0.85,1.56,11.65,1.06,[
 {text:"Q   ",options:{fontSize:17,bold:true,color:GREEN}},
 {text:"Using the healthy zonation ruler, can we measure how — and how much — hepatocyte zonation degrades as MASLD advances from healthy to end-stage, and is that degradation linked to plasticity?",options:{fontSize:13.5,color:DARK}}],{valign:"middle",sp:1.03});
card(s,0.6,2.9,3.95,2.45,"H1 — Erosion",[{text:"A de-zonation score rises monotonically Healthy → end-stage.\n\n",options:{fontSize:13,color:INK}},{text:"Test: ordered trend on per-donor values.",options:{fontSize:12,italic:true,color:MID}}],TEAL,TEALT);
card(s,4.69,2.9,3.95,2.45,"H2 — Which programs",[{text:"Specific programs (e.g. pericentral CYP detox) collapse earliest.\n\n",options:{fontSize:13,color:INK}},{text:"Test: pseudobulk donor×zone DE + FDR.",options:{fontSize:12,italic:true,color:MID}}],ORANGE,ORANGET);
card(s,8.78,2.9,3.95,2.45,"H3 — Plasticity link",[{text:"The most de-zonated cells are the ones gaining bile-duct identity.\n\n",options:{fontSize:13,color:INK}},{text:"Test: within-donor correlation.",options:{fontSize:12,italic:true,color:MID}}],TEAL,TEALT);
img(s,"fig8.png",0.6,5.5,3.8,1.55);
T(s,0.6,7.08,3.8,0.25,[{text:"illustrative — the H1 collapse curve we're after",options:{fontSize:8,italic:true,color:MUTED}}],{align:"center"});
rrect(s,4.7,5.5,8.03,1.5,LIGHT,{line:"D7DDE3",lw:1,rad:0.08});
T(s,4.95,5.55,7.6,1.42,[{text:"Why it matters:  ",options:{bold:true,color:ORANGE,fontSize:12}},{text:"drug dosing (pericentral CYP) · ammonia / encephalopathy (periportal urea) · finer-than-histology staging · cancer / de-differentiation link · a reusable decoder for spatially-blind atlases.",options:{fontSize:12,color:INK}}],{valign:"middle",sp:1.05});

/* ---------- 6 METHOD ---------- */
s=p.addSlide(); band(s,"The method","How we decode position");
const steps=[["1","Signatures","pericentral & periportal gene sets — landmark & full, compared"],["2","Coordinate","score = mean_z(PC) − mean_z(PP) per cell"],["3","Classifier","zone probabilities → entropy = confusion = de-zonation"],["4","Collapse","one metric per donor, tested across stages"]];
let x=0.6; steps.forEach((st,i)=>{
 const acc=i%2?ORANGE:TEAL; rrect(s,x,1.6,2.85,1.85,i%2?ORANGET:TEALT,{line:"D7DDE3",lw:1,rad:0.08});
 ell(s,x+0.22,1.78,0.52,0.52,acc); T(s,x+0.22,1.78,0.52,0.52,[{text:st[0],options:{fontSize:18,bold:true,color:WHITE}}],{align:"center",valign:"middle",margin:0});
 T(s,x+0.84,1.84,1.9,0.5,[{text:st[1],options:{fontSize:14,bold:true,color:DARK}}],{valign:"middle"});
 T(s,x+0.22,2.45,2.5,0.9,[{text:st[2],options:{fontSize:10.5,color:INK}}]);
 if(i<3)T(s,x+2.8,2.1,0.4,0.5,[{text:"▶",options:{fontSize:14,bold:true,color:MID}}],{align:"center",valign:"middle"});
 x+=3.07;});
img(s,"fig5.png",0.7,3.7,5.9,3.4); img(s,"fig6.png",6.95,3.85,5.85,3.0);

/* ---------- 7 HONESTY ---------- */
s=p.addSlide(); band(s,"Why it holds up","Doing it honestly");
rrect(s,0.6,1.55,12.13,1.15,ORANGET,{line:ORANGE,lw:1.2,rad:0.07});
T(s,0.85,1.6,11.6,1.05,[{text:"Negative control.  ",options:{fontSize:15,bold:true,color:ORANGE}},{text:"Shuffle the disease-stage labels and re-run: the collapse trend must VANISH. A 'signal' that survives shuffling was an artefact. (The positive control — recovering zonation in healthy liver — is the next slide.)",options:{fontSize:13.5,color:INK}}],{valign:"middle",sp:1.05});
T(s,0.6,2.95,7.0,0.4,[{text:"What de-zonation is — and isn't",options:{fontSize:15,bold:true,color:DARK}}]);
T(s,0.6,3.42,7.0,2.4,[
 [{text:"IS  ",options:{fontSize:13.5,bold:true,color:GREEN}},{text:"— loss of the expression program: pericentral–periportal mutual exclusivity weakens and the coordinate spread narrows.",options:{fontSize:13.5,color:INK}}],
 [{text:"ISN'T  ",options:{fontSize:13.5,bold:true,color:ORANGE}},{text:"— physical spatial scrambling with intact expression: dissociated data couldn't see it, and it's very unlikely here.",options:{fontSize:13.5,color:INK}}]
].flatMap((line,i)=> i===0?line:[{text:"\n",options:{fontSize:6}},...line]),{sp:1.1});
img(s,"fig7.png",7.85,3.05,4.95,2.55);
T(s,0.6,6.95,12.1,0.4,[{text:"Donor-level inference (no pseudoreplication) and held-out-gene / circularity guards underpin every test — details in backup.",options:{fontSize:10.5,italic:true,color:MUTED}}]);

/* ---------- 8 POSITIVE CONTROL ---------- */
s=p.addSlide(); band(s,"Positive control","The ruler works on healthy liver"); pill(s,"✓ DONE — REAL DATA",GREEN);
img(s,"p2_validation.png",0.7,1.7,12.0,3.75);
T(s,0.7,5.6,12,0.5,[{text:"On real Paper 2 healthy hepatocytes the coordinate recovers zonation:  ",options:{bold:true,color:DARK,fontSize:14}},{text:"pericentral CYP2E1 rises with it and periportal ASS1 falls.",options:{fontSize:14,color:INK}}]);
T(s,0.7,6.15,12,0.8,[{text:"A single broad central hump is exactly what a continuum looks like — the proof of zonation is the marker slopes, not two peaks. We validated before trusting it on disease.",options:{fontSize:12.5,italic:true,color:MUTED}}],{sp:1.05});

/* ---------- 9 H1 result ---------- */
s=p.addSlide(); band(s,"Result","H1 — Does zonation collapse across stages?"); pill(s,"TO FILL AFTER HACKATHON",ORANGE);
img(s,"fig4.png",0.7,1.6,7.2,4.5);
rrect(s,0.7,6.2,3.5,0.42,ORANGE,{rad:0.2}); T(s,0.7,6.2,3.5,0.42,[{text:"EXPECTED SHAPE — swap for real A6",options:{fontSize:10,bold:true,color:WHITE}}],{align:"center",valign:"middle",margin:0});
card(s,8.2,1.6,4.55,2.0,"What to look for",[{text:"Coordinate spread NARROWS and pericentral–periportal anti-correlation weakens toward 0 across stages.",options:{fontSize:12.5,color:INK}}],TEAL,TEALT);
card(s,8.2,3.8,4.55,2.35,"We found: ___",[{text:"[fill: ρ, donor-bootstrap 95% CI, permutation p]\n\n",options:{fontSize:12.5,color:INK}},{text:"plot_a6_collapse · pipeline.py:collapse",options:{fontSize:10.5,italic:true,color:MUTED}}],ORANGE,ORANGET);

/* ---------- 10 H2 ---------- */
s=p.addSlide(); band(s,"Result","H2 — Which programs collapse, and where?"); pill(s,"TO FILL AFTER HACKATHON",ORANGE);
placeholder(s,0.7,1.6,7.2,4.6,"Volcano per zone (portal / central): effect vs −log10 q","plot_a7_volcano · signature genes flagged");
card(s,8.2,1.6,4.55,2.0,"What to look for",[{text:"A coherent set of genes at q<0.05 — surviving EXCLUSION of the signature genes — concentrated in one zone first.",options:{fontSize:12.5,color:INK}}],TEAL,TEALT);
card(s,8.2,3.8,4.55,2.35,"We found: ___",[{text:"[fill: # genes q<0.05 per zone; name the 3–5 earliest-collapsing programs]\n\n",options:{fontSize:12.5,color:INK}},{text:"pipeline.py:de",options:{fontSize:10.5,italic:true,color:MUTED}}],ORANGE,ORANGET);

/* ---------- 11 H3 ---------- */
s=p.addSlide(); band(s,"Result","H3 — Are de-zonated cells the plastic ones?"); pill(s,"TO FILL AFTER HACKATHON",ORANGE);
placeholder(s,0.7,1.6,7.2,4.6,"Stage-stratified scatter: de-zonation vs plasticity score","plot_a8_plasticity · WITHIN donor/stage");
card(s,8.2,1.6,4.55,2.0,"What to look for",[{text:"A positive within-donor link — not a pooled one (late disease trivially has more of both).",options:{fontSize:12.5,color:INK}}],TEAL,TEALT);
card(s,8.2,3.8,4.55,2.35,"We found: ___",[{text:"[fill: mean per-donor ρ; OLS dez coefficient controlling stage+donor]\n\n",options:{fontSize:12.5,color:INK}},{text:"pipeline.py:plasticity",options:{fontSize:10.5,italic:true,color:MUTED}}],ORANGE,ORANGET);

/* ---------- 12 LIMITATIONS ---------- */
s=p.addSlide(); band(s,"What we can't claim","Limitations & honest scope");
img(s,"fig7.png",0.7,1.7,6.5,3.55);
T(s,7.55,1.7,5.2,5.0,[
 [{text:"• Blind to pure spatial scrambling",options:{bold:true,color:DARK,fontSize:13.5}},{text:" — if cells keep identity but move, dissociated data sees nothing.",options:{fontSize:13.5,color:INK}}],
 [{text:"\n• Pseudo-zonal, not (x,y)",options:{bold:true,color:DARK,fontSize:13.5}},{text:" — a 1-D reconstructed coordinate, never a true position.",options:{fontSize:13.5,color:INK}}],
 [{text:"\n• Ruler-validity matters",options:{bold:true,color:DARK,fontSize:13.5}},{text:" — disease may corrupt the marker genes; Step 5b checks the ruler still holds.",options:{fontSize:13.5,color:INK}}],
 [{text:"\n• Associational",options:{bold:true,color:DARK,fontSize:13.5}},{text:" — we measure collapse, not its cause.",options:{fontSize:13.5,color:INK}}]
].flat(),{sp:1.1});

/* ---------- 13 CONCLUSIONS ---------- */
s=p.addSlide(); darkbg(s); pill(s,"TO FILL AFTER HACKATHON",ORANGE);
T(s,0.7,0.55,8,0.9,[{text:"Conclusions",options:{fontSize:30,bold:true,color:WHITE,fontFace:HF}}]);
function dc(y,h,b){T(s,0.9,y,11.5,0.95,[{text:h+"  ",options:{bold:true,color:ORANGE,fontSize:17}},{text:b,options:{color:ICE,fontSize:17}}],{sp:1.05});}
dc(1.95,"H1 —","[did zonation collapse, and how monotonically? ___]");
dc(3.0,"H2 —","[which programs eroded first, and in which zone? ___]");
dc(4.05,"H3 —","[did de-zonation track plasticity, within donors? ___]");
rect(s,0.9,5.2,11.5,0.02,MID);
T(s,0.9,5.45,11.5,1.2,[{text:"One-line takeaway: a reference-decoder turns the many spatially-blind disease atlases into a quantitative readout of how liver identity disintegrates. [refine with results]",options:{fontSize:15,italic:true,color:WHITE}}],{sp:1.05});

/* ---------- 14 THANKS ---------- */
s=p.addSlide(); darkbg(s);
T(s,0.9,2.7,11.5,1.2,[{text:"Thank you — questions?",options:{fontSize:40,bold:true,color:WHITE,fontFace:HF}}]);
T(s,0.9,4.0,11.5,0.5,[{text:"Roee · Shira   |   Computational Genomics 76553         (backup slides follow)",options:{fontSize:15,color:ICE}}]);

/* ---------- BACKUPS ---------- */
function bk(t){let s=p.addSlide(); band(s,"Backup",t); return s;}
s=bk("Is the ruler still a ruler? (validity battery)"); pill(s,"TO FILL AFTER HACKATHON",ORANGE);
placeholder(s,0.7,1.7,12.0,4.9,"Per-stage: internal coherence · cross-program anti-corr · split-half · program-off vs restriction-lost","plot_a5b_ruler (Step 5b)");
s=bk("Classifier — held-out confusion matrix (Paper 2)"); pill(s,"TO FILL AFTER HACKATHON",ORANGE);
placeholder(s,0.7,1.7,12.0,4.9,"Confusion matrix + held-out accuracy on Paper 2 before applying to Paper 1","Step 4b · calibrated multinomial logistic regression");
s=bk("Statistical rigor — the checklist");
const items=["BH-FDR q<0.05, never raw p","Ordered trend test, not pairwise only","Donor-level resampling (never 69k cells as independent)","Pseudobulk donor×zone DE; H2 via coordinate×stage interaction on held-out genes (repeated random splits)","Positive + negative controls","Effect sizes beside p/q"];
let yy=1.75; items.forEach((it,i)=>{ell(s,0.7,yy+0.03,0.3,0.3,i%2?ORANGE:TEAL); T(s,1.18,yy,11.4,0.55,[{text:it,options:{fontSize:15,color:INK}}],{valign:"middle"}); yy+=0.82;});
s=bk("Bonus — collapse vs inherited risk (Paper 3)"); pill(s,"OPTIONAL — IF IT RAN",MID);
placeholder(s,0.7,1.7,12.0,4.9,"Hypergeometric overlap: Step-7 collapse drivers vs Paper-3 risk-variant targets, expression-matched background","step9_bonus_enrichment.py · report fold + BH q");
s=bk("Data & reproducibility");
T(s,0.7,1.75,12.0,4.6,[
 [{text:"Raw → processed:  ",options:{bold:true,color:DARK,fontSize:14.5}},{text:"Seurat .rds → counts.mtx; MATLAB .mat → paper2_train.npz. Pipeline reads only data/processed/.",options:{fontSize:14.5,color:INK}}],
 [{text:"\n\nRepo:  ",options:{bold:true,color:DARK,fontSize:14.5}},{text:"src/{prep,steps,plotting,tools}, signatures/{full,paper2_landmark,core,expanded}, results/. run_all.py reproduces every figure on a clean checkout.",options:{fontSize:14.5,color:INK}}],
 [{text:"\n\nSignatures:  ",options:{bold:true,color:DARK,fontSize:14.5}},{text:"reported BOTH ways — the full transcriptome-wide program (default) and the exact Paper 2 landmark set — as a robustness comparison.",options:{fontSize:14.5,color:INK}}]
].flat(),{sp:1.08});

p.writeFile({ fileName: OUT }).then(()=>console.log("WROTE",OUT)).catch(e=>console.log("ERR",e));
