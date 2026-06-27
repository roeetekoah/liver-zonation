// Reworked front matter for a non-technical presenter.
// Background, Question, Catch-1 (x2), Catch-2 (x2). Standalone -> early_slides.pptx. Run: node early_slides.js
const pptxgen=require("pptxgenjs");
const fs=require("fs");
const A=__dirname+"/assets/";
function pngSize(f){const b=fs.readFileSync(f);return{w:b.readUInt32BE(16),h:b.readUInt32BE(20)};}
function img(s,file,box){const d=pngSize(A+file),ar=d.w/d.h;let w=box.w,h=w/ar;if(box.h&&h>box.h){h=box.h;w=h*ar;}s.addImage({path:A+file,x:box.x+(box.w-w)/2,y:box.y,w,h});}
const PC="1D4ED8",PP="EA580C",CONFOUND="BE123C",BIOPSY="0D9488",ENDSTAGE="86198F",STRESS="DC2626",
      INK="1B2B31",TEAL="1B6E78",TEALD="123F47",AMBER="C0561B",ORANGE="C0561B",MUTE="5C6E73",
      WHITE="FFFFFF",BG="F7F5F1",SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});
const p=new pptxgen();p.layout="LAYOUT_WIDE";
const bleed=(s)=>s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:13.333,h:7.5,fill:{color:BG},line:{type:"none"}});
function head(s,kicker,headline,section){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(kicker,{x:0.74,y:0.30,w:8.6,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  if(section)s.addText(section,{x:9.4,y:0.32,w:3.45,h:0.3,fontSize:11,bold:true,color:TEAL,charSpacing:2,align:"right",margin:0});
  s.addText(headline,{x:0.48,y:0.64,w:12.4,h:0.85,fontSize:27,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
function footC(s){s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});}
function figcap(s,x,y,w,txt){s.addText(txt,{x,y,w,h:0.4,fontSize:12,italic:true,color:MUTE,align:"center",margin:0});}
function chip(s,x,y,w,h,txt,fill){s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.1,shadow:sh()});
  s.addText(txt,{x,y,w,h,fontSize:15,bold:true,color:WHITE,align:"center",valign:"middle",margin:3});}
let s;

// ============================================================ SLIDE A — BACKGROUND
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"BACKGROUND","The liver is zoned — and a paper says disease un-zones it","BACKGROUND");
s.addShape(p.shapes.RECTANGLE,{x:1.0,y:1.65,w:11.0,h:0.55,fill:{color:PP}});
s.addShape(p.shapes.RECTANGLE,{x:1.0,y:1.65,w:5.5,h:0.55,fill:{color:PC}});
s.addText("PERICENTRAL zone",{x:1.15,y:1.65,w:5.2,h:0.55,fontSize:13,bold:true,color:WHITE,align:"left",valign:"middle"});
s.addText("PERIPORTAL zone",{x:6.7,y:1.65,w:5.15,h:0.55,fontSize:13,bold:true,color:WHITE,align:"right",valign:"middle"});
s.addText("detox / drug metabolism",{x:1.0,y:2.24,w:5.5,h:0.3,fontSize:12.5,bold:true,color:PC,align:"center"});
s.addText("urea cycle",{x:6.5,y:2.24,w:5.5,h:0.3,fontSize:12.5,bold:true,color:PP,align:"center"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:2.95,w:6.0,h:2.55,fill:{color:WHITE},line:{color:TEAL,width:1.4},rectRadius:0.08,shadow:sh()});
s.addText("WHAT WAS KNOWN  ·  zonation atlas",{x:0.95,y:3.12,w:5.5,h:0.3,fontSize:12,bold:true,color:TEAL,charSpacing:1,align:"left"});
s.addText([{text:"A healthy-liver atlas mapped the ",options:{}},{text:"marker genes",options:{bold:true}},
  {text:" that say which zone a cell belongs to. That is our ",options:{}},
  {text:"ruler",options:{bold:true,color:TEAL}},{text:" for “what zonation is.”",options:{}}],
  {x:0.95,y:3.55,w:5.5,h:1.8,fontSize:14.5,color:INK,align:"left",valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.95,y:2.95,w:5.85,h:2.55,fill:{color:WHITE},line:{color:CONFOUND,width:1.4},rectRadius:0.08,shadow:sh()});
s.addText("THE CLAIM  ·  Gribben et al., Nature 2024",{x:7.2,y:3.12,w:5.4,h:0.3,fontSize:12,bold:true,color:CONFOUND,charSpacing:1,align:"left"});
s.addText([{text:"In fatty-liver disease (MASLD), hepatocytes:\n",options:{breakLine:true}},
  {text:"1.  lose their zonation",options:{bold:true,color:INK}},{text:"  (the two groups blur together), and\n",options:{breakLine:true}},
  {text:"2.  turn into bile-duct cells",options:{bold:true,color:INK}},{text:"  (transdifferentiation).",options:{}}],
  {x:7.2,y:3.55,w:5.4,h:1.8,fontSize:14,color:INK,align:"left",valign:"top",paraSpaceAfter:4});
// OUR IDEA — the takeaway, made to pop
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:5.72,w:12.12,h:1.22,fill:{color:"E7F0EE"},line:{color:TEAL,width:1.8},rectRadius:0.09,shadow:sh()});
s.addText("OUR IDEA",{x:0.95,y:5.88,w:11.6,h:0.3,fontSize:13,bold:true,color:TEALD,charSpacing:2,align:"left"});
s.addText("Take the atlas’s healthy-zonation ruler, and measure the “gap” across the MASLD disease stages — does it really shrink?",
  {x:0.95,y:6.22,w:11.6,h:0.65,fontSize:16.5,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top"});
footC(s);

// ============================================================ SLIDE B — THE QUESTION
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"THE QUESTION","Our question","BACKGROUND");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.0,y:2.4,w:11.33,h:2.1,fill:{color:WHITE},line:{color:ORANGE,width:1.6},rectRadius:0.09,shadow:sh()});
s.addText("Does hepatocyte zonation really degrade across MASLD — and is it linked to the hepatocyte→bile-duct transdifferentiation the paper describes?",
  {x:1.4,y:2.55,w:10.55,h:1.8,fontSize:23,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"middle"});
s.addText("We re-checked both claims in the raw data — and ran into two catches: first our ruler, then the experiment itself.",
  {x:1.0,y:5.0,w:11.33,h:0.5,fontSize:15,italic:true,color:MUTE,align:"left"});
footC(s);

// ============================================================ SLIDE C — CATCH 1a — OUR FIRST RULER
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"OUR FIRST RULER","The first ruler — a school-class analogy","THE CATCH");
s.addText([{text:"Imagine a make-believe school",options:{bold:true}},
  {text:" where — by design — every student is clearly one of two kinds: ",options:{}},
  {text:"top",options:{bold:true,color:PC}},{text:" (≥ 90) or ",options:{}},{text:"failing",options:{bold:true,color:PP}},
  {text:" (≤ 30), nobody in between. (A thought experiment — real grades vary, but the two-bin picture makes the idea clear.)",options:{italic:true,color:MUTE}}],
  {x:0.7,y:1.5,w:12.3,h:0.6,fontSize:15.5,color:INK,align:"left"});
img(s,"catch_class.png",{x:1.4,y:2.2,w:10.5,h:3.2});
figcap(s,1.4,5.5,10.5,"In this imagined class, two clear groups (top = pericentral cells, failing = periportal). The first method measures only the GAP between them.");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:1.4,y:6.05,w:10.5,h:0.66,fill:{color:"FBEEE9"},line:{color:CONFOUND,width:1},rectRadius:0.06});
s.addText([{text:"The naive reading:  ",options:{bold:true,color:CONFOUND}},
  {text:"if the gap collapses to zero — everyone looks average — it reads as “zonation lost.”",options:{color:INK}}],
  {x:1.62,y:6.05,w:10.1,h:0.66,fontSize:14.5,align:"left",valign:"middle"});
footC(s);

// ============================================================ SLIDE D — CATCH 1b — WHY THE RULER MISLEADS
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"WHY THE RULER MISLEADS","A zero gap can mean very different things","THE CATCH");
img(s,"catch_scenarios.png",{x:0.35,y:1.5,w:12.6,h:2.95});
figcap(s,0.35,4.5,12.6,"Three classes that all read GAP ≈ 0 — yet only the first is real de-zonation.");
const cards=[
  ["It hides who moved",CONFOUND,"Real de-zonation? A top↔failing swap? Or did the failing students simply leave? The gap reads the same."],
  ["It’s bent by tweaks",CONFOUND,"Give the failing a grade bonus and they “look” top: gap = 0, yet nothing real changed. Any across-the-board shift fools a relative ruler."],
  ["One number, re-graded data",AMBER,"A single relative score crams all of these together — and it’s built on normalized grades tuned for the original question, not ours."]];
for(let i=0;i<3;i++){const x=0.5+i*4.12,y=4.95,w=3.9,h=1.42;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:WHITE},line:{color:"E2DCCF",width:1},rectRadius:0.06,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w:0.1,h,fill:{color:cards[i][1]}});
  s.addText(cards[i][0],{x:x+0.28,y:y+0.12,w:w-0.4,h:0.35,fontSize:14.5,bold:true,color:cards[i][1],align:"left",valign:"top",margin:0});
  s.addText(cards[i][2],{x:x+0.28,y:y+0.5,w:w-0.42,h:0.85,fontSize:11.5,color:INK,align:"left",valign:"top",margin:0});
}
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.5,y:6.5,w:12.42,h:0.5,fill:{color:"E7F0EE"},line:{color:TEAL,width:1},rectRadius:0.06});
s.addText([{text:"→ So we drop the gap and count the raw work each cell does",options:{bold:true,color:TEALD}},
  {text:" — actual molecules, not a relative score — which can tell these apart.",options:{color:INK}}],
  {x:0.7,y:6.5,w:12.0,h:0.5,fontSize:14,align:"left",valign:"middle"});
footC(s);

// ============================================================ SLIDE E1 — CATCH 2a — THE SETUP CAN FAKE IT
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"THE SECOND CATCH","Could the setup itself fake the signal?","THE CATCH");
// timeline (the ruler)
const xs=[1.0,2.7,3.9,5.1,6.3,7.5,9.0],lab=["Healthy","F0","F1","F2","F3","F4","End-stage"];
const colb=[CONFOUND,BIOPSY,BIOPSY,BIOPSY,BIOPSY,BIOPSY,ENDSTAGE],wd=[1.35,1.1,1.1,1.1,1.1,1.1,2.1];
s.addShape(p.shapes.LINE,{x:1.0,y:1.7,w:10.1,h:0,line:{color:MUTE,width:1.5,endArrowType:"triangle"}});
for(let i=0;i<lab.length;i++){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:xs[i],y:1.83,w:wd[i],h:0.55,fill:{color:colb[i]},rectRadius:0.06,shadow:sh()});
  s.addText(lab[i],{x:xs[i],y:1.83,w:wd[i],h:0.55,fontSize:12.5,bold:true,color:WHITE,align:"center",valign:"middle"});}
s.addShape(p.shapes.RECTANGLE,{x:0.93,y:1.77,w:1.49,h:0.95,fill:{type:"none"},line:{color:CONFOUND,width:1.8,dashType:"dash"}});
s.addShape(p.shapes.RECTANGLE,{x:8.92,y:1.77,w:2.26,h:0.95,fill:{type:"none"},line:{color:CONFOUND,width:1.8,dashType:"dash"}});
s.addText("invasive whole-organ surgery",{x:9.0,y:2.72,w:3.8,h:0.28,fontSize:11.5,bold:true,color:CONFOUND,align:"right"});
s.addText("quick needle biopsies",{x:2.7,y:2.72,w:5.5,h:0.28,fontSize:11.5,bold:true,color:BIOPSY,align:"center"});
// the big idea, as a flow of chips
chip(s,0.9,3.45,3.4,0.9,"cut tissue\ninvasively",CONFOUND);
s.addText("→",{x:4.35,y:3.45,w:0.8,h:0.9,fontSize:34,bold:true,color:MUTE,align:"center",valign:"middle"});
chip(s,5.15,3.45,3.4,0.9,"STRESS programs\nswitch ON",STRESS);
s.addText("→",{x:8.6,y:3.45,w:0.8,h:0.9,fontSize:34,bold:true,color:MUTE,align:"center",valign:"middle"});
chip(s,9.4,3.45,3.4,0.9,"expression\nchanges",INK);
// the bold question
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.9,y:4.95,w:11.9,h:1.6,fill:{color:"FBEEE9"},line:{color:CONFOUND,width:1.2},rectRadius:0.08});
s.addText([{text:"So the two ends carry an extra stress signal.\n",options:{bold:true,fontSize:19,color:INK,fontFace:SERIF,breakLine:true}},
  {text:"Is it coming from how they were collected — and could it be faking the “de-zonation”?",options:{bold:true,fontSize:20,color:CONFOUND,fontFace:SERIF}}],
  {x:1.2,y:5.1,w:11.3,h:1.3,align:"left",valign:"middle"});
s.addText("We ran two checks  →",{x:0.9,y:6.65,w:11.9,h:0.35,fontSize:14,italic:true,color:MUTE,align:"right"});
footC(s);

// ============================================================ SLIDE E2 — CATCH 2b — TWO TELLS
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"THE SECOND CATCH","Could the stress be the real signal? Two reasons to doubt it","THE CATCH");
// Tell 1 (left)
s.addText([{text:"① ",options:{bold:true,color:STRESS}},{text:"Can’t be pinned on zonation",options:{bold:true,color:INK}}],
  {x:0.5,y:1.5,w:6.2,h:0.45,fontSize:20,fontFace:SERIF,align:"left",margin:0});
img(s,"catch2_lineages.png",{x:0.4,y:2.05,w:6.2,h:3.1});
s.addText([{text:"Even if the stress ",options:{}},{text:"is",options:{italic:true}},
  {text:" a zonation change, we can’t separate it from handling — cells with ",options:{}},
  {text:"no zonation program at all",options:{bold:true,color:CONFOUND}},
  {text:" (e.g. endothelium) show the same spike. So it’s at least confounded.",options:{}}],
  {x:0.5,y:5.25,w:6.2,h:0.95,fontSize:12.5,color:INK,align:"left",valign:"top"});
// divider
s.addShape(p.shapes.LINE,{x:6.75,y:1.55,w:0,h:4.6,line:{color:"D7D0C4",width:1}});
// Tell 2 (right)
s.addText([{text:"② ",options:{bold:true,color:STRESS}},{text:"Doesn’t behave like disease",options:{bold:true,color:INK}}],
  {x:7.0,y:1.5,w:6.0,h:0.45,fontSize:20,fontFace:SERIF,align:"left",margin:0});
img(s,"catch2_bysource.png",{x:7.0,y:2.05,w:5.9,h:3.1});
s.addText([{text:"If it were the disease, this pattern is odd: ",options:{}},
  {text:"loud in HEALTHY tissue",options:{bold:true,color:CONFOUND}},{text:" and ",options:{}},
  {text:"silent in cirrhosis",options:{bold:true,color:BIOPSY}},
  {text:". A disease signal should rise with severity — so the pattern leans to procurement.",options:{}}],
  {x:7.0,y:5.25,w:5.9,h:0.95,fontSize:12.5,color:INK,align:"left",valign:"top"});
// payoff
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.5,y:6.4,w:12.42,h:0.56,fill:{color:"E7F0EE"},line:{color:TEAL,width:1},rectRadius:0.06});
s.addText([{text:"→ so we look at every group — ",options:{bold:true,color:TEALD}},
  {text:"healthy · F0 · F1–F4 · end-stage",options:{bold:true,color:INK}},
  {text:" — but the two ends are procurement-confounded; disease is read from the matched biopsies (F1–F4).",options:{bold:true,color:TEALD}}],
  {x:0.7,y:6.4,w:12.0,h:0.56,fontSize:12.5,align:"left",valign:"middle"});
footC(s);

// ============================================================ SLIDE G — HOW WE MEASURE
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"HOW WE MEASURE","Our fix: count, control, look finer","METHOD");
s.addText("The two catches told us what to fix. So we changed three things — same data, read more honestly:",
  {x:0.7,y:1.5,w:12.3,h:0.45,fontSize:15.5,color:INK,align:"left"});
const fixes=[
  ["①","Count real molecules",BIOPSY,"We stop measuring the relative gap and count the actual molecules in each cell — so we can see who moved and how many.","fixes: the gap hid who moved"],
  ["②","Control the grading",AMBER,"We pin down the normalization ourselves, so an across-the-board tweak — an artifact — can’t quietly shift the answer.","fixes: the gap was bent by tweaks"],
  ["③","Look finer than two bins",PC,"Not just top vs failing. For every cell: clearly pericentral? periportal? both? neither? — and how loud is its program?","fixes: the coarse top / failing split"]];
for(let i=0;i<3;i++){const x=0.6+i*4.13,y=2.2,w=3.92,h=4.05;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:WHITE},line:{color:"E2DCCF",width:1},rectRadius:0.08,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w,h:0.12,fill:{color:fixes[i][2]}});
  s.addText(fixes[i][0],{x:x+0.22,y:y+0.28,w:1.0,h:0.8,fontSize:40,bold:true,color:fixes[i][2],fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(fixes[i][1],{x:x+0.28,y:y+1.15,w:w-0.5,h:0.8,fontSize:18,bold:true,color:fixes[i][2],fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(fixes[i][3],{x:x+0.28,y:y+2.0,w:w-0.5,h:1.4,fontSize:13.5,color:INK,align:"left",valign:"top",margin:0});
  s.addText(fixes[i][4],{x:x+0.28,y:y+3.55,w:w-0.5,h:0.35,fontSize:11,italic:true,color:MUTE,align:"left",valign:"top",margin:0});
}
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:6.45,w:12.32,h:0.5,fill:{color:"E7F0EE"},line:{color:TEAL,width:1},rectRadius:0.06});
s.addText([{text:"Same data — raw, normalization-controlled, and read at a finer grain. ",options:{bold:true,color:TEALD}},
  {text:"Now the ruler can’t fool us.",options:{color:INK}}],
  {x:0.8,y:6.45,w:12.0,h:0.5,fontSize:14,align:"left",valign:"middle"});
footC(s);

p.writeFile({fileName:__dirname+"/early_slides.pptx"}).then(f=>console.log("WROTE",f));
