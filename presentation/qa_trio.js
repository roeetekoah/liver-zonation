// QA trio: 3 backup / deep-dive slides reworked from the old technical intro slides.
// Each carries the DEPTH the simplified front matter drops (for Q&A), not a repeat.
// Standalone -> qa_trio.pptx. Run: node qa_trio.js
const pptxgen=require("pptxgenjs");
const PC="1D4ED8",PP="EA580C",CONFOUND="BE123C",BIOPSY="0D9488",ENDSTAGE="86198F",
      STRESS="DC2626",INK="1B2B31",TEAL="1B6E78",TEALD="123F47",AMBER="C0561B",
      MUTE="5C6E73",WHITE="FFFFFF",BG="F7F5F1",CARD="FFFFFF",LINE="E2DCCF",SERIF="Georgia";
const COURSE="Computational Genomics 76553  ·  HUJI  ·  MASLD snRNA-seq hackathon";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:90,opacity:0.12});
const p=new pptxgen();p.layout="LAYOUT_WIDE";
const bleed=(s)=>s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:13.333,h:7.5,fill:{color:BG},line:{type:"none"}});
function head(s,kicker,headline,section){
  s.addShape(p.shapes.RECTANGLE,{x:0.5,y:0.34,w:0.16,h:0.26,fill:{color:AMBER}});
  s.addText(kicker,{x:0.74,y:0.30,w:9.0,h:0.35,fontSize:13,bold:true,color:AMBER,charSpacing:3,align:"left",margin:0});
  if(section)s.addText(section,{x:9.9,y:0.32,w:2.95,h:0.3,fontSize:11,bold:true,color:TEAL,charSpacing:2,align:"right",margin:0});
  s.addText(headline,{x:0.48,y:0.62,w:12.4,h:0.8,fontSize:26,bold:true,color:INK,fontFace:SERIF,align:"left",valign:"top",margin:0});
}
function footC(s){s.addText(COURSE,{x:0.5,y:7.12,w:10.5,h:0.3,fontSize:10.5,color:MUTE,align:"left",margin:0});}
function card(s,x,y,w,h,accent){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:CARD},line:{color:LINE,width:1},rectRadius:0.06,shadow:sh()});
  if(accent)s.addShape(p.shapes.RECTANGLE,{x,y,w:0.1,h,fill:{color:accent}});
}
function ttl(s,x,y,w,txt,color){s.addText(txt,{x:x+0.28,y:y+0.13,w:w-0.45,h:0.32,fontSize:13,bold:true,color:color||TEAL,charSpacing:1,align:"left",valign:"top",margin:0});}
let s;

// ================================================= SLIDE 1 — QA · THE RELATIVE RULER
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"QA · THE RELATIVE RULER","The first ruler — and why we retired it","BACKUP");

card(s,0.6,1.55,6.0,2.7,TEAL);
ttl(s,0.6,1.55,6.0,"HOW THE FIRST RULER WORKED");
s.addText([{text:"One ",options:{}},{text:"relative coordinate.",options:{bold:true,color:INK}},
  {text:" The pericentral- and periportal-marker programs are each z-scored across all cells; “zonation strength” is read off the spread / anti-correlation of that coordinate — one number per group.",options:{}}],
  {x:0.88,y:2.0,w:5.5,h:1.4,fontSize:13.5,color:INK,align:"left",valign:"top",margin:0,lineSpacingMultiple:1.05});
s.addText([{text:"Markers:  ",options:{bold:true,color:TEAL}},
  {text:"Paper 2’s landmark genes — later the full transcriptome-wide zonated set (1,273 pericentral / 364 periportal genes).",options:{color:INK}}],
  {x:0.88,y:3.5,w:5.5,h:0.7,fontSize:12.5,align:"left",valign:"top",margin:0});

const rr=[["①  Depth-sensitive","z-scoring depends on cell count and sequencing depth. F4 biopsies run shallower — so the spread shrinks for non-biological reasons, even when zonation is unchanged."],
  ["②  Mechanism-blind","depletion, dimming, co-expression, turn-off and noise all shrink the spread the same way. One number cannot tell them apart."]];
for(let i=0;i<2;i++){const y=1.55+i*1.37;card(s,6.85,y,5.87,1.25,CONFOUND);
  s.addText(rr[i][0],{x:7.12,y:y+0.12,w:5.45,h:0.32,fontSize:13.5,bold:true,color:CONFOUND,align:"left",margin:0});
  s.addText(rr[i][1],{x:7.12,y:y+0.5,w:5.45,h:0.68,fontSize:12,color:INK,align:"left",valign:"top",margin:0});
}

s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:4.5,w:12.12,h:1.5,fill:{color:"FBEEE9"},line:{color:CONFOUND,width:1.2},rectRadius:0.07,shadow:sh()});
s.addText("THE TELL",{x:0.85,y:4.66,w:11.6,h:0.3,fontSize:12,bold:true,color:CONFOUND,charSpacing:2,align:"left",margin:0});
s.addText([{text:"Biopsy-only, the relative ruler showed an apparent detox “drift” (a relative score sliding 66 → 49). It ",options:{}},
  {text:"did not survive the count-based classification",options:{bold:true,color:INK}},
  {text:" — the same donors, counted in real molecules, show nothing structural. That single number was reading depth and composition, not biology — so we replaced it with depth-matched molecule counts.",options:{}}],
  {x:0.85,y:4.98,w:11.6,h:0.95,fontSize:14,color:INK,align:"left",valign:"top",margin:0});
footC(s);

// ================================================= SLIDE 2 — QA · PROCUREMENT & STRESS
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"QA · PROCUREMENT & STRESS","The two ends are confounded — the stress is handling","BACKUP");

s.addText("THREE TISSUE SOURCES — only one is a needle biopsy",{x:0.6,y:1.5,w:6.2,h:0.3,fontSize:12.5,bold:true,color:TEAL,charSpacing:1,align:"left",margin:0});
const src=[["Disease spectrum  ·  F0–F4","16-gauge needle core biopsy (right lobe, ~2 cm)","38 donors   (F0 2 · F1 8 · F2 12 · F3 12 · F4 4)",BIOPSY],
  ["Healthy","deceased-donor organ cube (~1 cm³, multi-lobe)","4 donors",CONFOUND],
  ["End-stage","whole-organ explant cubes (multi-lobe)","5 donors",ENDSTAGE]];
for(let i=0;i<3;i++){const y=1.9+i*0.92;card(s,0.6,y,6.05,0.82,src[i][3]);
  s.addText(src[i][0],{x:0.85,y:y+0.09,w:5.7,h:0.28,fontSize:13,bold:true,color:src[i][3],align:"left",margin:0});
  s.addText(src[i][1],{x:0.85,y:y+0.37,w:5.7,h:0.24,fontSize:11,italic:true,color:MUTE,align:"left",margin:0});
  s.addText(src[i][2],{x:0.85,y:y+0.56,w:5.7,h:0.24,fontSize:11.5,bold:true,color:INK,align:"left",margin:0});
}
s.addText([{text:"Both ends are surgical organ cubes — not needle biopsies.",options:{bold:true,color:INK}},
  {text:"  Disease is read only from the matched biopsies (F0–F4).",options:{color:INK}}],
  {x:0.6,y:4.74,w:6.05,h:0.6,fontSize:12,align:"left",valign:"top",margin:0});

s.addText("HANDLING, NOT HYPOXIA",{x:6.95,y:1.5,w:5.8,h:0.3,fontSize:12.5,bold:true,color:TEAL,charSpacing:1,align:"left",margin:0});
s.addText([{text:"The end-stage spike is the acute ",options:{}},{text:"immediate-early",options:{bold:true,color:STRESS}},
  {text:" program (IEG) — not the sustained ",options:{}},{text:"hypoxia",options:{bold:true,color:INK}},
  {text:" program (HIF).   Fold = end-stage ÷ biopsy:",options:{}}],
  {x:6.95,y:1.82,w:5.8,h:0.55,fontSize:12.5,color:INK,align:"left",valign:"top",margin:0});
const rows=[[{text:"Lineage",options:{bold:true,color:WHITE,fill:{color:TEALD}}},{text:"IEG",options:{bold:true,color:WHITE,fill:{color:TEALD},align:"center"}},{text:"HIF",options:{bold:true,color:WHITE,fill:{color:TEALD},align:"center"}}]];
const tdata=[["Hepatocyte","18.5×","1.8×"],["Endothelial  (non-zonated)","18.2×","2.6×"],["Stellate","12.0×","2.6×"],["Cholangiocyte","10.6×","0.8×"],["Macrophage","5.3×","1.9×"],["Lymphocyte","3.2×","1.6×"]];
tdata.forEach((r,i)=>{const bgc=i%2?"F2EFE8":"FFFFFF";rows.push([
  {text:r[0],options:{color:INK,fill:{color:bgc}}},
  {text:r[1],options:{bold:true,color:STRESS,align:"center",fill:{color:bgc}}},
  {text:r[2],options:{color:MUTE,align:"center",fill:{color:bgc}}}]);});
s.addTable(rows,{x:6.95,y:2.42,w:5.8,colW:[3.2,1.3,1.3],rowH:0.3,fontSize:11.5,border:{type:"solid",color:"E2DCCF",pt:0.5},valign:"middle",margin:2});
s.addText([{text:"IEG jumps ~18× — as much in non-zonated endothelium as in hepatocytes. HIF barely moves. ",options:{}},
  {text:"Disease ischemia would lead with HIF; instead acute handling leads",options:{bold:true,color:INK}},
  {text:" → a procurement / dissociation signature, not zonation.",options:{}}],
  {x:6.95,y:4.62,w:5.8,h:0.95,fontSize:11.5,color:INK,align:"left",valign:"top",margin:0});

s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:6.05,w:12.12,h:0.8,fill:{color:"E7F0EE"},line:{color:TEAL,width:1},rectRadius:0.06});
s.addText([{text:"Documented snRNA dissociation / handling artifact:  ",options:{bold:true,color:TEALD}},
  {text:"van den Brink et al. 2017 (Nat. Methods);  O’Flanagan et al. 2019 & Denisenko et al. 2020 (Genome Biol.). The immediate-early / heat-shock signature is the canonical tissue-handling tell.",options:{color:INK}}],
  {x:0.85,y:6.16,w:11.6,h:0.6,fontSize:12,align:"left",valign:"middle",margin:0});
footC(s);

// ================================================= SLIDE 3 — QA · EXACT PIPELINE
s=p.addSlide();s.background={color:BG};bleed(s);
head(s,"QA · EXACT PIPELINE","Raw-count anchor classification — the exact steps","BACKUP");

const steps=["raw UMI counts","down-thin to 1,500","anchor ON if ≥ 2 UMI","classify  PC/PP/dual/null","fraction per donor","median by stage"];
const scol=[INK,BIOPSY,AMBER,PC,TEAL,TEAL];const cw=[1.5,1.7,1.85,2.5,1.7,1.4];
let cx=0.6;const cy=1.55,chh=0.6;
for(let i=0;i<steps.length;i++){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:cx,y:cy,w:cw[i],h:chh,fill:{color:scol[i]},rectRadius:0.05,shadow:sh()});
  s.addText(steps[i],{x:cx,y:cy,w:cw[i],h:chh,fontSize:10.5,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  cx+=cw[i];
  if(i<steps.length-1){s.addText("→",{x:cx-0.01,y:cy,w:0.2,h:chh,fontSize:14,bold:true,color:MUTE,align:"center",valign:"middle",margin:0});cx+=0.2;}
}

card(s,0.6,2.5,6.0,2.0,PC);
ttl(s,0.6,2.5,6.0,"THE ANCHORS",PC);
s.addText([{text:"Pericentral:  ",options:{bold:true,color:PC}},{text:"GLUL, CYP3A4\n",options:{color:INK,breakLine:true}},
  {text:"Periportal:  ",options:{bold:true,color:PP}},{text:"ASS1, PCK1, HAL, ALDOB",options:{color:INK}}],
  {x:0.88,y:2.92,w:5.5,h:0.7,fontSize:13,align:"left",valign:"top",margin:0});
s.addText([{text:"Rule (mutually exclusive):  ",options:{bold:true,color:INK}},
  {text:"PC = ≥1 PC-anchor & <2 PP;  PP = ≥2 PP & <1 PC;  dual = ≥1 PC & ≥2 PP;  null = neither.",options:{color:INK}}],
  {x:0.88,y:3.66,w:5.55,h:0.75,fontSize:11.5,align:"left",valign:"top",margin:0});

card(s,6.85,2.5,5.87,2.0,AMBER);
ttl(s,6.85,2.5,5.87,"WHY THESE CHOICES",AMBER);
s.addText([{text:"Down-thin to a common 1,500 UMIs",options:{bold:true,color:INK}},
  {text:" so depth can’t fake a class shift (held at 1,000 / 1,500 / 3,000; Monte-Carlo SD 0.006–0.010).\n",options:{breakLine:true}},
  {text:"≥ 2 UMI = ambient-robust",options:{bold:true,color:INK}},{text:" (≥ 1 lets ambient RNA call a class).\n",options:{breakLine:true}},
  {text:"Donor is the unit",options:{bold:true,color:INK}},{text:" — nuclei never pseudoreplicated (Squair et al. 2021).",options:{}}],
  {x:7.13,y:2.92,w:5.42,h:1.5,fontSize:12,color:INK,align:"left",valign:"top",margin:0,lineSpacingMultiple:1.05});

s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:4.62,w:12.12,h:1.98,fill:{color:"E7F0EE"},line:{color:TEAL,width:1.2},rectRadius:0.07,shadow:sh()});
s.addText([{text:"9 / 9  raw-data sanity checks pass   ",options:{bold:true,color:TEALD,fontSize:14}},
  {text:"(src/prep/06_sanity_raw.py)",options:{italic:true,color:MUTE,fontSize:11}}],
  {x:0.85,y:4.76,w:11.6,h:0.3,align:"left",margin:0});
const checks=["raw integer UMIs (not SCT)","panel == recorded library","raw range, not the SCT band",
  "differs from the SCT matrix","ALB dominates hepatocytes","panel ≤ library, per cell",
  "69,426 hepatocytes (matches paper)","detection rates plausible","no silent gene drop"];
const gx=[0.85,4.8,8.75],gy=[5.2,5.66,6.12];
checks.forEach((c,idx)=>{const col=idx%3,row=Math.floor(idx/3);
  s.addText([{text:"✓  ",options:{bold:true,color:TEAL}},{text:c,options:{color:INK}}],
    {x:gx[col],y:gy[row],w:3.9,h:0.4,fontSize:11.5,align:"left",valign:"top",margin:0});
});
footC(s);

p.writeFile({fileName:__dirname+"/qa_trio.pptx"}).then(f=>console.log("WROTE",f));
