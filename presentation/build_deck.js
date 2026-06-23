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
p.title="Matched biopsies preserve hepatocyte transcriptional zonation in MASLD";

// --- helpers: kicker + short headline; footer; figure caption; classification chip ---
function head(s,kicker,headline){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:12.0,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.85,fontSize:28,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
let _pg=1;  // slide 1 (title) has no footer; first foot() call is slide 2
function foot(s){ _pg++;
  s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});
  s.addText(String(_pg),{x:12.2,y:7.12,w:0.6,h:0.3,fontSize:10.5,color:MUTE,align:"right",margin:0});
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

// ============================================================ SLIDE 3b — THE LEGACY APPROACH
s=p.addSlide(); s.background={color:BG};
head(s,"THE LEGACY APPROACH","The metric that produced the collapse");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:1.85,w:6.4,h:1.35,fill:{color:LIGHT},rectRadius:0.07});
s.addText("WHAT WE FIRST USED",{x:0.95,y:1.98,w:5.9,h:0.3,fontSize:12,bold:true,color:MUTE,charSpacing:2,align:"left"});
s.addText("A z-scored zonation coordinate, marker–marker correlations, and spread / slope-loss plots — pooled across all samples.",
  {x:0.95,y:2.3,w:5.9,h:0.85,fontSize:15,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.LINE,{x:3.9,y:3.35,w:0,h:0.35,line:{color:MUTE,width:1.6,endArrowType:"triangle"}});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:3.85,w:6.4,h:1.5,fill:{color:"FBEEE9"},line:{color:CONFOUND,width:1},rectRadius:0.07});
s.addText("THE CLAIM IT PRODUCED",{x:0.95,y:3.98,w:5.9,h:0.3,fontSize:12,bold:true,color:CONFOUND,charSpacing:2,align:"left"});
s.addText("“Hepatocytes lose their zonation; the pericentral program turns off, strongest at end-stage.”",
  {x:0.95,y:4.3,w:5.9,h:0.95,fontSize:16,italic:true,bold:true,color:SLATE,align:"left",valign:"top"});
s.addText("THE TRAP",{x:7.6,y:1.95,w:5.0,h:0.3,fontSize:13,bold:true,color:ORANGE,charSpacing:2,align:"left"});
s.addText([
  {text:"Every metric is a relative summary — it hides who moved, how many, and from where.",options:{bullet:true,breakLine:true}},
  {text:"They pool healthy + biopsy + end-stage across a hidden sampling discontinuity.",options:{bullet:true,breakLine:true}},
  {text:"Depth, cell number and tissue source all bend a z-score or correlation.",options:{bullet:true,breakLine:true}},
  {text:"→ so we switched to raw molecule counts (next slide: why the samples differ).",options:{bullet:true,bold:true,color:BIOPSY}}],
  {x:7.85,y:2.45,w:5.0,h:3.0,fontSize:17,color:INK,align:"left",paraSpaceAfter:9});
foot(s);
s.addNotes("Show the legacy approach and the claim it produced, then dismantle it. We first read the data with a z-scored relative ruler and marker correlations — which produced the headline 'hepatocytes lose zonation, pericentral turns off.' But every such metric is a relative summary pooled across all samples; it hides who moved and is bent by depth, cell number and tissue source. That motivated the pivot to raw molecule counts on the matched axis.");

// ============================================================ SLIDE 3c — THE FOUR CLASSES (vocabulary)
s=p.addSlide(); s.background={color:BG};
head(s,"THE VOCABULARY","Every hepatocyte falls in one of four classes");
s.addText("Before asking how zonation could break down, we fix the words. Each hepatocyte either runs the pericentral program, the periportal program, both at once, or neither — four mutually exclusive classes:",
  {x:0.7,y:1.5,w:12.3,h:0.6,fontSize:16,color:INK,align:"left"});
// axis headers — periportal across the top, pericentral down the left
s.addText("PERIPORTAL  PROGRAM   (ASS1, CPS1, PCK1 …)",{x:2.95,y:2.18,w:9.15,h:0.3,fontSize:12.5,bold:true,color:PP,charSpacing:1,align:"center",margin:0});
s.addText("not detected",{x:2.95,y:2.5,w:4.45,h:0.3,fontSize:12.5,bold:true,color:MUTE,align:"center",margin:0});
s.addText("detected",{x:7.65,y:2.5,w:4.45,h:0.3,fontSize:12.5,bold:true,color:MUTE,align:"center",margin:0});
s.addText("PERICENTRAL\nPROGRAM\n(GLUL, CYP …)",{x:0.4,y:2.45,w:2.4,h:0.85,fontSize:12.5,bold:true,color:PC,align:"center",margin:0});
s.addText("detected",{x:0.4,y:3.5,w:2.4,h:0.3,fontSize:12.5,bold:true,color:MUTE,align:"center",margin:0});
s.addText("not detected",{x:0.4,y:5.2,w:2.4,h:0.3,fontSize:12.5,bold:true,color:MUTE,align:"center",margin:0});
// 2x2 grid of definition cards — colours match the mechanism chips on the next slide
classbox(s,2.95,2.9,4.45,1.55,"PC-anchor","Pericentral identity — pericentral genes detected, periportal genes silent.",PC);
classbox(s,7.65,2.9,4.45,1.55,"Dual","Co-expression — both programs detectable in the same nucleus.",DUAL);
classbox(s,2.95,4.6,4.45,1.55,"Null","Double-negative — neither program detectable.",NULL,INK);
classbox(s,7.65,4.6,4.45,1.55,"PP-anchor","Periportal identity — periportal genes detected, pericentral genes silent.",PP);
s.addText([{text:"These four classes are the vocabulary. ",options:{bold:true}},
  {text:"“Losing zonation” means cells ",options:{}},{text:"redistribute",options:{italic:true}},
  {text:" across them — the next slide is the four ways that can happen, in these same colours.",options:{}}],
  {x:0.7,y:6.35,w:12.3,h:0.5,fontSize:13.5,italic:true,color:MUTE,align:"left"});
foot(s);
s.addNotes("Definitions before mechanisms. Every hepatocyte is sorted into exactly one of four classes by which zonation program it runs: PC-anchor (pericentral only), PP-anchor (periportal only), Dual (both — the co-expression state), or Null (neither — double-negative). The 2x2 is pericentral detected/not against periportal detected/not. The card colours are carried onto the next slide, where each failure mode is a change in how cells distribute across these four boxes. 'Detected' here is operationalised on the later method slide as the >=2-UMI, depth-normalized rule.");

// ============================================================ SLIDE 4 — FAILURE MODES
s=p.addSlide(); s.background={color:BG};
head(s,"WHAT WE TEST","Zonation loss is not one mechanism");
s.addText("If the zonation expression signal breaks down, it can do so in distinct ways — each has its own count signature, which we test separately:",
  {x:0.7,y:1.6,w:12.0,h:0.7,fontSize:17,color:INK,align:"left"});
chip(s,1.0,2.6,2.6,1.2,"Depletion\n(an anchor box ↓)",PC);
chip(s,3.85,2.6,2.6,1.2,"Co-expression\n(the dual box ↑)",DUAL);
chip(s,6.7,2.6,2.6,1.2,"Turn-off\n(the null box ↑)",NULL,INK);
chip(s,9.55,2.6,2.85,1.2,"Composition shift\n(PP : PC ratio moves)",PP);
s.addText([{text:"We expected pericentral depletion — but an ",options:{}},
  {text:"emptying anchor box",options:{bold:true,color:PC}},
  {text:" (depletion) and a ",options:{}},
  {text:"filling null box",options:{bold:true,color:"6B7280"}},
  {text:" (turn-off) are different boxes, opposite directions — neither implies the other. We track all four, not just the pericentral depletion we expected.",options:{}}],
  {x:1.0,y:4.25,w:11.9,h:0.7,fontSize:15,color:"334155",align:"left",valign:"top"});
s.addText("Any relative summary — a z-score, a marker correlation, a UMAP axis — is scale-free by construction: it divides out the absolute level, so it reads the gradient’s shape, not how many cells sit where. The four box-counts above collapse into one number; only counting molecules tells them apart.",
  {x:1.0,y:5.35,w:11.9,h:1.3,fontSize:15,italic:true,color:MUTE,align:"left",valign:"top"});
foot(s,4);
s.addNotes("De-zonation is not one event but several, each a different movement among the four boxes from the previous slide. Depletion = an anchor (pole-identity) box shrinks — pericentral OR periportal. Turn-off = the null, double-negative box grows. These are dissociable, which is the question that keeps coming up: a pole can convert to the opposite pole (depletion with the null box untouched), and cells can go double-negative without any single pole shrinking (turn-off with no depletion). Co-expression fills the dual box; composition shift tilts the PP:PC ratio. A single correlation or z-score collapses all four into one number; absolute box counts keep them separate. All four are flat across biopsy F1-F4. Two further routes act on the gradient itself rather than the boxes — gradient compression and dimming — and get their own slide next.");

// ============================================================ SLIDE 4b — THE GRADIENT AXIS (compression + dimming)
// mini line-schematic of a zonation gradient (yf: 0=top/high expression, 1=bottom/low)
function gplot(s,px,py,pw,ph,lines){
  s.addShape(p.shapes.LINE,{x:px,y:py,w:0,h:ph,line:{color:"C2CBCB",width:1}});
  s.addShape(p.shapes.LINE,{x:px,y:py+ph,w:pw,h:0,line:{color:"C2CBCB",width:1}});
  for(const ln of lines){ const x1=px+ln.x1*pw,y1=py+ln.y1*ph,x2=px+ln.x2*pw,y2=py+ln.y2*ph;
    // OOXML extents must be non-negative — use abs() and flipV for rising lines
    const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.abs(x2-x1),h=Math.abs(y2-y1),flipV=((x2-x1)*(y2-y1)<0);
    s.addShape(p.shapes.LINE,{x,y,w,h,flipV:flipV,line:{color:ln.c,width:ln.w||3,dashType:ln.d}}); }
}
s=p.addSlide(); s.background={color:BG};
head(s,"THE GRADIENT AXIS","Beyond the boxes — zonation is a gradient");
s.addText("The four classes are discrete bins. Zonation is really a continuous gradient, which can weaken two further ways the box-counts can’t see — one of shape, one of level:",
  {x:0.7,y:1.55,w:12.3,h:0.6,fontSize:16,color:INK,align:"left"});
// --- card A: COMPRESSION (shape) ---
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:2.25,w:6.0,h:3.55,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
s.addText([{text:"Compression  ",options:{bold:true,fontSize:19,color:TEAL,fontFace:SERIF}},{text:"the gradient flattens",options:{italic:true,fontSize:14,color:MUTE}}],
  {x:0.9,y:2.42,w:5.4,h:0.4,align:"left",margin:0});
gplot(s,0.95,3.0,1.9,1.45,[
  {x1:0,y1:0.95,x2:1,y2:0.08,c:"B7C1C1",w:2,d:"dash"},
  {x1:0,y1:0.58,x2:1,y2:0.44,c:TEAL,w:3.5}]);
s.addText([{text:"— before    ",options:{color:"9AA6A6"}},{text:"— after",options:{color:TEAL,bold:true}}],
  {x:0.95,y:4.5,w:1.95,h:0.25,fontSize:10.5,align:"center",margin:0});
s.addText("Per-cell PC↔PP balance drifts toward the middle — the contrast between poles shrinks.",
  {x:3.05,y:3.0,w:3.35,h:1.4,fontSize:13.5,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.9,y:4.95,w:5.4,h:0.66,fill:{color:"E7F0EE"},rectRadius:0.05});
s.addText([{text:"Mild, non-monotone (peak F3); both poles stay populated → ",options:{color:"14532D"}},{text:"gradient present.",options:{bold:true,color:"14532D"}}],
  {x:1.05,y:4.97,w:5.15,h:0.62,fontSize:12.5,align:"left",valign:"middle"});
// --- card B: DIMMING (amplitude) ---
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.85,y:2.25,w:6.0,h:3.55,fill:{color:"FFFFFF"},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
s.addText([{text:"Dimming  ",options:{bold:true,fontSize:19,color:AMBER,fontFace:SERIF}},{text:"the gradient drops",options:{italic:true,fontSize:14,color:MUTE}}],
  {x:7.15,y:2.42,w:5.4,h:0.4,align:"left",margin:0});
gplot(s,7.2,3.0,1.9,1.45,[
  {x1:0,y1:0.82,x2:1,y2:0.08,c:"B7C1C1",w:2,d:"dash"},
  {x1:0,y1:1.0,x2:1,y2:0.34,c:AMBER,w:3.5}]);
s.addText([{text:"— before    ",options:{color:"9AA6A6"}},{text:"— after",options:{color:AMBER,bold:true}}],
  {x:7.2,y:4.5,w:1.95,h:0.25,fontSize:10.5,align:"center",margin:0});
s.addText("Cells keep their balance, but the program’s overall level falls (same shape, lower).",
  {x:9.3,y:3.0,w:3.35,h:1.4,fontSize:13.5,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.15,y:4.95,w:5.4,h:0.66,fill:{color:"FBEEE2"},rectRadius:0.05});
s.addText([{text:"Nominal ~30% dip (12.7→8.9 UMI/nuc) — borderline; not corroborated genome-wide → ",options:{color:"7C2D12"}},{text:"dropped.",options:{bold:true,color:"7C2D12"}}],
  {x:7.3,y:4.97,w:5.15,h:0.62,fontSize:12,align:"left",valign:"middle"});
s.addText([{text:"On matched biopsies the gradient holds its shape, and the one amplitude hint doesn’t hold up — consistent with the flat box-counts. ",options:{}},
  {text:"Only the explant collapses to a single pole.",options:{italic:true,color:MUTE}}],
  {x:0.7,y:6.05,w:12.3,h:0.6,fontSize:14.5,color:"334155",align:"left",valign:"top"});
foot(s);
s.addNotes("The continuous-gradient axis, which the discrete box-counts cannot capture. Two routes here, and they are distinct facets: compression is a loss of SHAPE — the per-cell PC/(PC+PP) balance drifts toward the middle, contrast between poles shrinks (still a relative measure); dimming is a loss of LEVEL — the program's absolute magnitude falls while the balance is unchanged. Compression: down-thinned, donor-balanced per-cell balance histograms (results/figures/h2/gradient_polarization_dist.png) show a mild, non-monotone middle drift peaking at F3 with both poles staying populated — gradient present, not collapsed; only the explant collapses to the periportal pole. Dimming: a nominal ~30% within-PC detox dip (12.7 to 8.9 down-thinned UMIs/nucleus, F1 to F4). It is borderline to begin with — only about 1.4x the ~26% minimum detectable effect at n=8 vs 4 — and it is NOT corroborated by the genome-wide donor-level pseudobulk DGE of the same genes (CYP2E1 FDR .98, CYP1A2 .91, ADH4 .97, GLUL ~.80, all non-significant). Since those detox genes are expressed mostly in PC cells, a real dimming should have left a donor-level footprint; none appears, so we drop it rather than report it. We do not claim the DGE formally disproves dimming. Net: the gradient is preserved in shape and, where testable, in amplitude — matching the flat anchor counts.");

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

// ============================================================ SLIDE 8b — THE CONFOUNDER AUDIT
s=p.addSlide(); s.background={color:BG};
head(s,"THE CONFOUNDER AUDIT","Every confounder we could test, tested in counts");
s.addText("Two jobs: (a) the structural confounds that make the original trajectory uninterpretable, and (b) the within-biopsy checks that the preserved-zonation null is not itself an artifact.",
  {x:0.7,y:1.55,w:12.2,h:0.55,fontSize:14,italic:true,color:MUTE,align:"left"});
const AUD=[
  [{text:"Confounder",options:{bold:true}},{text:"What we did  (test · numbers)",options:{bold:true}},{text:"Verdict",options:{bold:true}}],
  ["Tissue source","organ-cube / explant ends are not acquisition-matched to needle biopsy","excluded → biopsy-only F1–F4"],
  ["Procurement stress","IEG+HSP across 6 lineages; hep 18× ≈ endothelial 18× (no zonation)","organ-wide handling, not zonation"],
  ["Sequencing batch","run × source Cramér’s V = 0.84; run × F (biopsy) = 0.40","ends confounded; biopsy estimable"],
  ["Lobe (caudate)","marker detection R / C / L within explants","lobe-invariant"],
  ["Sequencing depth","binomial down-thin to B = 1,000 / 1,500 / 3,000 UMIs","PC-share flat at every B (SD 0.006–0.010)"],
  ["Ambient RNA (“soup”)","corr( ALB burden , dual fraction ) across 38 donors = +0.04","does not drive co-expression"],
  ["Cholangiocyte mis-annotation","KRT19⁺ ≤ 0.001, EPCAM⁺ ≤ 0.003 in every anchor class","not contaminating cholangiocytes"],
  ["Ploidy / complexity","nFeatures by stage: 2218 / 3063 / 3169 / 2641 / 1984","non-monotone — does not track stage"],
  ["Depth-match discard","3.5–7.8 % dropped below B, uniformly lower-detection","depth-driven, not PC-biased"],
  ["Clinical covariates","partial corr( detox , F | Age ) = −0.32; Age–F = +0.43","demographics do not explain trends"],
];
s.addTable(AUD,{x:0.7,y:2.2,w:12.2,colW:[2.7,6.6,2.9],fontSize:11,color:INK,
  border:{pt:0.5,color:"D7D0C4"}, fill:{color:"FFFFFF"}, rowH:0.4, valign:"middle", align:"left", margin:[2,5,2,5]});
foot(s);
s.addNotes("Show the full extent of the confounder work. Top four are the structural confounds that make the original full-trajectory comparison uninterpretable (source, stress, batch, lobe). The remaining six are within-biopsy checks that our preserved-zonation null is not an artifact — depth, ambient RNA, cholangiocyte mis-annotation, ploidy, the depth-match discard, and clinical covariates. Every one was tested in counts at the donor level; none manufactures the result. Batch at the single-experiment-label level is perfectly confounded and we flag it as untestable rather than absent.");

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
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
s.addShape(p.shapes.RECTANGLE,{x:0.85,y:0.5,w:0.16,h:0.26,fill:{color:AMBER}});
s.addText("CONCLUSION",{x:1.08,y:0.46,w:11.5,h:0.4,fontSize:14,bold:true,color:AMBER,charSpacing:3,align:"left"});
s.addText("Preservation, not progressive collapse",
  {x:0.85,y:0.85,w:11.6,h:0.8,fontSize:30,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
const cols=[
  {h:"Conclusions",c:"F0B27A",items:["Full healthy→end-stage trajectory is source-confounded.","In biopsy F1–F4, hepatocyte transcriptional zonation is preserved.","Main DGE signal = biliary/ductular burden, most consistent with composition / ambient RNA."]},
  {h:"Limits",c:"FCA5A5",items:["snRNA-seq ≠ lobule geometry / spatial architecture.","Imaging / protein / organoid evidence not re-analyzed.","F4 has only 4 biopsy donors.","Gene-level DGE can miss weak coordinated pathways."]},
  {h:"Next",c:"9CC6CC",items:["CAMERA / ROAST gene-set tests.","Leave-one-F4-donor-out DGE.","Quantitative contamination model.","Spatial / independent biopsy validation."]}
];
const takes=[
  {n:"01",t:"Matched biopsies stay zonated",s:"Across F1–F4 every count route — depletion, co-expression, turn-off, composition — is flat, and the gradient holds its shape."},
  {n:"02",t:"The trajectory was acquisition, not disease",s:"Healthy and end-stage are deceased-donor cubes and explants; the apparent “progression” tracks how the tissue was taken."},
  {n:"03",t:"The biliary signal looks compositional",s:"The lone genome-wide change is a biliary / ductular burden, most consistent with composition / ambient RNA."}];
let ty=1.92; for(const k of takes){
  s.addText(k.n,{x:0.92,y:ty,w:1.15,h:0.7,fontSize:34,bold:true,color:AMBER,fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(k.t,{x:2.2,y:ty+0.02,w:10.5,h:0.45,fontSize:21,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(k.s,{x:2.22,y:ty+0.5,w:10.4,h:0.5,fontSize:14.5,color:"C9D6D3",align:"left",valign:"top",margin:0});
  ty+=1.0; }
s.addShape(p.shapes.LINE,{x:2.22,y:4.98,w:10.3,h:0,line:{color:"2E4A4D",width:1}});
s.addText("The snRNA-seq evidence for progressive de-zonation does not survive matched-source re-analysis — what looked like a disease trajectory was, in large part, an acquisition trajectory.",
  {x:0.92,y:5.18,w:11.9,h:0.9,fontSize:17,bold:true,italic:true,color:WHITE,align:"left",valign:"top"});
s.addText("Scope — snRNA-seq transcriptomes only: imaging, protein and organoid evidence are untouched, and a weak coordinated gene-set program is not excluded.",
  {x:0.92,y:6.5,w:11.9,h:0.5,fontSize:13,color:"8FA3A0",align:"left",valign:"top"});
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

b=back("SCENARIO COVERAGE","Every de-zonation route, mapped to its signature");
const TAX=[
  [{text:"Mechanism",options:{bold:true}},{text:"Signature",options:{bold:true}},{text:"Biopsy F0→F4 (donor-median)",options:{bold:true}},{text:"Verdict",options:{bold:true}}],
  ["Pericentral depletion","PC-anchor fraction ↓","36 / 19 / 23 / 22 / 21 %","flat → no depletion"],
  ["Periportal depletion","PP-anchor fraction ↓","20 / 21 / 22 / 24 / 24 %","flat → no depletion"],
  ["Dimming","within-PC level ↓ (magnitude)","12.7 → 8.9 detox UMI/nuc (F1→F4)","borderline; not corroborated genome-wide → dropped"],
  ["Co-expression","dual (≥2 UMI) fraction ↑","~0.0 / 0.2 / 0.4 / 0.2 / 0.2 %","ambient soup → no"],
  ["Gradient compression","per-cell balance → middle","mild, non-monotone (peak F3)","gradient present"],
  ["Turn-off","null (double-neg) fraction ↑","34 / 44 / 36 / 39 / 39 %","flat → no turn-off"],
  ["Composition shift","PP : PC anchor ratio","0.62 / 1.16 / 1.01 / 1.10 / 1.18","~flat → no shift"],
  ["Induction","program burden ↑","flat in biopsy; rises only end-stage","explant-only"],
];
b.addTable(TAX,{x:0.7,y:1.65,w:12.0,colW:[2.5,2.95,3.95,2.6],fontSize:12.5,color:INK,
  border:{pt:0.5,color:"C9BFAE"}, fill:{color:"FFFFFF"},
  rowH:0.4, valign:"middle", align:"left",
  margin:[3,5,3,5]});
b.addText("Each row is a distinct way zonation could fail, mapped to its signature on depth-normalized counts. Seven are count-based (cells crossing boxes); dimming is the one magnitude axis the counts can’t see. Only the null (all stable) survives biopsy F1–F4 — the lone positive hint, dimming, did not hold up genome-wide.",
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
