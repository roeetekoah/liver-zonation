// One-page explainer: competitive vs self-contained gene-set tests, and why a robust claim needs both.
// Backup slide + standalone PDF. Run: node geneset_tests_explainer.js -> geneset_tests_explainer.pptx
const pptxgen=require("pptxgenjs");
const PC="1D4ED8",PP="EA580C",CONFOUND="BE123C",BIOPSY="0D9488",INK="1B2B31",TEAL="1B6E78",
      TEALD="123F47",AMBER="C0561B",GREEN="15803D",MUTE="5C6E73",WHITE="FFFFFF",BG="F7F5F1",
      LINE="DAD4CA",ORANGE="C0561B",SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});
const p=new pptxgen();p.layout="LAYOUT_WIDE";
function head(s,k,h,sec){s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:ORANGE}});
  s.addText(k,{x:0.74,y:0.30,w:9.0,h:0.35,fontSize:13,bold:true,color:ORANGE,charSpacing:3,align:"left",margin:0});
  if(sec)s.addText(sec,{x:9.9,y:0.32,w:2.95,h:0.3,fontSize:11,bold:true,color:TEAL,charSpacing:2,align:"right",margin:0});
  s.addText(h,{x:0.48,y:0.62,w:12.4,h:0.7,fontSize:26,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});}
function foot(s){s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});}
let s=p.addSlide();s.background={color:BG};
head(s,"BACKUP · METHOD","Two gene-set tests — and why a robust claim needs both","QA");
s.addText("Every program is run through two tests that ask different questions. Each, alone, has a blind spot.",
  {x:0.6,y:1.32,w:12.3,h:0.34,fontSize:14,italic:true,color:MUTE,align:"left",margin:0});

// --- two definition cards ---
function card(x,w,col,title,q,desc,good,bad){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y:1.78,w,h:2.0,fill:{color:WHITE},line:{color:col,width:1.4},rectRadius:0.07,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x,y:1.78,w:0.1,h:2.0,fill:{color:col}});
  s.addText(title,{x:x+0.28,y:1.9,w:w-0.45,h:0.3,fontSize:14.5,bold:true,color:col,charSpacing:1,align:"left",margin:0});
  s.addText(q,{x:x+0.28,y:2.24,w:w-0.5,h:0.5,fontSize:14,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(desc,{x:x+0.28,y:2.74,w:w-0.5,h:0.3,fontSize:11.5,italic:true,color:MUTE,align:"left",margin:0});
  s.addText([{text:"✓  ",options:{bold:true,color:GREEN}},{text:good,options:{color:INK}}],{x:x+0.28,y:3.08,w:w-0.5,h:0.34,fontSize:11.5,align:"left",valign:"top",margin:0});
  s.addText([{text:"✗  ",options:{bold:true,color:CONFOUND}},{text:bad,options:{color:INK}}],{x:x+0.28,y:3.42,w:w-0.5,h:0.34,fontSize:11.5,align:"left",valign:"top",margin:0});
}
card(0.6,6.0,BIOPSY,"SELF-CONTAINED   ·   ROAST",
  "Do the program’s own genes actually change — up or down — at all?",
  "tests the set’s fold-changes against “no change” (zero); ignores other genes.",
  "immune to the relative-share effect — what other genes do can’t fake it.",
  "alone: if the whole genome drifts, the set can look like it moves too.");
card(6.85,5.95,PC,"COMPETITIVE   ·   CAMERA · GSEA",
  "Does the program move MORE than the rest of the genome?",
  "compares the set’s shift against the background of all other genes.",
  "shows the change is specific to this program, not everywhere.",
  "alone: a few strong genes can make the whole set look significant, even if most of it doesn’t move.");

// --- 2×2 truth table ---
const hx1=2.0,hx2=7.45,cw=5.3,r1=4.45,r2=5.42,rh=0.9;
s.addText("SELF-CONTAINED  moves ✓",{x:hx1,y:4.12,w:cw,h:0.28,fontSize:11.5,bold:true,color:BIOPSY,align:"center",margin:0});
s.addText("SELF-CONTAINED  flat ✗",{x:hx2,y:4.12,w:cw,h:0.28,fontSize:11.5,bold:true,color:MUTE,align:"center",margin:0});
s.addText("COMPETITIVE ✓",{x:0.55,y:r1,w:1.3,h:rh,fontSize:11,bold:true,color:PC,align:"center",valign:"middle",margin:0});
s.addText("COMPETITIVE ✗",{x:0.55,y:r2,w:1.3,h:rh,fontSize:11,bold:true,color:MUTE,align:"center",valign:"middle",margin:0});
function cell(x,y,fill,border,title,why,tag,tagcol){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:cw,h:rh,fill:{color:fill},line:{color:border,width:1.3},rectRadius:0.05});
  s.addText([{text:title,options:{bold:true,color:border,fontSize:13.5}},{text:tag?("   "+tag):"",options:{bold:true,color:tagcol||border,fontSize:11.5}}],
    {x:x+0.2,y:y+0.1,w:cw-0.35,h:0.3,align:"left",margin:0});
  s.addText(why,{x:x+0.2,y:y+0.42,w:cw-0.35,h:0.42,fontSize:11.5,color:INK,align:"left",valign:"top",margin:0});
}
cell(hx1,r1,"E7F3EC",GREEN,"ROBUST — real & specific","→ pericentral detox","✓ keep",GREEN);
cell(hx2,r1,"FBEEE9",CONFOUND,"Not coherent — not robust","→ PC identity · phase-II",null);
s.addText("a few genes move (or a relative-share effect) — not the whole set",{x:hx2+0.2,y:r1+0.42,w:cw-0.35,h:0.42,fontSize:10.5,italic:true,color:MUTE,align:"left",valign:"top",margin:0});
cell(hx1,r2,"FCF3E6",AMBER,"Genome-wide drift","not specific",null);
s.addText("moves, but no more than everything else",{x:hx1+0.2,y:r2+0.42,w:cw-0.35,h:0.42,fontSize:11,italic:true,color:MUTE,align:"left",valign:"top",margin:0});
cell(hx2,r2,"F1EFEA",MUTE,"No change","",null);

// --- bottom line ---
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:6.5,w:12.25,h:0.62,fill:{color:"E7F0EE"},line:{color:TEAL,width:1.2},rectRadius:0.06});
s.addText([{text:"A robust positive claim needs BOTH ticks:  ",options:{bold:true,color:TEALD}},
  {text:"self-contained says it’s real (its own genes moved off zero); competitive says it’s specific (more than the background). Only pericentral detox passes both — that’s our one confident finding.",options:{color:INK}}],
  {x:0.85,y:6.5,w:11.7,h:0.62,fontSize:13,align:"left",valign:"middle",margin:0});
foot(s);

// ===================================================== SLIDE 2 — stats glossary (plain words)
s=p.addSlide();s.background={color:BG};
head(s,"BACKUP · STATS","The stats terms in your part, in plain words","QA");
const gl=[
 ["ρ  ·  Spearman",BIOPSY,"How strongly two things move together, by rank, from −1 to +1.   ρ = −0.48 → a moderate trend: detox falls as fibrosis rises.   (−1 = perfect opposite · 0 = no link · +1 = perfectly together.)"],
 ["p-value",PC,"The chance of seeing a trend this strong if there were really nothing there — pure noise.   p = 0.003 → about 3 in 1,000 → very unlikely a fluke.   The usual bar is p < 0.05."],
 ["FDR  ·  q-value",AMBER,"A p-value corrected for testing thousands of genes at once.   FDR = 0.05 → about 5% of the called “hits” are expected to be false.   This is why a single gene must clear FDR, not raw p."],
 ["NES  ·  GSEA",CONFOUND,"How strongly a gene set piles up at the down (or up) end of the genome-wide ranking, vs random.   More negative = a stronger coordinated down-shift of the whole set."]];
for(let i=0;i<4;i++){const y=1.62+i*1.28;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y,w:12.2,h:1.12,fill:{color:WHITE},line:{color:LINE,width:1},rectRadius:0.07,shadow:sh()});
  s.addShape(p.shapes.RECTANGLE,{x:0.6,y,w:0.1,h:1.12,fill:{color:gl[i][1]}});
  s.addText(gl[i][0],{x:0.9,y:y+0.16,w:3.2,h:0.8,fontSize:17,bold:true,color:gl[i][1],fontFace:SERIF,align:"left",valign:"top",margin:0});
  s.addText(gl[i][2],{x:4.2,y:y+0.16,w:8.4,h:0.85,fontSize:13.5,color:INK,align:"left",valign:"top",margin:0});
}
foot(s);
p.writeFile({fileName:__dirname+"/geneset_tests_explainer.pptx"}).then(f=>console.log("WROTE",f));
