// Dimming-revision fixes (v2): the affected slides rebuilt in the deck's style, restructured.
// Flow: gradient axis -> dimming FINDING (clean per-cell fig) -> HOW WE KNOW (four tests, in-flow) -> conclusion.
// Canonical untouched. Run: node dimming_revision.js -> dimming_revision_fixes.pptx
const pptxgen=require("pptxgenjs");
const fs=require("fs");
const A=__dirname+"/assets/";
function pngSize(file){const b=fs.readFileSync(file);return{w:b.readUInt32BE(16),h:b.readUInt32BE(20)};}
const PC="1D4ED8",PP="EA580C",BIOPSY="0D9488",CONFOUND="BE123C",ENDSTAGE="86198F",
      WHITE="FFFFFF",MUTE="5C6E73",LINE="DAD4CA",INK="1B2B31",TEAL="1B6E78",TEALD="123F47",
      AMBER="C0561B",ORANGE="C0561B",BG="F7F5F1",DARK="16242B",SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});
const p=new pptxgen();p.layout="LAYOUT_WIDE";
function head(s,kicker,headline,section){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:8.6,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  if(section)s.addText(section,{x:9.4,y:0.32,w:3.45,h:0.3,fontSize:11,bold:true,color:TEAL,charSpacing:2,align:"right",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.85,fontSize:28,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
function foot(s){s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});}
function fcite(s,txt){s.addShape(p.shapes.LINE,{x:0.5,y:6.78,w:3.2,h:0,line:{color:"C9C0B2",width:0.75}});
  s.addText(txt,{x:0.5,y:6.84,w:12.0,h:0.26,fontSize:10,italic:true,color:"6B6256",align:"left",margin:0});}
function img(s,file,box){const d=pngSize(A+file),ar=d.w/d.h;let w=box.w,h=w/ar;if(box.h&&h>box.h){h=box.h;w=h*ar;}s.addImage({path:A+file,x:box.x+(box.w-w)/2,y:box.y,w,h});}
let s;

// ============================ SLIDE 1 — GRADIENT AXIS (dimming-def -> "detox")
s=p.addSlide();s.background={color:BG};
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

// ============================ SLIDE 2 — THE LANDSCAPE (one picture: only detox is robust)
s=p.addSlide();s.background={color:BG};
head(s,"RESULTS · THE LANDSCAPE","Only one program robustly changes — pericentral detox","RESULTS");
s.addText([{text:"Each dot is one pre-specified program. ",options:{bold:true}},
  {text:"Right = it moves more than the genome (competitive); up/down = it moves on its own (self-contained). Only a dot in a far corner is robust.",options:{}}],
  {x:0.7,y:1.5,w:12.3,h:0.45,fontSize:14.5,color:INK,align:"left"});
img(s,"fig_geneset_landscape.png",{x:0.5,y:2.0,w:8.4,h:4.45});
// right column — reading guide, with the landmark conclusion stated in full
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.25,y:2.08,w:3.6,h:1.45,fill:{color:WHITE},line:{color:BIOPSY,width:1.4},rectRadius:0.07,shadow:sh()});
s.addText([{text:"Pericentral detox (CYP)\n",options:{bold:true,color:BIOPSY,fontSize:13.5,breakLine:true}},
  {text:"falls coherently and hard enough → clears both tests + the per-cell trend (ρ=−0.48). The one robust change.",options:{color:INK,fontSize:11.5}}],
  {x:9.45,y:2.2,w:3.25,h:1.3,align:"left",valign:"top",margin:0});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.25,y:3.6,w:3.6,h:2.15,fill:{color:"FBEEE9"},line:{color:CONFOUND,width:1.7},rectRadius:0.07,shadow:sh()});
s.addText("WHY THE OTHERS AREN’T ROBUST",{x:9.45,y:3.72,w:3.3,h:0.3,fontSize:11,bold:true,color:CONFOUND,charSpacing:1,align:"left",margin:0});
s.addText([{text:"The landmark & phase-II sets only lean down ",options:{}},{text:"faintly",options:{bold:true}},
  {text:" — far too weakly to clear the self-contained test (no single gene moves). ",options:{}},
  {text:"A shift this faint isn’t a real turn-off;",options:{bold:true,color:CONFOUND}},
  {text:" only the CYP detox core moves hard enough to count as a robust change.",options:{}}],
  {x:9.45,y:4.04,w:3.3,h:1.65,fontSize:11.5,color:INK,align:"left",valign:"top",margin:0,lineSpacingMultiple:1.02});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.25,y:5.86,w:3.6,h:0.72,fill:{color:"F2EFE8"},line:{color:MUTE,width:1},rectRadius:0.07});
s.addText([{text:"Controls behaved ↑ ",options:{bold:true,color:MUTE,fontSize:11.5}},
  {text:"— the test reads real biology.",options:{color:MUTE,fontSize:11,italic:true}}],
  {x:9.45,y:5.86,w:3.3,h:0.72,align:"left",valign:"middle",margin:0});
foot(s);

// ============================ SLIDE 3 — THE ZOOM (the one real change, per-cell)
s=p.addSlide();s.background={color:BG};
head(s,"THE ONE REAL CHANGE","Pericentral detox dims — dimming, not de-zonation","RESULTS");
img(s,"fig_within_pc_detox.png",{x:0.4,y:1.7,w:7.8,h:4.2});
// right — three short callouts (no paragraph)
const cues=[["Per-cell, depth-matched","composition can’t fake it — the decisive evidence (ρ=−0.48).",BIOPSY],
  ["Cells keep their class","the pericentral anchor fractions stay flat — no de-zonation; no identity gene is individually lost.",PC],
  ["Coordinated, not a switch","no single gene clears FDR — many genes each shift a little, same direction.",AMBER]];
for(let i=0;i<3;i++){const y=1.85+i*1.18;
  s.addShape(p.shapes.RECTANGLE,{x:8.5,y:y,w:0.1,h:0.95,fill:{color:cues[i][2]}});
  s.addText(cues[i][0],{x:8.74,y:y,w:4.1,h:0.34,fontSize:15,bold:true,color:cues[i][2],fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(cues[i][1],{x:8.74,y:y+0.36,w:4.15,h:0.6,fontSize:12.5,color:INK,align:"left",valign:"top",margin:0});
}
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:8.5,y:5.45,w:4.4,h:0.95,fill:{color:"E7F0EE"},line:{color:TEAL,width:1.2},rectRadius:0.07});
s.addText([{text:"Like a radio: ",options:{bold:true,color:TEALD}},
  {text:"same genre (cells stay pericentral), lower volume (the detox channel dims).",options:{italic:true,color:INK}}],
  {x:8.72,y:5.45,w:4.0,h:0.95,fontSize:12.5,align:"left",valign:"middle",margin:0});
fcite(s,"A relative decline within a fixed budget, not proven absolute molecule loss; a donor-level trend; could partly reflect a shift among PC subzones.");
foot(s);

// ============================ SLIDE 4 — CONCLUSION (softened)
s=p.addSlide();s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
s.addShape(p.shapes.RECTANGLE,{x:0.85,y:0.5,w:0.16,h:0.26,fill:{color:AMBER}});
s.addText("CONCLUSION",{x:1.08,y:0.46,w:11.5,h:0.4,fontSize:14,bold:true,color:AMBER,charSpacing:3,align:"left"});
s.addText("No de-zonation signal — the pericentral detox program dims",
  {x:0.85,y:0.85,w:11.8,h:0.8,fontSize:29,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
const takes=[
  {n:"01",t:"No transcriptional de-zonation signal — cells keep their zonal class (large shift excluded)"},
  {n:"02",t:"The one real change: the pericentral detox program dims (gates held)"},
  {n:"03",t:"Much of the dramatic trajectory may track acquisition, not disease"}];
let ty=2.1;for(const k of takes){
  s.addText(k.n,{x:0.92,y:ty-0.06,w:1.25,h:0.8,fontSize:37,bold:true,color:AMBER,fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(k.t,{x:2.4,y:ty,w:10.2,h:0.85,fontSize:20,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle",margin:0});
  ty+=1.2;}
s.addShape(p.shapes.LINE,{x:2.4,y:5.7,w:9.95,h:0,line:{color:"2E4A4D",width:1}});
s.addText([{text:"We correct one evidence leg",options:{bold:true,color:WHITE}},
  {text:" — the snRNA marker-correlation; the paper’s imaging and protein staining are untouched. The biliary signal is a separate compositional lead.",options:{color:"C9D6D3"}}],
  {x:0.92,y:5.9,w:11.9,h:0.5,fontSize:15,italic:true,align:"left",valign:"top"});
s.addText("Scope — a “PC-like program,” not lobular location; a weak coordinated gene-set program is not excluded; F4 is only 4 donors.",
  {x:0.92,y:6.72,w:11.9,h:0.4,fontSize:12,color:"8FA3A0",align:"left",valign:"top"});
foot(s);

p.writeFile({fileName:__dirname+"/dimming_revision_fixes.pptx"}).then(f=>console.log("WROTE",f));
