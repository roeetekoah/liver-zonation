// MASLD snRNA-seq hackathon deck. Kicker style (ALL-CAPS kicker + short headline), per
// the project's Zonation_Reanalysis.pptx. Run from here: node build_deck.js
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const A = __dirname + "/assets/";
// read a PNG's pixel dimensions (IHDR) so figures embed at their EXACT native aspect (no stretch)
function pngSize(file){ const b=fs.readFileSync(file); return {w:b.readUInt32BE(16), h:b.readUInt32BE(20)}; }

// exact palette + fonts from the project's old build_deck.js (archive/legacy_reports/)
const PC="1D4ED8", PP="EA580C", DUAL="7C3AED", NULL="9CA3AF",
      BIOPSY="0D9488", CONFOUND="BE123C", ENDSTAGE="86198F", STRESS="DC2626", BILIARY="7C3AED",
      WHITE="FFFFFF", MUTE="5C6E73", LINE="DAD4CA",
      INK="1B2B31", TEAL="1B6E78", TEALD="123F47", AMBER="C0561B", CREAM="F7F5F1", PALE="ECF1F1",
      SLATE="123F47", ORANGE="C0561B", KICK="C0561B", BG="F7F5F1", LIGHT="ECF1F1", DARK="16242B";
const SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});

const p=new pptxgen(); p.layout="LAYOUT_WIDE"; p.author="Roee Tekoah, Shira Gelbstein";
p.title="No transcriptional de-zonation signal in matched MASLD biopsies — but the pericentral detox program dims";

// --- helpers: kicker + short headline (+ optional act tag top-right); footer; caption; chips ---
function head(s,kicker,headline,section){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:8.6,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  if(section) s.addText(section,{x:9.4,y:0.32,w:3.45,h:0.3,fontSize:11,bold:true,color:TEAL,charSpacing:2,align:"right",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.85,fontSize:28,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
let _pg=1;  // slide 1 (title) has no footer; first foot() call is slide 2
function foot(s){ _pg++;
  s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});
  s.addText(String(_pg),{x:12.2,y:7.12,w:0.6,h:0.3,fontSize:10.5,color:MUTE,align:"right",margin:0});
}
function fcite(s,txt){ // paper-style citation footnote, set apart at the slide foot
  s.addShape(p.shapes.LINE,{x:0.5,y:6.78,w:3.2,h:0,line:{color:"C9C0B2",width:0.75}});
  s.addText(txt,{x:0.5,y:6.84,w:11.6,h:0.26,fontSize:10,italic:true,color:"6B6256",align:"left",margin:0});
}
function sep(t,sub){ // dark act-separator slide (a clean 2-second break between sections)
  const d=p.addSlide(); d.background={color:DARK};
  d.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
  d.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
  d.addText(t,{x:0.95,y:2.9,w:11.5,h:1.1,fontSize:44,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
  if(sub) d.addText(sub,{x:0.98,y:4.15,w:11.5,h:0.5,fontSize:17,italic:true,color:"9FC0C4",align:"left"});
}
function img(s,file,box){ // fit within (box.w x box.h) preserving the PNG's native aspect — exact, no stretch
  const d=pngSize(A+file), ar=d.w/d.h;
  let w=box.w, h=w/ar;
  if(box.h && h>box.h){ h=box.h; w=h*ar; }
  const x=box.x+(box.w-w)/2;          // centre horizontally within the box
  s.addImage({path:A+file,x:x,y:box.y,w:w,h:h});
}
function figcap(s,x,y,w,txt){ s.addText(txt,{x,y,w,h:0.4,fontSize:12,italic:true,color:MUTE,align:"center",margin:0}); }
function chip(s,x,y,w,h,txt,fill,tcol){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.08,shadow:sh()});
  s.addText(txt,{x,y,w,h,fontSize:14.5,bold:true,color:tcol||WHITE,align:"center",valign:"middle",margin:2});
}
function classbox(s,x,y,w,h,title,sub,fill,tcol){ // labelled definition card (title + plain-language line)
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.07,shadow:sh()});
  s.addText(title,{x:x+0.18,y:y+0.13,w:w-0.36,h:0.5,fontSize:20,bold:true,color:tcol||WHITE,fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(sub,{x:x+0.18,y:y+0.68,w:w-0.36,h:h-0.8,fontSize:13.5,color:tcol||WHITE,align:"left",valign:"top",margin:0});
}

// ============================================================ SLIDE 1 — TITLE
let s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
s.addText("LIVER GENOMICS  ·  SINGLE-NUCLEUS RE-ANALYSIS",
  {x:0.85,y:1.15,w:11.9,h:0.4,fontSize:15,bold:true,color:"9FC0C4",charSpacing:3,align:"left"});
s.addText("No transcriptional de-zonation signal in matched MASLD biopsies",
  {x:0.85,y:1.6,w:11.7,h:1.35,fontSize:34,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"top"});
s.addText("— but the pericentral detox program dims",
  {x:0.85,y:2.95,w:11.7,h:0.6,fontSize:23,italic:true,color:"9FC0C4",fontFace:SERIF,align:"left",valign:"top"});
s.addText("A critical re-analysis of the single-nucleus RNA-seq in Gribben et al., Nature 2024 (GSE202379)",
  {x:0.85,y:3.7,w:11.6,h:0.5,fontSize:17,italic:true,color:"C9D6D3",align:"left"});
s.addShape(p.shapes.LINE,{x:0.85,y:4.55,w:5.0,h:0,line:{color:ORANGE,width:1.5}});
s.addText([{text:"Roee Tekoah",options:{bold:true}},{text:"   ·   ",options:{color:"7E8F8B"}},{text:"Shira Gelbstein",options:{bold:true}}],
  {x:0.85,y:4.75,w:11.6,h:0.45,fontSize:20,color:"EDE7DB",align:"left"});
s.addText("Computational Genomics (76553)  ·  Hebrew University of Jerusalem  ·  Hackathon",
  {x:0.85,y:5.3,w:11.6,h:0.4,fontSize:15,color:"9CB0AC",align:"left"});
s.addText("47 donors  ·  ~99,809 nuclei  ·  69,426 hepatocytes  ·  raw-count, donor-level analysis",
  {x:0.85,y:6.35,w:11.6,h:0.4,fontSize:13,color:"7E8F8B",align:"left"});
s.addNotes("Title slide. We are Roee Tekoah and Shira Gelbstein; this is our hackathon re-analysis of the single-nucleus RNA-seq in Gribben et al., Nature 2024, asking whether the evidence for progressive hepatocyte de-zonation in MASLD survives once tissue acquisition is controlled. One-line answer: in matched biopsies we find no detectable progressive de-zonation — a large collapse is excluded, subtle drift is not. We are not claiming zonation is 'preserved' in any positive sense, and we do not touch the paper's imaging/protein evidence.");

// ============================================================ SLIDE 2 — BACKGROUND  [BACKGROUND]
s=p.addSlide(); s.background={color:BG};
head(s,"BACKGROUND","Hepatocytes are transcriptionally zonated","BACKGROUND");
s.addShape(p.shapes.RECTANGLE,{x:1.0,y:1.85,w:10.4,h:0.55,fill:{color:PP}});
s.addShape(p.shapes.RECTANGLE,{x:1.0,y:1.85,w:5.2,h:0.55,fill:{color:PC}});
s.addText("Pericentral (zone 3)",{x:1.15,y:1.85,w:5.0,h:0.55,fontSize:15,bold:true,color:WHITE,align:"left",valign:"middle"});
s.addText("Periportal (zone 1)",{x:6.3,y:1.85,w:5.0,h:0.55,fontSize:15,bold:true,color:WHITE,align:"right",valign:"middle"});
s.addText("Central vein",{x:0.6,y:2.45,w:2.4,h:0.3,fontSize:12.5,color:MUTE,align:"left"});
s.addText("Portal tract",{x:9.4,y:2.45,w:2.4,h:0.3,fontSize:12.5,color:MUTE,align:"right"});
s.addText([{text:"GLUL, CYP3A4, CYP2E1 ",options:{bold:true,color:PC}},{text:"— drug metabolism (Wnt-driven)",options:{color:INK}}],
  {x:1.0,y:2.8,w:5.2,h:0.35,fontSize:14,align:"center"});
s.addText([{text:"ASS1, CPS1, PCK1, HAL, ALDOB ",options:{bold:true,color:PP}},{text:"— urea cycle",options:{color:INK}}],
  {x:6.2,y:2.8,w:5.2,h:0.35,fontSize:14,align:"center"});
// two co-equal cards: their published claim  vs  our question
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.65,y:3.5,w:6.0,h:2.78,fill:{color:TEALD},rectRadius:0.08,shadow:sh()});
s.addText([{text:"THE PUBLISHED CLAIM   ",options:{bold:true,fontSize:12,color:"9FC0C4",charSpacing:2}},
  {text:"— Gribben 2024",options:{fontSize:11,color:"7E9DA0"}}],
  {x:0.9,y:3.66,w:5.5,h:0.3,align:"left",margin:0});
s.addText("“Hepatocytes lose their zonation.”",{x:0.9,y:4.0,w:5.5,h:0.42,fontSize:18,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"top",margin:0});
s.addText([
  {text:"End-stage hepatocytes co-express pericentral + periportal markers — validated by imaging + protein.",options:{bullet:true,color:"D7E6E8",breakLine:true}},
  {text:"Hepatocyte↔cholangiocyte transdifferentiation, “prominent in end-stage.”",options:{bullet:true,color:"D7E6E8"}}],
  {x:1.1,y:4.62,w:5.35,h:1.55,fontSize:12.5,align:"left",valign:"top",paraSpaceAfter:8});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.85,y:3.5,w:5.85,h:2.78,fill:{color:"FFFFFF"},line:{color:ORANGE,width:1.5},rectRadius:0.08,shadow:sh()});
s.addText("OUR QUESTION",{x:7.1,y:3.66,w:5.4,h:0.3,fontSize:12,bold:true,color:ORANGE,charSpacing:2,align:"left",margin:0});
s.addText("Does hepatocyte zonation degrade across MASLD — and is it linked to the hepatocyte→cholangiocyte transdifferentiation they describe?",
  {x:7.1,y:4.05,w:5.4,h:2.0,fontSize:16.5,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
foot(s);
s.addNotes("Minimal background: the liver lobule is zonated — pericentral hepatocytes (near the central vein) run one program (GLUL, CYP3A4, the CYP/detox genes), periportal hepatocytes (near the portal tract) run another (ASS1, CPS1, PCK1, urea cycle). Gribben et al.'s claim is that in MASLD hepatocytes lose this zonation and acquire cholangiocyte-like identity. That is what we test.");

sep("The catch","our first approach is misleading — and the tissue itself is confounded");
// ============================================================ THE METRIC — A TRAP  [THE CATCH]
s=p.addSlide(); s.background={color:BG};
head(s,"THE FIRST APPROACH","A relative ruler — and what it hides","THE CATCH");
s.addText("THE OLD RULER",{x:0.7,y:1.8,w:6.0,h:0.3,fontSize:13,bold:true,color:MUTE,charSpacing:2,align:"left"});
s.addText("We first read it with a z-scored zonation coordinate and marker–marker correlations, pooled across all samples.",
  {x:0.7,y:2.15,w:6.0,h:0.9,fontSize:15,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:3.45,w:6.0,h:1.65,fill:{color:"FBEEE9"},line:{color:CONFOUND,width:1},rectRadius:0.07});
s.addText("WHAT IT SHOWED",{x:0.92,y:3.6,w:5.6,h:0.3,fontSize:12,bold:true,color:CONFOUND,charSpacing:2,align:"left"});
s.addText("“Hepatocytes lose their zonation; the pericentral program turns off, strongest at end-stage.”",
  {x:0.92,y:3.95,w:5.6,h:1.05,fontSize:15,italic:true,bold:true,color:SLATE,align:"left",valign:"top"});
s.addText("This is the published finding — our first, relative reading reproduced it.",
  {x:0.7,y:5.35,w:6.0,h:0.5,fontSize:12.5,italic:true,color:MUTE,align:"left",valign:"top"});
// THE TRAP — what a relative summary hides, as cards (not bullets)
s.addText("THE TRAP",{x:7.0,y:1.8,w:5.9,h:0.3,fontSize:13,bold:true,color:ORANGE,charSpacing:2,align:"left"});
const trap=[
  ["Hides who moved","no counts — which cells, how many, and from where."],
  ["Mixes the samples","pools healthy + biopsy + end-stage across a hidden acquisition break."],
  ["Bent by artifacts","depth, cell number and tissue source all tilt a z-score or correlation."]];
let tyy=2.25;
for(const c of trap){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.0,y:tyy,w:5.9,h:1.0,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x:7.0,y:tyy,w:0.1,h:1.0,fill:{color:CONFOUND}});
  s.addText(c[0],{x:7.32,y:tyy+0.14,w:5.4,h:0.35,fontSize:16,bold:true,color:CONFOUND,align:"left",valign:"top",margin:0});
  s.addText(c[1],{x:7.32,y:tyy+0.52,w:5.4,h:0.42,fontSize:12.5,color:INK,align:"left",valign:"top",margin:0});
  tyy+=1.12;
}
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.0,y:tyy+0.03,w:5.9,h:0.62,fill:{color:"E7F0EE"},line:{color:TEAL,width:1},rectRadius:0.06});
s.addText("→ so we count molecules instead.",
  {x:7.0,y:tyy+0.03,w:5.9,h:0.62,fontSize:15,bold:true,color:TEALD,align:"center",valign:"middle"});
foot(s);
s.addNotes("The first catch: the metric. We first read it with a relative ruler — a z-scored zonation coordinate + marker correlations pooled over all samples — which produced 'hepatocytes lose zonation; pericentral turns off, strongest at end-stage.' But a relative summary hides who moved, pools healthy+biopsy+end-stage across a hidden sampling break, and is bent by depth/cell-number/tissue-source; and even biopsy-only it stays depth-sensitive and conflates turn-off vs de-zonation vs noise. So we switched to raw molecule counts. The second catch is the tissue itself (next slide).");
// ============================================================ THE TISSUE — confound + stress merged  [THE CATCH]
s=p.addSlide(); s.background={color:BG};
head(s,"THE TISSUE — A CONFOUND","Stage is entangled with how the tissue was taken","THE CATCH");
// ① stage tracks acquisition (timeline)
s.addText("①  Stage tracks how the tissue was taken",{x:0.6,y:1.5,w:12.3,h:0.32,fontSize:14.5,bold:true,color:CONFOUND,align:"left"});
const xs=[1.0,2.7,3.9,5.1,6.3,7.5,9.0], lab=["Healthy","F0","F1","F2","F3","F4","End-stage"];
const colb=[CONFOUND,BIOPSY,BIOPSY,BIOPSY,BIOPSY,BIOPSY,ENDSTAGE], wd=[1.35,1.1,1.1,1.1,1.1,1.1,2.1];
s.addShape(p.shapes.LINE,{x:1.0,y:2.05,w:10.1,h:0,line:{color:MUTE,width:1.5,endArrowType:"triangle"}});
for(let i=0;i<lab.length;i++){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:xs[i],y:2.18,w:wd[i],h:0.56,fill:{color:colb[i]},rectRadius:0.06,shadow:sh()});
  s.addText(lab[i],{x:xs[i],y:2.18,w:wd[i],h:0.56,fontSize:13,bold:true,color:WHITE,align:"center",valign:"middle"});
}
s.addShape(p.shapes.RECTANGLE,{x:0.93,y:2.12,w:1.49,h:0.96,fill:{type:"none"},line:{color:CONFOUND,width:1.8,dashType:"dash"}});
s.addShape(p.shapes.RECTANGLE,{x:8.92,y:2.12,w:2.26,h:0.96,fill:{type:"none"},line:{color:CONFOUND,width:1.8,dashType:"dash"}});
s.addText("deceased-donor",{x:0.55,y:2.8,w:2.3,h:0.25,fontSize:11,color:CONFOUND,align:"center"});
s.addText("16-gauge needle biopsies",{x:2.7,y:2.8,w:5.5,h:0.25,fontSize:12,bold:true,color:BIOPSY,align:"center"});
s.addText("explants",{x:8.92,y:2.8,w:2.26,h:0.25,fontSize:11,color:ENDSTAGE,align:"center"});
s.addText([{text:"The ends aren’t acquisition-matched to the biopsies (2/8/12/12/4) → ",options:{color:INK}},{text:"we use biopsy-only F1–F4.",options:{bold:true,color:BIOPSY}}],
  {x:1.0,y:3.2,w:11.2,h:0.35,fontSize:13.5,align:"center"});
// ② the ends carry organ-wide stress
s.addText("②  And the ends carry organ-wide stress",{x:0.6,y:3.78,w:12.3,h:0.32,fontSize:14.5,bold:true,color:STRESS,align:"left"});
img(s,"fig_stress.png",{x:0.3,y:4.2,w:8.2,h:2.25});
figcap(s,0.3,6.48,8.2,"Figure 1.  Procurement-stress module by tissue source (donor-level).");
s.addText("Stress spikes even where there’s no zonation.",
  {x:8.75,y:4.25,w:4.25,h:0.6,fontSize:15.5,bold:true,color:STRESS,align:"left",valign:"top"});
s.addText([{text:"Immediate-early / heat-shock genes jump 18× in the ends — but ",options:{}},
  {text:"endothelium, which has no zonation program, jumps 18× too",options:{bold:true}},
  {text:"; hypoxia (HIF) stays flat. So it’s acute handling¹, not a zonation change.",options:{}}],
  {x:8.75,y:5.05,w:4.25,h:1.45,fontSize:12.5,color:INK,align:"left",valign:"top"});
fcite(s,"¹ Dissociation / handling artifact: van den Brink et al. 2017; O’Flanagan et al. 2019; Denisenko et al. 2020.   Provenance: paper Methods + GSE202379 metadata.");
foot(s);
s.addNotes("The tissue catch, both halves on one slide. (1) Stage is collinear with acquisition: healthy and end-stage are deceased-donor cubes/explants, F0-F4 are needle biopsies (2/8/12/12/4) — the ends are not acquisition-matched, so a 'progressive' trajectory can be manufactured by procurement/ischemia/dissociation/batch. (2) The ends also carry organ-wide stress: IEG+HSP spike ~18x in explants, but endothelium (no zonation program) spikes the same ~18x, and hypoxia (HIF) stays flat (1.7-2.6x) — acute handling, not a zonation program. Both reasons → exclude the deceased-donor/explant ends, use biopsy-only F1-F4. Verified from the paper's Methods + dataset metadata.");

sep("Method","how we re-test it, in counts");
// ============================================================ SLIDE 6 — VOCABULARY + MOVES (merged)  [METHOD]
s=p.addSlide(); s.background={color:BG};
head(s,"THE VOCABULARY","Four classes — and the four ways they can move","METHOD");
s.addText([{text:"Every hepatocyte is one of four classes (left). ",options:{bold:true,color:INK}},
  {text:"“Losing zonation” = cells redistribute across them — four distinct moves (right), each with its own count signature.",options:{color:INK}}],
  {x:0.7,y:1.45,w:12.3,h:0.5,fontSize:15,align:"left"});
// ---- LEFT: the four classes (2x2) ----
s.addText("THE FOUR CLASSES",{x:0.6,y:2.2,w:5.9,h:0.3,fontSize:13,bold:true,color:MUTE,charSpacing:2,align:"left"});
s.addText("periportal program →",{x:1.95,y:2.56,w:4.4,h:0.26,fontSize:11,bold:true,color:PP,align:"center",margin:0});
s.addText("PP −",{x:1.95,y:2.84,w:2.15,h:0.26,fontSize:11,bold:true,color:MUTE,align:"center",margin:0});
s.addText("PP +",{x:4.2,y:2.84,w:2.15,h:0.26,fontSize:11,bold:true,color:MUTE,align:"center",margin:0});
s.addText("pericentral\nprogram ↓",{x:0.28,y:3.85,w:1.55,h:0.6,fontSize:11,bold:true,color:PC,align:"center",margin:0});
s.addText("PC +",{x:0.5,y:3.45,w:1.35,h:0.26,fontSize:11,bold:true,color:MUTE,align:"center",margin:0});
s.addText("PC −",{x:0.5,y:4.8,w:1.35,h:0.26,fontSize:11,bold:true,color:MUTE,align:"center",margin:0});
classbox(s,1.95,3.15,2.15,1.25,"PC-anchor","pericentral only",PC);
classbox(s,4.2,3.15,2.15,1.25,"Dual","both — co-expression",DUAL);
classbox(s,1.95,4.5,2.15,1.25,"Null","neither",NULL,INK);
classbox(s,4.2,4.5,2.15,1.25,"PP-anchor","periportal only",PP);
// ---- divider ----
s.addShape(p.shapes.LINE,{x:6.7,y:2.55,w:0,h:3.25,line:{color:"D7D0C4",width:1}});
// ---- RIGHT: the four moves (2x2 chips, colours match the box each move touches) ----
s.addText("THE FOUR MOVES",{x:7.0,y:2.2,w:6.0,h:0.3,fontSize:13,bold:true,color:MUTE,charSpacing:2,align:"left"});
chip(s,7.0,2.7,2.9,1.4,"Depletion\nan anchor box ↓",PC);
chip(s,10.05,2.7,2.9,1.4,"Co-expression\nthe dual box ↑",DUAL);
chip(s,7.0,4.25,2.9,1.4,"Turn-off\nthe null box ↑",NULL,INK);
chip(s,10.05,4.25,2.9,1.4,"Composition shift\nPP : PC ratio moves",PP);
// ---- bottom line ----
s.addText([{text:"The moves are dissociable — an emptying anchor box (depletion) and a filling null box (turn-off) are opposite directions; neither implies the other. ",options:{color:INK}},
  {text:"A single z-score or correlation collapses all four into one number — only counting molecules tells them apart.",options:{italic:true,color:MUTE}}],
  {x:0.7,y:6.1,w:12.3,h:0.8,fontSize:13,align:"left",valign:"top"});
foot(s);
s.addNotes("Vocabulary + moves on one slide. LEFT — the 2x2: every hepatocyte is sorted into exactly one of four classes by which program it runs (pericentral detected? x periportal detected?): PC-anchor (PC only), PP-anchor (PP only), Dual (both — co-expression), Null (neither — double-negative). RIGHT — 'losing zonation' is not one event but four distinct moves among these boxes, each with its own count signature: Depletion (an anchor box shrinks), Co-expression (the dual box fills), Turn-off (the null box fills), Composition shift (the PP:PC ratio tilts); chip colours match the box each move touches. They are dissociable — a pole can convert to the opposite pole (depletion, null untouched) and cells can go double-negative without any pole shrinking (turn-off, no depletion). A single relative summary (z-score, correlation, UMAP axis) is scale-free — it divides out the level and reads only the gradient's shape, collapsing all four into one number; absolute counts keep them separate. We track all four, not just the pericentral depletion we expected.");

// ============================================================ SLIDE 7 — THE GRADIENT AXIS  [METHOD]
s=p.addSlide(); s.background={color:BG};
head(s,"THE GRADIENT AXIS","Beyond the boxes — zonation is a gradient","METHOD");
s.addText([{text:"Zonation is a continuous gradient — cells strung on an anti-diagonal. It can weaken two ways ",options:{}},
  {text:"without any cell changing class:",options:{bold:true}}],
  {x:0.7,y:1.5,w:12.3,h:0.45,fontSize:15.5,color:INK,align:"left"});
img(s,"fig_gradient_schematic.png",{x:0.4,y:2.05,w:7.7,h:4.05});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:8.25,y:2.1,w:4.65,h:1.85,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
s.addText([{text:"Compression  ",options:{bold:true,fontSize:17,color:TEAL,fontFace:SERIF}},{text:"— shape",options:{italic:true,fontSize:13,color:MUTE}}],
  {x:8.45,y:2.24,w:4.25,h:0.35,align:"left",margin:0});
s.addText("Balance drifts to the middle; the poles’ contrast shrinks.",
  {x:8.45,y:2.66,w:4.25,h:0.55,fontSize:13,color:INK,align:"left",valign:"top"});
s.addText([{text:"Mild, non-monotone → ",options:{color:"14532D"}},{text:"gradient present.",options:{bold:true,color:"14532D"}}],
  {x:8.45,y:3.4,w:4.25,h:0.4,fontSize:12,italic:true,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:8.25,y:4.15,w:4.65,h:1.9,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
s.addText([{text:"Dimming  ",options:{bold:true,fontSize:17,color:AMBER,fontFace:SERIF}},{text:"— level",options:{italic:true,fontSize:13,color:MUTE}}],
  {x:8.45,y:4.29,w:4.25,h:0.35,align:"left",margin:0});
s.addText("The pericentral detox program declines in level — same balance, lower volume.",
  {x:8.45,y:4.71,w:4.25,h:0.6,fontSize:13,color:INK,align:"left",valign:"top"});
s.addText([{text:"Real coordinated decline → ",options:{color:"7C2D12"}},{text:"a finding (Results).",options:{bold:true,color:"7C2D12"}}],
  {x:8.45,y:5.5,w:4.25,h:0.4,fontSize:12,italic:true,align:"left",valign:"top"});
s.addText([{text:"Matched biopsies: shape holds (no compression); level dims (detox — confirmed next). ",options:{bold:true}},
  {text:"Only the explant collapses to one pole.",options:{italic:true,color:MUTE}}],
  {x:0.45,y:6.3,w:7.7,h:0.6,fontSize:12.5,color:"334155",align:"left",valign:"top"});
foot(s);
s.addNotes("The continuous-gradient axis, which the discrete box-counts cannot capture. Compression = loss of SHAPE (per-cell PC/(PC+PP) balance drifts to the middle); dimming = loss of LEVEL (the program's relative magnitude falls while the balance is unchanged). Compression: mild non-monotone middle drift peaking at F3, both poles populated — gradient present; only the explant collapses. Dimming: the pericentral detox program declines in relative level — a real coordinated finding, confirmed in Results by gene-set + per-cell tests. Cells keep their identity.");

// ============================================================ SLIDE 9 — METHOD  [METHOD]
s=p.addSlide(); s.background={color:BG};
head(s,"HOW WE MEASURE","Raw-count anchor classification","METHOD");
const steps=["raw UMI counts","down-thin to 1,500","marker ON if ≥ 2 UMI","classify nucleus (e.g. PC)","fraction per donor"];
let px=0.35; for(let i=0;i<steps.length;i++){ const w=2.35;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:px,y:1.7,w:w,h:0.8,fill:{color:i==2?"EDE9FE":LIGHT},line:{color:i==2?DUAL:"CBD5E1",width:1.2},rectRadius:0.07});
  s.addText(steps[i],{x:px,y:1.7,w:w,h:0.8,fontSize:14,bold:i==2,color:i==2?DUAL:INK,align:"center",valign:"middle",margin:3});
  if(i<steps.length-1) s.addShape(p.shapes.LINE,{x:px+w,y:2.1,w:0.22,h:0,line:{color:MUTE,width:1.6,endArrowType:"triangle"}});
  px+=w+0.22; }
const why=[
  ["Raw counts, not SCT","A single molecule may be ambient — absolute detection is what matters.",INK],
  ["Depth-matched¹","Down-thin every nucleus to 1,500 UMIs so depth can’t drive detection (stable at 1k / 1.5k / 3k).",BIOPSY],
  ["≥2 UMI, not ≥1","Kills ambient soup — apparent co-expression 7–10% → 0.2–0.5%.",DUAL],
  ["Donor is the unit (~47)","No pseudoreplication. Robust on 6 marker sets (2–1,637 genes, incl. Paper 2’s own).",PC]];
for(let i=0;i<4;i++){ const col=i%2,row=Math.floor(i/2); const x=0.7+col*6.05,y=3.05+row*1.5;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:5.9,h:1.32,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w:0.1,h:1.32,fill:{color:why[i][2]}});
  s.addText(why[i][0],{x:x+0.3,y:y+0.15,w:5.4,h:0.4,fontSize:16,bold:true,color:why[i][2],align:"left",valign:"top",margin:0});
  s.addText(why[i][1],{x:x+0.3,y:y+0.6,w:5.4,h:0.62,fontSize:13,color:INK,align:"left",valign:"top",margin:0});
}
fcite(s,"¹ Depth-matched down-sampling: Amezquita et al., Nat. Methods 2020.   ·   Raw-extraction integrity: 9/9 sanity checks pass (integer UMIs; 69,426 hepatocytes match the paper).");
foot(s);
s.addNotes("Why raw counts: a single marker molecule may be ambient, so absolute detection matters and SCT-normalized values are the wrong object. Down-thin every nucleus to a common 1,500-UMI budget, call a marker on at >=2 UMIs, classify each hepatocyte PC/PP/dual/null, infer at the donor level (~47). The >=2 cut matters: at >=1 UMI apparent co-expression is ~7-10% (ambient soup), collapsing ~40x to ~0.2-0.5% at >=2. Robust on 6 marker sets spanning 2 to 1,637 genes (incl. Paper 2's own) and the full threshold grid. Raw-extraction integrity: 9/9 sanity checks pass (integer UMIs, library 920-49,854 not the SCT band, hepatocyte count = the paper's 69,426).");

sep("Results","what the counts actually say");
// ============================================================ SLIDE 10 — RESULT  [RESULTS]
s=p.addSlide(); s.background={color:BG};
head(s,"THE RESULT","No depletion signal across matched biopsies","RESULTS");
img(s,"fig_result3.png",{x:0.2,y:1.6,w:9.2,h:4.55});
figcap(s,0.2,6.3,9.2,"Figure 2.  Pericentral / periportal anchor and dual co-expression across matched biopsy F1–F4 (box = per-donor spread; F0 n=2 omitted — in backup).");
s.addText([
  {text:"No depletion.\n",options:{bold:true,color:PC,breakLine:true}},{text:"PC & PP anchors flat across F1–F4.\n\n",options:{breakLine:true}},
  {text:"No co-expression.\n",options:{bold:true,color:DUAL,breakLine:true}},{text:"Dual stays ~0.4% (vs 2.9% in explants).\n\n",options:{breakLine:true}},
  {text:"Null & PP:PC flat too.\n",options:{bold:true,color:"475569",breakLine:true}},{text:"44/36/39/39%;  ratio ≈ 1.1.\n\n",options:{breakLine:true}},
  {text:"→ no de-zonation signal.",options:{bold:true,color:BIOPSY,fontSize:16}}],
  {x:9.55,y:1.65,w:3.5,h:4.1,fontSize:14,color:INK,align:"left",valign:"top",paraSpaceAfter:2});
s.addText("Spread, the equivalence bound (> ±19 pp excluded) and the 10-confounder audit — all in backup.",
  {x:9.55,y:6.05,w:3.5,h:0.8,fontSize:11,italic:true,color:MUTE,align:"left",valign:"top"});
foot(s);
s.addNotes("The core result. PC and PP anchor fractions are flat/non-monotone across F1-F4 — no depletion. Dual co-expression at the ambient-robust >=2-UMI cut stays ~0.4% and does not trend (vs ~2.9% in confounded explants). Null (44/36/39/39%) and PP:PC (~1.1) are flat too. WHY READABLE DESPITE THE SPREAD: donors scatter ~25-35 pp within each stage (SD ~12 pp), but the donor is the replicate, so each stage average has SE ~ SD/sqrt(n) ~ 4 pp; the spread is the same at every stage — noise around a flat line, not a hidden trend. EQUIVALENCE (TOST): a shift > ±19 pp is excluded; a <=10 pp drift is not (F4 n=4). F0 OMITTED: its 2 donors disagree 16.6 pp on the PC anchor (44% vs 28%), too unstable to anchor a trend, and it carries the highest PC fraction of any stage so dropping it doesn't flatter the result. QA: 10 confounders audited (source, stress, batch, depth, ambient, ploidy, cholangiocyte, discard, covariates, lobe) — none manufactures the result. All in backup.");

// ============================================================ SLIDE 11 — GRADIENT IN DATA  [RESULTS]
s=p.addSlide(); s.background={color:BG};
head(s,"THE GRADIENT, IN DATA","Cells stay spread across the zones — no collapse","RESULTS");
s.addText([{text:"Each panel: where hepatocytes fall on the pericentral ↔ periportal axis.  ",options:{bold:true,color:INK}},
  {text:"A spread of positions = zonation present;  cells bunched into one pile = collapse.",options:{color:MUTE}}],
  {x:0.7,y:1.48,w:12.3,h:0.35,fontSize:14.5,align:"left",margin:0});
img(s,"fig_gradient.png",{x:0.4,y:1.98,w:12.5,h:3.25});
figcap(s,0.4,5.35,12.5,"Figure 3.  Per-cell zonal balance by stage (down-thinned to 1,500 UMIs, ≤300 nuclei/donor). Dashed outline = the F1 distribution, repeated on each panel: biopsy F1–F4 barely move; only the explant collapses to the periportal pole.");
s.addText([
  {text:"Across biopsy F1–F4 the mass stays spread — the middle [0.4–0.6) drifts only 22 → 24 → 28 → 26% (peak F3, then reverts), non-monotone and mild. ",options:{}},
  {text:"Only the confounded explant collapses to a single (periportal) pole.",options:{bold:true,color:CONFOUND}}],
  {x:0.7,y:5.9,w:12.2,h:0.95,fontSize:14.5,color:INK,align:"left",valign:"top"});
foot(s);
s.addNotes("The per-cell gradient view — the most direct test of compression. x-axis is each cell's pericentral share PC/(PC+PP): 0 = all periportal, 1 = all pericentral; a spread of positions means zonation is intact, cells bunching into one pile means collapse. Across biopsy F1-F4 the distribution stays spread, with only a mild non-monotone middle drift peaking at F3 (it reverts at F4) — gradient present, not collapsed. The explant collapses onto the periportal pole — the same acquisition confound. On the rightward lean: the histograms center above 0.5 because the pericentral program is summed over 7 broadly/highly expressed CYP/detox genes vs 6 periportal genes — a marker-set asymmetry, not biology, and irrelevant to the claim, which is the CHANGE across stages (the lean is constant and cancels out). The dashed reference line marks the F1 centre, repeated across panels, to show it does not move.");

// ============================================================ SLIDE 13 — GENOME-WIDE  [RESULTS]
s=p.addSlide(); s.background={color:BG};
head(s,"GENOME-WIDE","Per gene, nothing usable moves","RESULTS");
img(s,"fig_volcano.png",{x:0.3,y:1.55,w:8.7,h:4.5});
figcap(s,0.3,6.05,8.7,"Figure 4.  Genome-wide pseudobulk differential expression, cirrhotic F4 vs F1 (edgeR).");
s.addText([
  {text:"64 of ~21,000 genes pass FDR¹ — ",options:{bold:true}},{text:"mostly biliary / ductular.\n\n",options:{}},
  {text:"Zonation genes flat ",options:{bold:true,color:PC}},{text:"(GLUL FDR 0.80). No large single-gene program.\n\n",options:{}},
  {text:"But a weak program, spread thinly across many genes, hides from per-gene FDR — ",options:{}},
  {text:"the coordinated pericentral-detox decline is exactly that (next slide).",options:{bold:true,color:AMBER}}],
  {x:9.2,y:1.8,w:3.85,h:4.2,fontSize:14,color:INK,align:"left",valign:"top",paraSpaceAfter:6});
fcite(s,"¹ Pseudobulk: Squair et al. 2021; edgeR / TMM: Robinson, McCarthy & Smyth 2010; Robinson & Oshlack 2010.");
foot(s);
s.addNotes("Per-gene pseudobulk: nothing usable moves (64/21,000 significant, mostly biliary/ductular; zonation flat, GLUL FDR 0.80). No large single-gene program. But per-gene FDR catches a big change in any ONE gene; a weak coordinated program (many genes each drifting a little, same direction) slips past — that is the pericentral-detox decline shown on the next slide.");

// ============================================================ SLIDE 13b — THE ONE REAL CHANGE (dimming)
s=p.addSlide(); s.background={color:BG};
head(s,"THE ONE REAL CHANGE","Pericentral detox dims — identity stays","RESULTS");
s.addText([{text:"Cells keep their class — ",options:{bold:true}},{text:"but within pericentral nuclei the detox program’s level falls with fibrosis (the one hint our counts gave, now confirmed).",options:{}}],
  {x:0.7,y:1.5,w:12.3,h:0.5,fontSize:15.5,color:INK,align:"left"});
img(s,"fig_dimming.png",{x:0.45,y:2.0,w:12.45,h:3.5});
figcap(s,0.45,5.55,12.45,"Figure 5.  Left — within-PC detox output¹ (depth-matched transcripts per PC nucleus) across fibrosis. Right — gene-set programs²: PC detox / identity down, biliary + fibrogenesis up, validating controls behaved.");
s.addText([{text:"Like a radio: ",options:{bold:true,color:TEAL}},{text:"the genre held (cells keep identity); the volume dropped (the program dims).   ",options:{italic:true}},
  {text:"A relative decline (transcripts within a fixed budget), not proven absolute molecule loss; a donor-level trend; could partly reflect a shift among PC subzones. No single gene clears per-gene FDR — only the coordinated set + the per-cell trend.",options:{color:MUTE}}],
  {x:0.7,y:6.0,w:12.3,h:0.85,fontSize:12.5,color:"334155",align:"left",valign:"top"});
fcite(s,"¹ Within-PC detox output: depth-matched to 1,500 UMIs, donor-level Spearman (ρ=−0.48, p=0.003); measured on detox genes (CYP2E1, CYP1A2, ADH4…) disjoint from the GLUL/CYP3A4 identity anchors — so the anchor fraction stays flat while the module dims.   ² Gene-set: camera — Wu & Smyth 2012; ROAST — Wu et al. 2010; GSEA — gseapy.");
foot(s);
s.addNotes("The one real biopsy-internal change. LEFT: within-PC detox output (detox transcripts per PC nucleus, depth-matched to 1,500 UMIs) falls from ~11.9 at F1 to ~8.8 at F4; donor-level Spearman rho -0.48, p=0.003. F0 (n=2) faded. RIGHT: gene-set test (camera) — PC detox (CYP) FDR 2e-6, PC identity 1.5e-4, phase-II 7e-3, all DOWN; biliary/ductular + fibrogenesis/inflammation controls UP; ER-stress flat (validating controls). CAREFUL FRAMING: this is a RELATIVE transcript decline within a fixed 1,500-UMI budget, not proven absolute molecule loss; it is a donor-level trend (not pseudoreplicated); it could partly reflect a shift among PC subzones rather than pure within-cell downregulation; no single detox gene clears per-gene FDR. Cells retain their pericentral/periportal identities — functional dimming of a zonated program, NOT de-zonation or transdifferentiation. This was our original within-PC metric (the one count hint), conservatively shelved as borderline, now confirmed by the coordinated set test + the full-trajectory trend, after ruling out a composition artifact (TMM, contaminant removal, the per-cell measure).");

// ============================================================ SLIDE 14 — SOURCE  [RESULTS]
s=p.addSlide(); s.background={color:BG};
head(s,"SOURCE","The biliary signal: most likely compositional — a lead","RESULTS");
img(s,"fig_compositional.png",{x:0.3,y:1.5,w:12.7,h:3.35});
figcap(s,0.3,4.92,12.7,"Figure 6.  Source attribution — cross-lineage abundance, decontX ambient-RNA removal, and the F4 ductular reaction.");
const lad=[
 ["STRONG","Biliary genes are cholangiocyte genes; hepatocyte co-expression ~0.4%","065F46","E7F2ED"],
 ["SUGGESTIVE","decontX¹ halves the hits — an ambient contribution, not proof","B45309","FBF0E2"],
 ["OPEN","EPCAM / SPINT2 / B3GNT3 survive — a rare intrinsic state not excluded; CXCL10 a separate inflammatory lead","BE123C","FBEEE9"]];
let ly=5.28;
for(const row of lad){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:ly,w:12.2,h:0.42,fill:{color:row[3]},rectRadius:0.05});
  s.addText(row[0],{x:0.78,y:ly,w:1.9,h:0.42,fontSize:12,bold:true,color:row[2],charSpacing:1,valign:"middle",margin:0});
  s.addText(row[1],{x:2.7,y:ly,w:9.9,h:0.42,fontSize:13,color:INK,valign:"middle",margin:0});
  ly+=0.47;
}
fcite(s,"¹ Ambient-RNA removal: decontX — Yang et al., Genome Biol. 2020.    Source attribution is a lead, not a closed verdict.");
foot(s);
s.addNotes("Distinguish evidence levels. Strong: the genes are 5-78x more abundant in cholangiocytes and per-cell hepatocyte co-expression is ~0.4%. Suggestive: decontX halves the hits and drops SOX4/SOX9 — supports an ambient contribution but not proof. Open: EPCAM/SPINT2/B3GNT3 survive — a rare intrinsic state is not excluded; CXCL10 is set aside as a candidate real inflammatory signal. So the dominant evidence points to composition/ambient RNA, a lead not a closed verdict.");

// ============================================================ SLIDE 15 — CONCLUSION  [DARK]
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
s.addShape(p.shapes.RECTANGLE,{x:0.85,y:0.5,w:0.16,h:0.26,fill:{color:AMBER}});
s.addText("CONCLUSION",{x:1.08,y:0.46,w:11.5,h:0.4,fontSize:14,bold:true,color:AMBER,charSpacing:3,align:"left"});
s.addText("Zonal identity holds — the pericentral detox program dims",
  {x:0.85,y:0.85,w:11.8,h:0.8,fontSize:29,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
const cols=[
  {h:"Conclusions",c:"F0B27A",items:["Full healthy→end-stage trajectory is source-confounded.","In biopsy F1–F4 cells keep zonal identity — no de-zonation (large shift excluded).","Two real biopsy-internal signals: a compositional biliary signal (a lead), and a confirmed pericentral-detox dimming (gene-set + per-cell)."]},
  {h:"Limits",c:"FCA5A5",items:["“PC-like program,” not lobular location — counts can’t see spatial position.","Imaging / protein / organoid evidence not re-analyzed.","F4 has only 4 biopsy donors.","Detox dimming is a RELATIVE decline (not proven absolute) and could partly reflect a shift among PC subzones; self-contained test clears only the CYP core."]},
  {h:"Next",c:"9CC6CC",items:["Spatial / independent-biopsy validation of the detox-dimming gradient.","Leave-one-F4-donor-out DGE.","Quantitative contamination model for the biliary lead.","Functional readout of pericentral detox capacity."]}
];
const takes=[
  {n:"01",t:"Cells keep their zonal identity — no de-zonation signal"},
  {n:"02",t:"The one real change: the pericentral detox program dims"},
  {n:"03",t:"The dramatic trajectory tracks acquisition, not disease"}];
let ty=2.1; for(const k of takes){
  s.addText(k.n,{x:0.92,y:ty-0.06,w:1.25,h:0.8,fontSize:37,bold:true,color:AMBER,fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(k.t,{x:2.4,y:ty,w:10.2,h:0.7,fontSize:21,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle",margin:0});
  ty+=1.2; }
s.addShape(p.shapes.LINE,{x:2.4,y:5.7,w:9.95,h:0,line:{color:"2E4A4D",width:1}});
s.addText([{text:"We correct one evidence leg",options:{bold:true,color:WHITE}},
  {text:" — the snRNA marker-correlation; the paper’s imaging and protein staining are untouched. The biliary signal is a separate compositional lead.",options:{color:"C9D6D3"}}],
  {x:0.92,y:5.9,w:11.9,h:0.5,fontSize:15,italic:true,align:"left",valign:"top"});
s.addText("Scope — a “PC-like program,” not lobular location; a weak coordinated gene-set program is not excluded; F4 is only 4 donors.",
  {x:0.92,y:6.72,w:11.9,h:0.4,fontSize:12,color:"8FA3A0",align:"left",valign:"top"});
foot(s);
s.addNotes("Close on the methodological lesson: in single-cell disease atlases, acquisition matching can dominate apparent disease trajectories. Bottom line, narrow and honest: the snRNA-seq evidence for progressive de-zonation does not survive matched-source re-analysis — we correct one evidence leg, the marker-correlation; imaging/protein/organoid untouched; the biliary signal is most consistent with composition/ambient RNA, a rare intrinsic state not excluded.");

// ============================================================ BACKUPS
function back(kicker,t){ const b=p.addSlide(); b.background={color:BG};
  b.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  b.addText("BACKUP  ·  "+kicker,{x:0.74,y:0.30,w:12.0,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3});
  b.addText(t,{x:0.48,y:0.64,w:12.4,h:0.8,fontSize:26,bold:true,color:SLATE,fontFace:SERIF,align:"left"}); return b; }
function bbul(b,items,y){ b.addText(items.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:9}})),
  {x:0.8,y:y||1.6,w:11.6,h:5.0,fontSize:20,color:INK,align:"left",valign:"top"}); }
let b;

b=back("SCOPE","Are you overturning the paper? No");
bbul(b,["We re-tested only the snRNA-seq transcriptional zonation/plasticity evidence.",
  "We did NOT test imaging, protein staining, organoids, or 3D architecture.",
  "Claim: matched biopsy transcriptomes do not show progressive zonation loss.",
  "We agree the strong signal is an end-stage phenomenon."]);

b=back("SECONDARY ENDPOINTS","Null and the PP : PC ratio are flat too");
img(b,"fig_secondary.png",{x:0.3,y:1.65,w:9.0,h:4.35});
figcap(b,0.3,6.05,9.0,"Figure 7.  Null (double-negative) fraction and the periportal : pericentral anchor ratio across biopsy F1–F4 (box = per-donor spread; each point = one donor).");
b.addText([
  {text:"Null (double-negative): ",options:{bold:true,color:"475569"}},{text:"≈ 44 / 36 / 39 / 39% — no rise across stages.\n\n",options:{breakLine:true}},
  {text:"PP : PC ratio: ",options:{bold:true,color:DUAL}},{text:"≈ 1.16 / 1.01 / 1.10 / 1.18 — hovers around the balanced 1 : 1 line.\n\n",options:{breakLine:true}},
  {text:"Same large person-to-person spread as the anchors, same absence of a stage trend.",options:{italic:true,color:MUTE}}],
  {x:9.5,y:1.75,w:3.6,h:4.3,fontSize:13.5,color:INK,align:"left",valign:"top"});

b=back("LOBE","Right, caudate and left lobes all agree");
img(b,"fig_lobe.png",{x:0.8,y:1.5,w:7.6,h:5.0});
figcap(b,0.8,6.5,7.6,"Figure 8.  Zonation-marker detection across Right / Caudate / Left lobes in end-stage explants.");
b.addText([{text:"Detection matches across all three lobes.\n",options:{bold:true,breakLine:true}},
  {text:"Lobe does not explain the signal; explant-vs-biopsy acquisition still does.",options:{}}],
  {x:8.7,y:2.6,w:4.0,h:2.5,fontSize:18,color:INK,align:"left"});

b=back("END-STAGE","Five organs, five phenotypes");
img(b,"fig_explant.png",{x:0.8,y:1.5,w:8.2,h:5.0});
figcap(b,0.8,6.5,8.2,"Figure 9.  Per-explant anchor fractions — end-stage is heterogeneous, not one coherent program.");
b.addText([{text:"PC-anchor 3% → 50%;  PP:PC 0.13 → 20.\n",options:{bold:true,breakLine:true}},
  {text:"Dramatic but NOT one program — pooling manufactures a uniform “collapse.”",options:{}}],
  {x:9.2,y:2.6,w:3.6,h:2.6,fontSize:17,color:INK,align:"left"});

b=back("ROBUSTNESS","Sensitivity grid + equivalence bound");
img(b,"fig_tost.png",{x:6.6,y:1.6,w:6.4,h:4.0});
figcap(b,6.6,5.65,6.4,"Figure 10.  Equivalence bound on the F4-vs-F1 pericentral-anchor change.");
b.addText([{text:"Stable across every variant:\n",options:{bold:true,breakLine:true}},
  {text:"anchor genes, periportal rule, ALDOB in/out, CPS1-based, 1 vs 2 UMI.\n\n",options:{breakLine:true}},
  {text:"No depletion · no dual rise · no turn-off — in all.\n\n",options:{bold:true,color:BIOPSY,breakLine:true}},
  {text:"Bound (TOST): large shift (~19 pp) excluded; subtle drift ≤10 pp not (F4 n=4).",options:{italic:true,color:MUTE}}],
  {x:0.7,y:1.8,w:5.7,h:4.2,fontSize:16,color:INK,align:"left",valign:"top"});

b=back("AUDIT DETAIL","Confounder battery — the numbers");
const AUD=[
  [{text:"Confounder",options:{bold:true}},{text:"What we did  (test · numbers)",options:{bold:true}},{text:"Verdict",options:{bold:true}}],
  ["Tissue source","organ-cube / explant ends are not acquisition-matched to needle biopsy","excluded → biopsy-only F1–F4"],
  ["Procurement stress","IEG+HSP across 6 lineages; hep 18× ≈ endothelial 18× (no zonation)","organ-wide handling, not zonation"],
  ["Sequencing batch","run × source Cramér’s V = 0.84; run × F (biopsy) = 0.40","ends confounded; biopsy estimable"],
  ["Lobe (R / C / L)","marker detection across right / caudate / left lobes in explants","lobe-invariant"],
  ["Sequencing depth","binomial down-thin to B = 1,000 / 1,500 / 3,000 UMIs","PC-share flat at every B (SD 0.006–0.010)"],
  ["Ambient RNA (“soup”)","corr( ALB share , dual fraction ) across 38 donors = +0.04","does not drive co-expression"],
  ["Cholangiocyte mis-annotation","KRT19⁺ ≤ 0.001, EPCAM⁺ ≤ 0.003 in every anchor class","not contaminating cholangiocytes"],
  ["Ploidy / complexity","nFeatures by stage: 2218 / 3063 / 3169 / 2641 / 1984","non-monotone — does not track stage"],
  ["Depth-match discard","3.5–7.8 % dropped below B, uniformly lower-detection","depth-driven, not PC-biased"],
  ["Clinical covariates","partial corr( detox , F | Age ) = −0.32; Age–F = +0.43","demographics do not explain trends"],
];
b.addTable(AUD,{x:0.7,y:1.7,w:12.2,colW:[2.7,6.6,2.9],fontSize:11,color:INK,
  border:{pt:0.5,color:"D7D0C4"}, fill:{color:"FFFFFF"}, rowH:0.42, valign:"middle", align:"left", margin:[2,5,2,5]});

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

b=back("GENE-SET RESULT","Ten pre-specified sets — the detox program goes down");
const GS=[
  [{text:"Gene set",options:{bold:true}},{text:"Zone / program (identity)",options:{bold:true}},{text:"n",options:{bold:true}},{text:"Dir",options:{bold:true}},{text:"camera FDR",options:{bold:true}}],
  ["xenobiotic_CYP","PC detox — phase-I (CYP)","13","↓","2×10⁻⁶"],
  ["detox_phase2","PC detox — phase-II (UGT/GST/SULT)","16","↓","7×10⁻³"],
  ["pericentral_anchors","PC identity (Paper 2 landmarks)","20","↓","1.5×10⁻⁴"],
  ["periportal_anchors","PP identity (Paper 2 landmarks)","20","↑","1.5×10⁻²"],
  ["urea_cycle","PP program (nitrogen)","9","↓","0.12  (ns)"],
  ["bile_acid_lipid","mixed metabolism","20","–","0.72  (ns)"],
  ["cholangiocyte_ductular","biliary / bile-duct markers","10","↑","1.9×10⁻⁵"],
  ["CTRL_interferon","inflammation  (+control)","20","↑","1.5×10⁻³"],
  ["CTRL_EMT","fibrogenesis / scar  (+control)","20","↑","9×10⁻⁶"],
  ["CTRL_ER_stress","unfolded-protein resp.  (−control)","20","–","0.72  (ns)"],
];
b.addTable(GS,{x:0.6,y:1.55,w:12.2,colW:[2.7,4.3,0.7,0.8,3.7],fontSize:12,color:INK,
  border:{pt:0.5,color:"D7D0C4"}, fill:{color:"FFFFFF"}, rowH:0.4, valign:"middle", align:"left", margin:[2,5,2,5]});
b.addText("Donor-level, biopsy F0–F4, limma::camera (GSEA agrees). Pre-specified, no fishing: PC/PP identity = Paper 2’s own landmark genes; CYP / detox / urea / bile = KEGG·HGNC cores; biliary = plasticity.txt + markers; controls = MSigDB Hallmark cores. The validating controls behaved (fibrogenesis & inflammation ↑, ER-stress flat) — proof the test detects real biology, not noise. The pericentral detox + identity programs fall; the see-saw (PP ↑) and biliary ↑ are why we adversarially controlled for composition (it survived).",
  {x:0.6,y:5.95,w:12.3,h:1.1,fontSize:11.5,italic:true,color:MUTE,align:"left"});

b=back("METHODS GLOSSARY","Gene-set testing, in one breath each");
b.addText([
  {text:"Pseudobulk  ",options:{bold:true,color:INK}},{text:"— sum each donor’s hepatocyte counts into one profile per donor (donor = unit of inference).\n",options:{breakLine:true}},
  {text:"CPM  ",options:{bold:true,color:INK}},{text:"— each gene as a share of the donor’s total counts; simple, but compositional (a few surging genes shrink everyone else’s share).\n",options:{breakLine:true}},
  {text:"TMM  ",options:{bold:true,color:BIOPSY}},{text:"— the scaling factor is taken from the bulk of genes after trimming the extreme movers, so surging genes can’t set it → composition-robust.\n",options:{breakLine:true}},
  {text:"Per-gene DGE  ",options:{bold:true,color:INK}},{text:"— test each gene on its own for a fibrosis trend (edgeR); misses a weak shift shared by many genes.\n",options:{breakLine:true}},
  {text:"Gene-set test  ",options:{bold:true,color:AMBER}},{text:"— test a whole pre-specified set at once. camera = competitive (more shifted than the rest of the genome?; Wu & Smyth 2012); ROAST = self-contained (does the set move against zero?; Wu et al. 2010).\n",options:{breakLine:true}},
  {text:"Within-PC detox output  ",options:{bold:true,color:BIOPSY}},{text:"— detox transcripts per pericentral nucleus after equalizing read depth: per-cell, relative to the cell’s own output, immune to between-cell composition.\n",options:{breakLine:true}},
  {text:"Adversarial check  ",options:{bold:true}},{text:"— redo with TMM, with ROAST, with the rising genes removed, and with the per-cell measure; all four agreed → the dimming is real.",options:{}}],
  {x:0.8,y:1.7,w:11.9,h:5.2,fontSize:16,color:INK,align:"left",valign:"top",paraSpaceAfter:9});

b=back("SCENARIO COVERAGE","Every de-zonation route, mapped to its signature");
const TAX=[
  [{text:"Mechanism",options:{bold:true}},{text:"Signature",options:{bold:true}},{text:"Biopsy F0→F4 (donor-median)",options:{bold:true}},{text:"Verdict",options:{bold:true}}],
  ["Pericentral depletion","PC-anchor fraction ↓","36 / 19 / 23 / 22 / 21 %","flat → no depletion"],
  ["Periportal depletion","PP-anchor fraction ↓","20 / 21 / 22 / 24 / 24 %","flat → no depletion"],
  ["Dimming","within-PC level ↓ (magnitude)","11.9 → 8.8 detox UMI/nuc (F1→F4); ρ = −0.48","REAL — gene-set + within-PC confirm (CYP FDR 2e-6)"],
  ["Co-expression","dual (≥2 UMI) fraction ↑","~0.0 / 0.2 / 0.4 / 0.2 / 0.2 %","ambient soup → no"],
  ["Gradient compression","per-cell balance → middle","mild, non-monotone (peak F3)","gradient present"],
  ["Turn-off","null (double-neg) fraction ↑","34 / 44 / 36 / 39 / 39 %","flat → no turn-off"],
  ["Composition shift","PP : PC anchor ratio","0.62 / 1.16 / 1.01 / 1.10 / 1.18","~flat → no shift"],
  ["Induction","program level ↑","flat in biopsy; rises only end-stage","explant-only"],
];
b.addTable(TAX,{x:0.7,y:1.65,w:12.0,colW:[2.5,2.95,3.95,2.6],fontSize:12.5,color:INK,
  border:{pt:0.5,color:"C9BFAE"}, fill:{color:"FFFFFF"},
  rowH:0.4, valign:"middle", align:"left",
  margin:[3,5,3,5]});
b.addText("Each row is a distinct way zonation could fail, mapped to its signature on depth-normalized counts. The structure-redistribution routes (cells crossing boxes) are all flat — cells keep their identity. The one magnitude route, dimming, is REAL: the pericentral detox program quiets, confirmed by gene-set + within-PC testing.",
  {x:0.7,y:6.45,w:12.0,h:0.7,fontSize:12.5,italic:true,color:MUTE,align:"left"});

// BACKUP — the detailed three-way partition (moved off the in-place conclusion)
{ const bc=p.addSlide(); bc.background={color:DARK};
  bc.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
  bc.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
  bc.addShape(p.shapes.RECTANGLE,{x:0.85,y:0.5,w:0.16,h:0.26,fill:{color:AMBER}});
  bc.addText("BACKUP  ·  FULL CONCLUSIONS",{x:1.08,y:0.46,w:11.5,h:0.4,fontSize:14,bold:true,color:AMBER,charSpacing:3,align:"left"});
  bc.addText("Conclusions · limits · next steps",{x:0.85,y:0.85,w:11.6,h:0.8,fontSize:28,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
  let bx=0.85; for(const col of cols){ const cw=3.85;
    bc.addShape(p.shapes.ROUNDED_RECTANGLE,{x:bx,y:1.8,w:cw,h:4.55,fill:{color:"1E3A3D"},rectRadius:0.08,shadow:sh()});
    bc.addText(col.h,{x:bx,y:1.95,w:cw,h:0.5,fontSize:20,bold:true,color:col.c,fontFace:SERIF,align:"center"});
    bc.addText(col.items.map(t=>({text:t,options:{bullet:true,color:"E2E8F0",breakLine:true,paraSpaceAfter:9}})),
      {x:bx+0.25,y:2.55,w:cw-0.45,h:3.6,fontSize:14.5,align:"left",valign:"top"});
    bx+=cw+0.25; }
}

p.writeFile({fileName:__dirname+"/MASLD_zonation.pptx"}).then(f=>console.log("WROTE",f));
