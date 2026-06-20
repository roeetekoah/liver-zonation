const pptxgen = require("pptxgenjs");
const p = new pptxgen(); p.layout = "LAYOUT_WIDE";
p.author = "Computational Genomics 76553"; p.title = "Spatial Degradation of Hepatocyte Zonation";
const INK="0E3A40", TEAL="16545C", TEAL2="1B6E78", AMBER="F6C453", CORAL="C05621", CREAM="F4F8F9", ICE="EAF3F4", GREY="5A6472", WHITE="FFFFFF";
const HF="Georgia", BF="Calibri";
const A="/sessions/hopeful-blissful-volta/mnt/Genomics/Hackathon/analysis/";
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.13});
function mix(a,b,t){const ah=parseInt(a,16),bh=parseInt(b,16);
  const ar=ah>>16,ag=(ah>>8)&255,ab=ah&255,br=bh>>16,bg=(bh>>8)&255,bb=bh&255;
  const r=Math.round(ar+(br-ar)*t),g=Math.round(ag+(bg-ag)*t),bl=Math.round(ab+(bb-ab)*t);
  return ((1<<24)+(r<<16)+(g<<8)+bl).toString(16).slice(1).toUpperCase();}
function gradbar(s,x,y,w,h){const n=24;for(let i=0;i<n;i++){const c=mix("F6C453","2C6FB0",i/(n-1));
  s.addShape(p.shapes.RECTANGLE,{x:x+i*(w/n),y,w:w/n+0.02,h,fill:{color:c},line:{type:"none"}});}}
function title(s,t){s.addText(t,{x:0.6,y:0.45,w:12.1,h:0.9,fontFace:HF,fontSize:30,bold:true,color:INK,margin:0});}
function card(s,x,y,w,h,fill){s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:fill},rectRadius:0.08,shadow:sh()});}
let s;

// 1 TITLE
s=p.addSlide(); s.background={color:INK};
s.addText("COMPUTATIONAL GENOMICS 76553  ·  FINAL HACKATHON",{x:0.7,y:0.8,w:12,h:0.4,fontFace:BF,fontSize:13,color:AMBER,charSpacing:3,bold:true,margin:0});
s.addText("Spatial Degradation of\nHepatocyte Zonation",{x:0.7,y:1.7,w:12,h:2.2,fontFace:HF,fontSize:46,bold:true,color:WHITE,lineSpacingMultiple:1.0,margin:0});
s.addText("Using a healthy spatial liver atlas to recover — and watch the collapse of — the lost spatial identity of diseased liver cells",{x:0.72,y:3.95,w:11,h:0.9,fontFace:HF,fontSize:18,italic:true,color:"CFEEF1",margin:0});
gradbar(s,0.72,5.25,7.2,0.28);
s.addText("PORTAL",{x:0.72,y:5.55,w:2,h:0.3,fontFace:BF,fontSize:10,color:"9FE0E6",margin:0});
s.addText("CENTRAL",{x:6.0,y:5.55,w:1.95,h:0.3,fontFace:BF,fontSize:10,color:"9FE0E6",align:"right",margin:0});
s.addText("Combining a healthy spatial atlas (Yakubovsky et al., Nature 2026)\nwith a single-nucleus disease cohort (Gribben et al., Nature 2024)",{x:0.72,y:6.1,w:9,h:0.8,fontFace:BF,fontSize:13,color:"DFF3F5",margin:0});
s.addText("Team: [names]",{x:9.8,y:6.45,w:2.8,h:0.4,fontFace:BF,fontSize:13,color:"9FE0E6",align:"right",margin:0});

// 2 QUESTION
s=p.addSlide(); s.background={color:CREAM}; title(s,"The question, in one breath");
s.addText([
 {text:"A healthy liver is spatially organised: each hepatocyte sits at a position along a blood-flow gradient and does the job that suits its position.\n\n",options:{}},
 {text:"One paper measured that map ",options:{}},{text:"with positions kept",options:{bold:true,color:TEAL2}},{text:" (spatial). Another profiled the whole disease course but with a method that ",options:{}},{text:"throws positions away",options:{bold:true,color:CORAL}},{text:" (single-nucleus).\n\n",options:{}},
 {text:"We use the healthy map to put a position back on each diseased cell, then measure how that organisation falls apart as disease worsens.",options:{bold:true,color:INK}}
],{x:0.6,y:1.6,w:7.2,h:5,fontFace:BF,fontSize:18,color:"24303a",lineSpacingMultiple:1.05,valign:"top",margin:0});
card(s,8.1,1.7,4.6,4.4,WHITE);
s.addText("Healthy lobule",{x:8.35,y:1.95,w:4.1,h:0.4,fontFace:BF,fontSize:13,bold:true,color:TEAL,margin:0});
gradbar(s,8.35,2.5,4.1,0.45);
s.addText("sharp portal-central gradient",{x:8.35,y:3.05,w:4.1,h:0.3,fontFace:BF,fontSize:11,italic:true,color:GREY,margin:0});
s.addText("Diseased lobule",{x:8.35,y:3.7,w:4.1,h:0.4,fontFace:BF,fontSize:13,bold:true,color:CORAL,margin:0});
for(let i=0;i<24;i++){const c=mix("BCA98B","7E96A8",Math.random());s.addShape(p.shapes.RECTANGLE,{x:8.35+i*(4.1/24),y:4.25,w:4.1/24+0.02,h:0.45,fill:{color:c},line:{type:"none"}});}
s.addText("blurred - identity lost",{x:8.35,y:4.8,w:4.1,h:0.3,fontFace:BF,fontSize:11,italic:true,color:GREY,margin:0});
s.addText("We turn that blurring into a number per stage.",{x:8.35,y:5.35,w:4.1,h:0.6,fontFace:BF,fontSize:12,bold:true,color:INK,margin:0});

// 3 BIOLOGY
s=p.addSlide(); s.background={color:CREAM}; title(s,"Liver zonation - and how disease erases it");
s.addText([
 {text:"Zonation. ",options:{bold:true,color:TEAL}},{text:"Hepatocytes specialise by position along the porto-central axis: oxygen-rich ",options:{}},
 {text:"periportal",options:{bold:true,color:"7a5a10"}},{text:" cells run the urea cycle (ASS1, HAL); oxygen-poor ",options:{}},
 {text:"pericentral",options:{bold:true,color:"2c6fb0"}},{text:" cells run detox (CYP2E1) and glutamine synthesis (GLUL).",options:{}}
],{x:0.6,y:1.55,w:6.3,h:2.2,fontFace:BF,fontSize:16,color:"24303a",lineSpacingMultiple:1.05,valign:"top",margin:0});
gradbar(s,0.6,3.7,6.3,0.4);
s.addText("ASS1 · HAL",{x:0.6,y:4.15,w:3,h:0.3,fontFace:BF,fontSize:11,bold:true,color:"6e4406",margin:0});
s.addText("GLUL · CYP2E1",{x:3.9,y:4.15,w:3,h:0.3,fontFace:BF,fontSize:11,color:"2c6fb0",align:"right",margin:0});
card(s,7.3,1.55,5.45,2.3,WHITE);
s.addText([{text:"De-zonation\n",options:{bold:true,fontSize:17,color:TEAL}},{text:"a hepatocyte forgets ",options:{}},{text:"where on the axis",options:{italic:true,bold:true}},{text:" it belongs - it co-expresses opposite-end genes.",options:{}}],{x:7.6,y:1.8,w:4.9,h:1.9,fontFace:BF,fontSize:14,color:"24303a",valign:"top",margin:0});
card(s,7.3,4.05,5.45,2.5,WHITE);
s.addText([{text:"Epithelial plasticity\n",options:{bold:true,fontSize:17,color:CORAL}},{text:"a hepatocyte forgets ",options:{}},{text:"that it is a hepatocyte at all",options:{italic:true,bold:true}},{text:" - drifting toward a bile-duct (cholangiocyte) identity; biphenotypic cells express both ALB and KRT7/KRT19.",options:{}}],{x:7.6,y:4.3,w:4.9,h:2.1,fontFace:BF,fontSize:14,color:"24303a",valign:"top",margin:0});
s.addText("We measure the first quantitatively, and test whether it travels with the second.",{x:0.6,y:5.0,w:6.3,h:1.2,fontFace:BF,fontSize:15,italic:true,bold:true,color:INK,valign:"top",margin:0});

// 4 TWO PAPERS
s=p.addSlide(); s.background={color:CREAM}; title(s,"Two papers, mirror-image gaps");
function paperCard(x,head,col,rows){ card(s,x,1.7,5.85,3.2,WHITE);
  s.addShape(p.shapes.RECTANGLE,{x,y:1.7,w:5.85,h:0.6,fill:{color:col}});
  s.addText(head,{x:x+0.25,y:1.7,w:5.45,h:0.6,fontFace:BF,fontSize:15,bold:true,color:WHITE,valign:"middle",margin:0});
  s.addText(rows.map(r=>({text:r,options:{bullet:true,breakLine:true,paraSpaceAfter:8}})),{x:x+0.3,y:2.5,w:5.3,h:2.25,fontFace:BF,fontSize:13.5,color:"24303a",valign:"top",margin:0});}
paperCard(0.6,"Paper 1 - the cells (Vallier 2024)",CORAL,["47 biopsies, healthy to end-stage","69,426 single-nucleus hepatocytes","Notes zonation loss - only qualitatively","Weakness: snRNA destroyed the spatial map"]);
paperCard(6.9,"Paper 2 - the ruler (Itzkovitz 2026)",TEAL,["Healthy human liver, spatial transcriptomics","Quantitative porto-central zonation map","1,724 zonated genes - our signatures","Weakness: healthy only, no disease stages"]);
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.6,y:5.3,w:12.15,h:1.25,fill:{color:INK},rectRadius:0.08,shadow:sh()});
s.addText([{text:"The gap:  ",options:{bold:true,color:AMBER}},{text:"one has the map but no disease; the other has the disease but no map. Nobody has used the healthy ruler to decode the disease cohort - that is our project.",options:{color:WHITE}}],{x:0.95,y:5.3,w:11.5,h:1.25,fontFace:BF,fontSize:15,valign:"middle",margin:0});

// 5 IDEA
s=p.addSlide(); s.background={color:CREAM}; title(s,"Use the healthy map to decode the diseased cells");
const bx=[{t:"Paper 2 ruler",d:"pericentral & periportal signatures",c:TEAL},{t:"Score each cell",d:"every Paper 1 hepatocyte vs both signatures",c:TEAL2},{t:"Zonation coordinate",d:"pericentral - periportal (per cell)",c:CORAL},{t:"Collapse across stages",d:"how sharp is the axis at each stage?",c:INK}];
bx.forEach((b,i)=>{const x=0.6+i*3.15; card(s,x,2.2,2.85,2.6,WHITE);
  s.addShape(p.shapes.RECTANGLE,{x,y:2.2,w:2.85,h:0.12,fill:{color:b.c}});
  s.addText((i+1)+"",{x:x+0.2,y:2.45,w:0.6,h:0.6,fontFace:HF,fontSize:26,bold:true,color:b.c,margin:0});
  s.addText(b.t,{x:x+0.2,y:3.05,w:2.5,h:0.5,fontFace:BF,fontSize:15,bold:true,color:INK,margin:0});
  s.addText(b.d,{x:x+0.2,y:3.55,w:2.5,h:1.1,fontFace:BF,fontSize:12.5,color:GREY,valign:"top",margin:0});
  if(i<3) s.addText(">",{x:x+2.88,y:3.0,w:0.24,h:0.8,fontFace:HF,fontSize:22,bold:true,color:GREY,align:"center",margin:0});});
s.addText("Honest framing: the reference is a 1-D axis, so we recover a pseudo-zonation coordinate - not a physical (x, y) position.",{x:0.6,y:5.4,w:12.1,h:0.8,fontFace:BF,fontSize:14,italic:true,color:GREY,margin:0});

// 6 HYPOTHESES
s=p.addSlide(); s.background={color:CREAM}; title(s,"Three hypotheses, three tests");
const hy=[{h:"H1 - erosion",c:TEAL,claim:"A de-zonation score rises Healthy to end-stage.",test:"Ordered-trend test (Jonckheere-Terpstra / Spearman on stage rank): does it climb step by step?"},
{h:"H2 - what fails first",c:TEAL2,claim:"Specific programs (e.g. pericentral CYP detox) collapse earliest.",test:"Per-gene differential expression within zones + Benjamini-Hochberg FDR to control false positives."},
{h:"H3 - plasticity link",c:CORAL,claim:"The most de-zonated cells are the ones turning duct-like.",test:"Compare plasticity (KRT7/19) in de-zonated vs zonated cells - Mann-Whitney U."}];
hy.forEach((o,i)=>{const x=0.6+i*4.05; card(s,x,1.7,3.75,4.35,WHITE);
  s.addShape(p.shapes.RECTANGLE,{x,y:1.7,w:3.75,h:0.7,fill:{color:o.c}});
  s.addText(o.h,{x:x+0.25,y:1.7,w:3.3,h:0.7,fontFace:BF,fontSize:16,bold:true,color:WHITE,valign:"middle",margin:0});
  s.addText([{text:"Claim. ",options:{bold:true,color:INK}},{text:o.claim,options:{color:"24303a"}}],{x:x+0.25,y:2.6,w:3.25,h:1.3,fontFace:BF,fontSize:13.5,valign:"top",margin:0});
  s.addText([{text:"Test. ",options:{bold:true,color:o.c}},{text:o.test,options:{color:"24303a"}}],{x:x+0.25,y:3.85,w:3.25,h:2.0,fontFace:BF,fontSize:13.5,valign:"top",margin:0});});

// 7 PIPELINE
s=p.addSlide(); s.background={color:CREAM}; title(s,"The pipeline - course methods, end to end");
const steps=["QC (inherited)","Normalize","Score + classify","Validate (5/5b)","Collapse curve (H1)","Zone DE + FDR (H2)","Plasticity link (H3)"];
steps.forEach((t,i)=>{const x=0.6+i*1.74; s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y:2.3,w:1.6,h:1.5,fill:{color:i<2?ICE:(i<4?"D7ECEF":(i<6?AMBER:"F3D9C7"))},rectRadius:0.06,shadow:sh()});
  s.addText((i+1)+"",{x,y:2.45,w:1.6,h:0.5,fontFace:HF,fontSize:20,bold:true,color:INK,align:"center",margin:0});
  s.addText(t,{x:x+0.1,y:2.95,w:1.4,h:0.8,fontFace:BF,fontSize:11.5,bold:true,color:"24303a",align:"center",valign:"top",margin:0});
  if(i<6)s.addText(">",{x:x+1.6,y:2.55,w:0.18,h:1,fontFace:HF,fontSize:16,bold:true,color:GREY,align:"center",margin:0});});
s.addText([{text:"All in scope: ",options:{bold:true,color:INK}},{text:"single-cell processing & clustering (Lec 15-16), differential expression, ordered-trend testing, and Benjamini-Hochberg FDR (Lec 5); counts & complexity from Ex 1-2.",options:{color:"24303a"}}],{x:0.6,y:4.6,w:12.1,h:1,fontFace:BF,fontSize:15,valign:"top",margin:0});
s.addText("Two-person split: one drives the reference + statistics, the other the disease data + modelling; safe baseline by end of Day 1, rich analysis on Day 2.",{x:0.6,y:5.6,w:12.1,h:1,fontFace:BF,fontSize:14,italic:true,color:GREY,valign:"top",margin:0});

// 8 FEASIBILITY
s=p.addSlide(); s.background={color:CREAM}; title(s,"Feasibility - the engine already starts");
s.addImage({path:A+"feasibility_fig.png",x:0.6,y:1.9,w:7.6,h:3.0,sizing:{type:"contain",w:7.6,h:3.0}});
s.addText("Real Paper 1 hepatocytes: the coordinate's spread narrows monotonically across stages (feasibility run).",{x:0.6,y:5.1,w:7.6,h:0.8,fontFace:BF,fontSize:12,italic:true,color:GREY,valign:"top",margin:0});
function stat(y,big,small,c){card(s,8.5,y,4.25,1.35,WHITE);s.addText(big,{x:8.7,y:y+0.12,w:3.9,h:0.7,fontFace:HF,fontSize:26,bold:true,color:c,margin:0});s.addText(small,{x:8.7,y:y+0.8,w:3.9,h:0.45,fontFace:BF,fontSize:12,color:GREY,margin:0});}
stat(1.9,"69,426","hepatocytes extracted, all 5 stages",TEAL);
stat(3.35,"rho +0.29 / -0.48","Paper 2 control: CYP2E1 / ASS1 track the axis",TEAL2);
stat(4.8,"loads & runs","both datasets public; pipeline validated",CORAL);
s.addText("Sanity-check only - the full analysis is the hackathon.",{x:8.5,y:6.3,w:4.25,h:0.4,fontFace:BF,fontSize:12,italic:true,bold:true,color:INK,margin:0});

// 9 WHY IT MATTERS
s=p.addSlide(); s.background={color:CREAM}; title(s,"Why it matters - not 'we filled a gap'");
const wm=[{t:"A reusable decoder",d:"once validated, it reads zonal identity out of the many existing dissociated disease atlases that have no spatial data."},
{t:"What fails first",d:"which zonal programs lose legibility earliest (H2) predicts the order in which liver functions fail."},
{t:"How identity breaks",d:"when/how the program becomes unreadable (silenced vs identity-mixed), tied to the plasticity linked to disease severity (H3)."}];
wm.forEach((o,i)=>{const y=1.7+i*1.55; s.addShape(p.shapes.OVAL,{x:0.7,y:y+0.05,w:0.85,h:0.85,fill:{color:[TEAL,TEAL2,CORAL][i]},shadow:sh()});
  s.addText((i+1)+"",{x:0.7,y:y+0.05,w:0.85,h:0.85,fontFace:HF,fontSize:26,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  s.addText(o.t,{x:1.8,y:y,w:10.7,h:0.5,fontFace:BF,fontSize:17,bold:true,color:INK,margin:0});
  s.addText(o.d,{x:1.8,y:y+0.5,w:10.7,h:0.9,fontFace:BF,fontSize:14,color:"24303a",valign:"top",margin:0});});
s.addText("Not a reproduction: Paper 1 showed zonation loss by eye (2 markers, 2 extremes); we make it quantitative, continuous, transcriptome-wide and stage-resolved.",{x:0.7,y:6.45,w:12,h:0.7,fontFace:BF,fontSize:13.5,italic:true,color:GREY,margin:0});

// 10 ASK
s=p.addSlide(); s.background={color:INK};
s.addText("The ask",{x:0.8,y:1.6,w:11,h:0.7,fontFace:BF,fontSize:15,bold:true,color:AMBER,charSpacing:3,margin:0});
s.addText("A rough green-light on this direction -\nso we can start prep now, not lose the runway.",{x:0.8,y:2.3,w:11.7,h:1.8,fontFace:HF,fontSize:30,bold:true,color:WHITE,lineSpacingMultiple:1.05,margin:0});
s.addText("Question locked · data downloaded & extracted · pipeline validated on real data · primer written.",{x:0.82,y:4.4,w:11.5,h:0.7,fontFace:BF,fontSize:16,italic:true,color:"CFEEF1",margin:0});
gradbar(s,0.82,5.4,7.2,0.26);
s.addText("Thank you - [team names]",{x:0.82,y:6.2,w:11,h:0.5,fontFace:BF,fontSize:14,color:"9FE0E6",margin:0});

p.writeFile({fileName:"/sessions/hopeful-blissful-volta/mnt/Genomics/Hackathon/Zonation_Hackathon_Deck.pptx"}).then(f=>console.log("WROTE",f)).catch(e=>console.error("ERR",e));
