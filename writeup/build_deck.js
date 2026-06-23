const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
p.author = "Zonation re-analysis";
p.title = "No detectable hepatocyte de-zonation across biopsy-stage MASLD";

const W = 13.33, H = 7.5;
const DARK="16242B", TEAL="1B6E78", TEALD="123F47", AMBER="C0561B", CREAM="F7F5F1",
      INK="1B2B31", MUTE="5C6E73", LINE="DAD4CA", WHITE="FFFFFF", PALE="ECF1F1";
const HF="Georgia", BF="Calibri";
const shadow=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.13});

function label(s, txt, color){ // small section pill
  s.addShape(p.shapes.RECTANGLE,{x:0.7,y:0.55,w:0.18,h:0.34,fill:{color:color||TEAL}});
  s.addText(txt.toUpperCase(),{x:0.98,y:0.55,w:9,h:0.34,fontFace:BF,fontSize:12,bold:true,
    color:color||TEAL,charSpacing:3,valign:"middle",margin:0});
}
function title(s, txt, w){
  s.addText(txt,{x:0.7,y:0.95,w:w||11.9,h:1.0,fontFace:HF,fontSize:30,bold:true,color:INK,margin:0,lineSpacing:34});
}
function content(masterColor){ const s=p.addSlide(); s.background={color:CREAM}; return s; }
let PG=1;
function pageno(s){ PG++; s.addText(String(PG),{x:12.7,y:6.95,w:0.5,h:0.35,fontFace:BF,fontSize:10,color:MUTE,align:"right"});}

// ---------- 1 TITLE ----------
let s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:H,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:H,fill:{color:AMBER}});
s.addText("LIVER GENOMICS  ·  SINGLE-NUCLEUS RE-ANALYSIS",{x:1.0,y:1.3,w:11,h:0.4,fontFace:BF,
  fontSize:13,bold:true,color:"9FC0C4",charSpacing:3,margin:0});
s.addText("No detectable hepatocyte de-zonation\nacross biopsy-stage MASLD",{x:1.0,y:1.9,w:11.4,h:1.9,
  fontFace:HF,fontSize:40,bold:true,color:WHITE,lineSpacing:46,margin:0});
s.addText("The reported collapse is inseparable from tissue-source / procurement confounding.",
  {x:1.0,y:4.0,w:11,h:0.5,fontFace:BF,fontSize:18,italic:true,color:"CFE0E2",margin:0});
s.addText([{text:"Raw-count, donor-level re-analysis of Gribben et al., Nature 2024 (GSE202379)  ·  47 donors  ·  69,426 hepatocyte nuclei"}],
  {x:1.0,y:5.7,w:11,h:0.4,fontFace:BF,fontSize:13,color:"8AA6AA",margin:0});

// ---------- 2 THE QUESTION ----------
s=content(); label(s,"the question"); title(s,"Is liver zonation lost in fatty-liver disease?");
// left: zonation explainer
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:2.1,w:6.0,h:4.4,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText("The healthy lobule is ZONATED",{x:1.0,y:2.35,w:5.4,h:0.4,fontFace:BF,fontSize:15,bold:true,color:INK,margin:0});
// gradient bar
s.addShape(p.shapes.RECTANGLE,{x:1.0,y:2.95,w:5.4,h:0.55,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:1.0,y:2.95,w:2.7,h:0.55,fill:{color:AMBER}});
s.addText("PERIPORTAL (zone 1)",{x:1.05,y:2.95,w:2.6,h:0.55,fontFace:BF,fontSize:10.5,bold:true,color:WHITE,valign:"middle",margin:0});
s.addText("PERICENTRAL (zone 3)",{x:3.8,y:2.95,w:2.55,h:0.55,fontFace:BF,fontSize:10.5,bold:true,color:WHITE,valign:"middle",align:"right",margin:0});
s.addText([
  {text:"Periportal: ",options:{bold:true,color:AMBER}},{text:"ASS1, CPS1, PCK1 — urea cycle, gluconeogenesis",options:{color:INK,breakLine:true}},
  {text:"Pericentral: ",options:{bold:true,color:TEAL}},{text:"GLUL, CYP3A4, drug-metabolizing enzymes (Wnt-driven)",options:{color:INK,breakLine:true}},
  {text:"Two opposing programs along the portal→central axis.",options:{italic:true,color:MUTE}}
],{x:1.0,y:3.8,w:5.4,h:2.4,fontFace:BF,fontSize:14,lineSpacing:22,margin:0});
// right: the claim
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.0,y:2.1,w:5.6,h:4.4,fill:{color:TEALD},rectRadius:0.08,shadow:shadow()});
s.addText("THE PUBLISHED CLAIM",{x:7.35,y:2.4,w:5,h:0.35,fontFace:BF,fontSize:12,bold:true,color:"9FC0C4",charSpacing:2,margin:0});
s.addText("“Hepatocytes lose their zonation”",{x:7.35,y:2.85,w:4.9,h:0.9,fontFace:HF,fontSize:23,bold:true,italic:true,color:WHITE,margin:0,lineSpacing:27});
s.addText("Gribben et al., Nature 2024 — end-stage hepatocytes co-express pericentral + periportal markers.",
  {x:7.35,y:3.9,w:4.9,h:0.9,fontFace:BF,fontSize:13.5,color:"D7E6E8",margin:0,lineSpacing:19});
s.addText([{text:"H1  ",options:{bold:true,color:AMBER}},{text:"Does hepatocyte zonation collapse across disease stage?",options:{color:WHITE}}],
  {x:7.35,y:5.45,w:4.9,h:0.8,fontFace:BF,fontSize:16,bold:true,margin:0,lineSpacing:21});
pageno(s,2);

// ---------- 2b FORMAL QUESTION + ANSWER ----------
s=content(); label(s,"the formal question",AMBER);
title(s,"Our research question — and the answer");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:1.9,w:11.9,h:1.3,fill:{color:TEALD},rectRadius:0.08,shadow:shadow()});
s.addText([{text:"“Using Paper 2’s healthy zonation ruler, can we assign a pseudo-zonation coordinate to every spatially-blind Paper-1 hepatocyte — and measure how, and how much, hepatocyte zonation degrades from healthy to end-stage, and is that linked to the transdifferentiation Paper 1 reported?”",options:{italic:true,color:WHITE}}],
  {x:1.0,y:2.0,w:11.3,h:1.05,fontFace:HF,fontSize:15.5,lineSpacing:21,valign:"middle",margin:0});
s.addText("Answer, clause by clause:",{x:0.7,y:3.5,w:11.5,h:0.55,fontFace:HF,fontSize:19,bold:true,italic:true,color:INK,valign:"middle",margin:0});
const qa=[
  ["Assign a coordinate?","Yes — but it’s the wrong instrument. The fitted ruler + marker-correlation turn depth and tissue differences into a fake collapse. We count molecules instead."],
  ["Measure degradation?","No detectable biopsy-stage change (F1→cirrhotic F4). The “healthy → end-stage” drop is the biopsy-vs-explant tissue axis — not identifiable as disease."],
  ["Linked to transdifferentiation?","Can’t establish. Biliary markers (KRT7/19, EPCAM, SOX4) stay ~0 across biopsy disease and rise only in explants — the same confound."]
];
let qx=0.7, qy=4.25, qw=3.85, qh=2.25, qg=0.28;
qa.forEach((c,i)=>{const x=qx+i*(qw+qg);
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y:qy,w:qw,h:qh,fill:{color:WHITE},rectRadius:0.07,shadow:shadow()});
  s.addShape(p.shapes.RECTANGLE,{x,y:qy,w:qw,h:0.08,fill:{color:AMBER}});
  s.addText(c[0],{x:x+0.25,y:qy+0.22,w:qw-0.5,h:0.5,fontFace:HF,fontSize:15,bold:true,color:INK,margin:0});
  s.addText(c[1],{x:x+0.25,y:qy+0.74,w:qw-0.5,h:qh-0.9,fontFace:BF,fontSize:12.5,color:"45565B",lineSpacing:17,margin:0,valign:"top"});
});
pageno(s);

// ---------- 2c LEGACY APPROACH + DANGEROUS CLAIM ----------
s=content(); label(s,"the legacy approach",AMBER);
title(s,"How we first read the data — and the claim it produced");
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:2.05,w:6.0,h:3.5,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText("The metrics we used at first",{x:0.95,y:2.2,w:5.5,h:0.4,fontFace:HF,fontSize:16,bold:true,color:TEAL,margin:0});
s.addText([
  {text:"z-scored zonation coordinate — ",options:{bold:true,color:INK}},{text:"z(PC) − z(PP) per cell\n",options:{color:MUTE,breakLine:true}},
  {text:"PC–PP marker anti-correlation\n",options:{bold:true,color:INK,breakLine:true}},
  {text:"coordinate spread / IQR per stage\n",options:{bold:true,color:INK,breakLine:true}},
  {text:"zonation heatmaps & slope-loss plots",options:{bold:true,color:INK}}
],{x:0.95,y:2.75,w:5.5,h:2.6,fontFace:BF,fontSize:14.5,lineSpacing:26,margin:0,valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.95,y:2.05,w:5.65,h:3.5,fill:{color:DARK},rectRadius:0.08,shadow:shadow()});
s.addText("The claim it produced",{x:7.2,y:2.2,w:5.2,h:0.4,fontFace:HF,fontSize:16,bold:true,color:"9FC0C4",margin:0});
s.addText("“Hepatocytes lose their zonation;\nthe pericentral program turns off,\nstrongest at end-stage.”",
  {x:7.2,y:2.85,w:5.2,h:1.5,fontFace:HF,fontSize:20,italic:true,color:WHITE,lineSpacing:26,margin:0});
s.addText([{text:"Every metric is a ",options:{color:"CFE0E2"}},{text:"relative summary",options:{bold:true,color:AMBER}},
  {text:" — z-scored, correlation-based, pooled across all samples. It hides who moved, how many, and from where.",options:{color:"CFE0E2"}}],
  {x:7.2,y:4.4,w:5.2,h:1.0,fontFace:BF,fontSize:13.5,lineSpacing:19,margin:0});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:5.75,w:11.9,h:0.95,fill:{color:PALE},rectRadius:0.07});
s.addText([{text:"The trap:  ",options:{bold:true,color:AMBER}},
  {text:"these statistics pool healthy, biopsy and end-stage samples together — across a hidden sampling discontinuity. The next slides show what that discontinuity is, and why it fakes a collapse.",options:{color:INK}}],
  {x:1.0,y:5.9,w:11.3,h:0.65,fontFace:BF,fontSize:14,lineSpacing:19,margin:0,valign:"middle"});
pageno(s);

// ---------- 3 THE CONFOUND TABLE ----------
s=content(); label(s,"the catch",AMBER);
title(s,"Disease stage is confounded with how the tissue was collected");
const rows=[
  [{text:"Disease stage",options:{bold:true,color:WHITE,fill:{color:INK},fontSize:14}},
   {text:"Donors",options:{bold:true,color:WHITE,fill:{color:INK},fontSize:14,align:"center"}},
   {text:"Tissue source",options:{bold:true,color:WHITE,fill:{color:INK},fontSize:14}},
   {text:"Lobes",options:{bold:true,color:WHITE,fill:{color:INK},fontSize:14}}],
  ["Healthy","4","surgical / atlas (mixed)","mixed"],
  ["NAFLD","7","needle biopsy","right"],
  ["NASH (no cirrhosis)","27","needle biopsy","right"],
  ["NASH cirrhosis","4","needle biopsy","right"],
  [{text:"End-stage",options:{bold:true,color:WHITE,fill:{color:AMBER}}},
   {text:"5",options:{bold:true,color:WHITE,fill:{color:AMBER},align:"center"}},
   {text:"transplant EXPLANT",options:{bold:true,color:WHITE,fill:{color:AMBER}}},
   {text:"left + right + caudate",options:{bold:true,color:WHITE,fill:{color:AMBER}}}],
];
s.addTable(rows,{x:0.7,y:2.2,w:8.6,colW:[3.0,1.1,2.7,1.8],rowH:0.55,fontFace:BF,fontSize:14,
  color:INK,valign:"middle",border:{pt:1,color:LINE},fill:{color:WHITE},align:"left"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:9.6,y:2.2,w:3.0,h:3.85,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText([
  {text:"Perfect collinearity.\n",options:{bold:true,color:AMBER,fontSize:16,breakLine:true}},
  {text:"Every end-stage sample is a transplant ",options:{color:INK}},
  {text:"explant",options:{bold:true,color:INK}},
  {text:"; every milder disease sample is a ",options:{color:INK}},
  {text:"needle biopsy",options:{bold:true,color:INK}},
  {text:".\n\nSo disease and acquisition cannot be separated.",options:{color:INK}}
],{x:9.85,y:2.45,w:2.55,h:3.4,fontFace:BF,fontSize:14,lineSpacing:20,valign:"top",margin:0});
s.addText("Verified directly from the paper's Methods + the dataset metadata.",
  {x:0.7,y:6.35,w:9,h:0.4,fontFace:BF,fontSize:12,italic:true,color:MUTE,margin:0});
pageno(s,3);

// ---------- 4 TISSUE-WIDE STRESS ----------
s=content(); label(s,"why it matters",AMBER);
title(s,"The end-stage “collapse” rides on organ-wide procurement stress");
s.addChart(p.charts.BAR,[
  {name:"biopsy",  labels:["Hepatocyte","Endothelial","Stellate","Macrophage","Cholangiocyte","Lymphocyte"], values:[0.4,0.3,0.4,0.6,0.6,0.9]},
  {name:"explant", labels:["Hepatocyte","Endothelial","Stellate","Macrophage","Cholangiocyte","Lymphocyte"], values:[7.4,6.3,5.2,5.8,5.2,4.1]}],
  {x:0.7,y:2.15,w:7.6,h:4.4,barDir:"col",barGrouping:"clustered",chartColors:[TEAL,AMBER],
   chartArea:{fill:{color:CREAM}},showValue:true,dataLabelPosition:"outEnd",dataLabelColor:INK,
   dataLabelFontFace:BF,dataLabelFontSize:9.5,dataLabelFormatCode:"0.0",
   catAxisLabelColor:MUTE,catAxisLabelFontFace:BF,catAxisLabelFontSize:10.5,
   valAxisLabelColor:MUTE,valAxisLabelFontSize:9,valGridLine:{color:"E2E8F0",size:0.5},catGridLine:{style:"none"},
   showLegend:true,legendPos:"t",legendColor:MUTE,legendFontFace:BF,legendFontSize:11,valAxisMaxVal:8});
s.addText("raw stress UMIs per 10⁴ by lineage (donor-median); explant/biopsy ≈ 5–21× across lineages",
  {x:0.7,y:6.45,w:7.6,h:0.4,fontFace:BF,fontSize:12,italic:true,color:MUTE,align:"center",margin:0});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:8.7,y:2.15,w:3.9,h:4.4,fill:{color:TEALD},rectRadius:0.08,shadow:shadow()});
s.addText([
  {text:"Endothelial cells",options:{bold:true,color:AMBER,fontSize:17,breakLine:true}},
  {text:"— irrelevant to hepatocyte zonation — are as stressed as hepatocytes.\n\n",options:{color:WHITE,breakLine:true}},
  {text:"⇒ organ-level ischemia / handling, not a hepatocyte disease program.\n\n",options:{color:"D7E6E8"}},
  {text:"End-stage excluded as a disease endpoint.",options:{bold:true,color:WHITE}}
],{x:8.95,y:2.45,w:3.4,h:3.8,fontFace:BF,fontSize:14.5,lineSpacing:21,margin:0,valign:"top"});
pageno(s,4);

// ---------- 4b SIMPSON'S PARADOX ----------
s=content(); label(s,"the paradox",AMBER);
title(s,"Simpson's paradox: the collapse is between groups, not within them");
s.addImage({path:"../results/figures/h2/simpson_anticorr.png",x:0.7,y:1.95,w:7.7,h:3.92});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:8.6,y:1.95,w:4.0,h:2.55,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText("The collapse dissolves",{x:8.8,y:2.08,w:3.6,h:0.35,fontFace:HF,fontSize:15,bold:true,color:TEAL,margin:0});
s.addText([
  {text:"pooled (legacy):  ",options:{color:INK}},{text:"+0.44, p=.002\n",options:{bold:true,color:AMBER,breakLine:true}},
  {text:"biopsy F0–F4 only:  ",options:{color:INK}},{text:"+0.29, p=.078 n.s.\n",options:{bold:true,color:INK,breakLine:true}},
  {text:"depth-matched counts:  ",options:{color:INK}},{text:"flat",options:{bold:true,color:TEAL}}
],{x:8.8,y:2.5,w:3.6,h:1.9,fontFace:BF,fontSize:13.5,lineSpacing:22,margin:0,valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:8.6,y:4.65,w:4.0,h:1.2,fill:{color:PALE},rectRadius:0.07});
s.addText([{text:"Lurking variable: ",options:{bold:true,color:AMBER}},
  {text:"procurement stress, maximal in end-stage organ cubes — collinear with disease stage.",options:{color:INK}}],
  {x:8.8,y:4.75,w:3.6,h:1.0,fontFace:BF,fontSize:12.5,lineSpacing:17,margin:0,valign:"middle"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:6.05,w:11.9,h:0.85,fill:{color:DARK},rectRadius:0.07});
s.addText([{text:"Textbook reversal:  ",options:{bold:true,color:AMBER}},
  {text:"each healthy donor is individually zonated (anti-corr −0.21), yet pooling the four flips the sign to +0.01 — “de-zonation” manufactured purely by aggregation.",options:{color:"CFE0E2"}}],
  {x:1.0,y:6.18,w:11.3,h:0.6,fontFace:BF,fontSize:13.5,lineSpacing:18,margin:0,valign:"middle"});
pageno(s);

// ---------- 5 METHOD DISCIPLINE ----------
s=content(); label(s,"how we measured");
title(s,"We changed the measurement, not just the plot");
const cards=[
  ["Raw UMI counts","The shipped matrix is an SCT model output (depth squeezed to ~5k). We extracted real molecule counts from the RNA assay."],
  ["Depth-matched","Downsample every nucleus to a common budget so detection differences reflect biology, not sequencing depth. Averaged over draws."],
  ["Donor is the unit","Inference at the donor level (~47), never the cell — no pseudoreplication of tens of thousands of nuclei."],
  ["Counts, not summaries","Cell counts, fractions, molecule burdens — never marker correlations / spreads / z-scores that hide who moved."]
];
let cx=0.7, cy=2.25, cw=6.0, ch=1.95, gx=0.35, gy=0.3;
cards.forEach((c,i)=>{const col=i%2,row=Math.floor(i/2);
  const x=cx+col*(cw+gx), y=cy+row*(ch+gy);
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:cw,h:ch,fill:{color:WHITE},rectRadius:0.07,shadow:shadow()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w:0.12,h:ch,fill:{color:i%2?AMBER:TEAL}});
  s.addText(c[0],{x:x+0.35,y:y+0.22,w:cw-0.6,h:0.5,fontFace:HF,fontSize:18,bold:true,color:INK,margin:0});
  s.addText(c[1],{x:x+0.35,y:y+0.78,w:cw-0.6,h:ch-0.95,fontFace:BF,fontSize:13.5,color:"45565B",lineSpacing:19,margin:0,valign:"top"});
});
pageno(s,5);

// ---------- 6 SCENARIO MAP ----------
s=content(); label(s,"the test");
title(s,"Six snRNA marker-count signatures expected under zonation collapse");
const sc=[
  [{text:"Mechanism",options:{bold:true,color:WHITE,fill:{color:INK}}},{text:"Count signature",options:{bold:true,color:WHITE,fill:{color:INK}}},{text:"Biopsy F0–F4 & NAS",options:{bold:true,color:WHITE,fill:{color:INK},align:"center"}}],
  ["Pericentral-cell depletion","PC-anchor nuclei fall","no change"],
  ["Within-cell program dimming","detox in PC nuclei falls","no change"],
  ["De-zonation: co-expression","dual PC⁺ PP⁺ nuclei rise","no change"],
  ["De-zonation: gradient compression","per-nucleus balance → middle","no change"],
  ["Identity turn-off","double-negative nuclei rise","no change"],
  ["Compositional shift","PP : PC anchor ratio shifts","no change"],
];
const scStyled=sc.map((r,ri)=>r.map((c,ci)=>{
  if(ri===0) return c;
  const base={fontFace:BF,fontSize:13.5,color:INK,valign:"middle"};
  if(ci===2){const ok=c!=="mild (caveat)"; return {text:c,options:{...base,bold:true,align:"center",color:ok?TEAL:AMBER}};}
  return {text:c,options:base};
}));
s.addTable(scStyled,{x:0.7,y:2.2,w:11.9,colW:[3.9,4.6,3.4],rowH:0.6,border:{pt:1,color:LINE},
  fill:{color:WHITE},valign:"middle",fontFace:BF,fontSize:13.5});
pageno(s,6);

// ---------- 7 CENSUS FLAT ----------
s=content(); label(s,"result");
title(s,"None detected — within biopsy-stage power (F1→cirrhotic F4)");
s.addChart(p.charts.BAR,[{name:"PC-anchor fraction",labels:["F1","F2","F3","F4"],values:[0.18,0.24,0.20,0.23]}],
  {x:0.7,y:2.2,w:6.7,h:4.2,barDir:"col",chartColors:[TEAL],chartArea:{fill:{color:CREAM}},
   showValue:true,dataLabelPosition:"outEnd",dataLabelColor:INK,dataLabelFontFace:BF,dataLabelFontSize:13,dataLabelFontBold:true,
   dataLabelFormatCode:"0.00",catAxisLabelColor:MUTE,catAxisLabelFontFace:BF,catAxisLabelFontSize:13,valAxisHidden:true,
   valGridLine:{style:"none"},catGridLine:{style:"none"},showLegend:false,valAxisMaxVal:0.34});
s.addText("Pericentral-anchor fraction of hepatocyte nuclei vs fibrosis stage (flat, non-monotone)",
  {x:0.7,y:6.4,w:6.7,h:0.4,fontFace:BF,fontSize:12,italic:true,color:MUTE,align:"center",margin:0});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:7.8,y:2.2,w:4.8,h:4.2,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText("Robust to everything that could fake a null:",{x:8.05,y:2.45,w:4.3,h:0.5,fontFace:BF,fontSize:15,bold:true,color:INK,margin:0});
s.addText([
  {text:"depth budget 1,000 / 1,500 / 3,000 UMIs",options:{bullet:true,breakLine:true}},
  {text:"anchor = GLUL-only / CYP3A4-only / both",options:{bullet:true,breakLine:true}},
  {text:"8 thinning draws (noise SD 0.006–0.010)",options:{bullet:true,breakLine:true}},
  {text:"every UMI threshold",options:{bullet:true,breakLine:true}},
  {text:"real co-expression (≥2 UMI): ~0 in biopsy vs 7× in explants",options:{bullet:true,breakLine:true}},
  {text:"ambient, contamination, ploidy: tested in counts — none drives it",options:{bullet:true}}
],{x:8.05,y:3.05,w:4.3,h:3.25,fontFace:BF,fontSize:13,color:"45565B",lineSpacing:19,paraSpaceAfter:5,margin:0});
pageno(s,7);

// ---------- 8 POLARIZATION FIGURE ----------
s=content(); label(s,"the picture");
title(s,"The gradient stays broad through cirrhosis — collapses only in explants");
s.addImage({path:"../results/figures/h2/gapfill_polarization.png",x:0.7,y:2.35,w:9.4,h:4.25,sizing:{type:"contain",w:9.4,h:4.25}});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:10.4,y:2.75,w:2.3,h:3.35,fill:{color:TEALD},rectRadius:0.08,shadow:shadow()});
s.addText([
  {text:"Each panel = per-nucleus zonal balance, PC ↔ PP.\n\n",options:{color:"D7E6E8",breakLine:true}},
  {text:"F0–F4: broad, spread — zonation intact.\n\n",options:{color:WHITE,bold:true,breakLine:true}},
  {text:"Explant: abnormal only here, and heterogeneous across donors (one even retains PC).",options:{color:AMBER,bold:true}}
],{x:10.62,y:2.75,w:1.9,h:3.35,fontFace:BF,fontSize:13,lineSpacing:18,margin:0,valign:"middle"});
pageno(s,8);

// ---------- 9 BOUNDED ANSWER (dark) ----------
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:H,fill:{color:TEAL}});
s.addText("A BOUNDED ANSWER — HONEST ABOUT POWER",{x:0.9,y:0.7,w:11,h:0.4,fontFace:BF,fontSize:14,bold:true,color:"9FC0C4",charSpacing:2,margin:0});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.9,y:1.55,w:5.7,h:4.9,fill:{color:"1E3A40"},rectRadius:0.08});
s.addText("WHAT WE CAN SAY",{x:1.2,y:1.85,w:5,h:0.4,fontFace:BF,fontSize:14,bold:true,color:TEAL,charSpacing:2,margin:0});
s.addText([
  {text:"No detectable hepatocyte de-zonation across acquisition-matched biopsy MASLD (F0–F4 + NAS), by any mechanism.",options:{color:WHITE,breakLine:true}},
  {text:"\n",options:{breakLine:true}},
  {text:"A broad PC↔PP gradient is present at every stage, including cirrhotic F4.",options:{color:WHITE,breakLine:true}},
  {text:"\n",options:{breakLine:true}},
  {text:"Near-total collapse is excluded.",options:{color:WHITE,bold:true}}
],{x:1.2,y:2.35,w:5.2,h:3.9,fontFace:BF,fontSize:16,lineSpacing:23,margin:0,valign:"top"});
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.9,y:1.55,w:5.5,h:4.9,fill:{color:"3A2A20"},rectRadius:0.08});
s.addText("WHAT WE DO NOT CLAIM",{x:7.2,y:1.85,w:5,h:0.4,fontFace:BF,fontSize:14,bold:true,color:AMBER,charSpacing:2,margin:0});
s.addText([
  {text:"Not “zonation preserved” — the design is underpowered (smallest detectable change ≈ 85% of the mean; F0, F4 each ~one donor).",options:{color:WHITE,breakLine:true}},
  {text:"\n",options:{breakLine:true}},
  {text:"Single-nucleus counts cannot see lobular spatial position — “PC-like program,” not location.",options:{color:WHITE,breakLine:true}},
  {text:"\n",options:{breakLine:true}},
  {text:"Single cohort; no protein / spatial validation.",options:{color:WHITE}}
],{x:7.2,y:2.35,w:5.0,h:3.9,fontFace:BF,fontSize:15.5,lineSpacing:22,margin:0,valign:"top"});
pageno(s,9);

// ---------- 10 BOUNDED CORRECTION ----------
s=content(); label(s,"the correction");
title(s,"We correct one evidence leg — not the whole claim");
const legs=[
  [TEAL,"snRNA marker-correlation","CORRECTED","A relative statistic, on procurement-confounded explant tissue. No progressive drift toward co-expression in biopsy (dual ≥2 UMI: 0.003 → 0.0, F1→F4)."],
  [MUTE,"Immunofluorescence (GLUL+ASS1)","NOT ADDRESSED","Protein co-localization — different molecule and timescale than the acute RNA stress we measure."],
  [MUTE,"FLASH 3D whole-organ imaging","NOT ADDRESSED","Architecture of end-stage explants; cirrhosis genuinely remodels the lobule. We cannot call it artifact."]
];
let ly=2.2;
legs.forEach((L)=>{
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:ly,w:11.9,h:1.32,fill:{color:WHITE},rectRadius:0.06,shadow:shadow()});
  s.addShape(p.shapes.RECTANGLE,{x:0.7,y:ly,w:0.14,h:1.32,fill:{color:L[0]}});
  s.addText(L[1],{x:1.05,y:ly+0.15,w:4.3,h:1.0,fontFace:HF,fontSize:17,bold:true,color:INK,valign:"middle",margin:0});
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:5.35,y:ly+0.42,w:1.85,h:0.48,fill:{color:L[2]==="CORRECTED"?TEAL:PALE},rectRadius:0.24});
  s.addText(L[2],{x:5.35,y:ly+0.42,w:1.85,h:0.48,fontFace:BF,fontSize:11.5,bold:true,
    color:L[2]==="CORRECTED"?WHITE:MUTE,align:"center",valign:"middle",charSpacing:1,margin:0});
  s.addText(L[3],{x:7.4,y:ly+0.13,w:5.0,h:1.06,fontFace:BF,fontSize:12.5,color:"45565B",lineSpacing:16,valign:"middle",margin:0});
  ly+=1.5;
});
pageno(s,10);

// ---------- 11 GENOME-WIDE CHECK ----------
s=content(); label(s,"the genome-wide check");
title(s,"Genome-wide, the biopsy hepatocyte transcriptome is broadly stable");
s.addText([
  {text:"Transcriptome-wide donor-level DE",options:{bold:true,color:INK}},
  {text:" — pseudobulk, 38 biopsy donors, 17,572 genes, Spearman vs fibrosis, BH-FDR — tested with no curated panel:",options:{color:INK}}
],{x:0.7,y:2.05,w:11.7,h:0.7,fontFace:BF,fontSize:16,lineSpacing:22,margin:0});
// card 1: zonation/detox flat
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:2.9,w:5.75,h:2.0,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText([{text:"Zonation & detox genes: all flat\n",options:{bold:true,color:TEAL,breakLine:true}},
  {text:"CYP2E1 FDR .98 · CYP1A2 .91 · ADH4 .97 · SLCO1B3 .80 · GLUL .85 · all periportal > .79.  The null holds far beyond the panel.",options:{color:"45565B"}}],
  {x:0.95,y:3.1,w:5.3,h:1.65,fontFace:BF,fontSize:14,lineSpacing:20,margin:0,valign:"middle"});
// card 2: 23 trend, mostly ambient, A2M intrinsic
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:6.65,y:2.9,w:5.95,h:2.0,fill:{color:WHITE},rectRadius:0.08,shadow:shadow()});
s.addText([{text:"23 genes do trend — but not zonation\n",options:{bold:true,color:INK,breakLine:true}},
  {text:"15/23 are stromal/immune ambient (stellate, cholangiocyte, endothelial). The one clear hepatocyte-intrinsic signal: ",options:{color:"45565B"}},
  {text:"A2M acute-phase, CPM 219→718.",options:{bold:true,color:INK}}],
  {x:6.9,y:3.1,w:5.5,h:1.65,fontFace:BF,fontSize:14,lineSpacing:20,margin:0,valign:"middle"});
// bottom: retired detox claim
s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:0.7,y:5.15,w:11.9,h:1.5,fill:{color:PALE},rectRadius:0.07});
s.addText([
  {text:"Correction: ",options:{bold:true,color:AMBER}},
  {text:"the earlier within-pericentral xenobiotic dip (12.7→8.9 molecules/nucleus) ",options:{color:INK}},
  {text:"does not survive this genome-wide test",options:{bold:true,color:INK}},
  {text:", so it is no longer reported as a finding. Net: a stable hepatocyte transcriptome with a modest acute-phase response — not de-zonation.",options:{color:INK}}
],{x:1.0,y:5.35,w:11.3,h:1.1,fontFace:BF,fontSize:14,lineSpacing:20,margin:0,valign:"middle"});
pageno(s,11);

// ---------- 12 LIMITATIONS ----------
s=content(); label(s,"limitations");
title(s,"What this dataset cannot settle");
const lim=[
  ["Power","A bounded null: near-total loss excluded, moderate graded change not."],
  ["End-stage disease","Unrecoverable here — no end-stage biopsies, no non-end-stage explants exist."],
  ["No spatial ground truth","snRNA gives a PC-like program, not lobule position; focal / architectural de-zonation is invisible."],
  ["Markers","GLUL is dropout-prone; CYP3A4 covaries with detox — so no independent “identity preserved” claim."],
  ["No clinical covariates","No etiology / alcohol / medication / fasting — fatal for any disease-specific gene claim."],
  ["Single cohort","No independent biopsy series or protein validation."]
];
let lx=0.7, lyy=2.25, lw=6.0, lh=1.25, lgx=0.35, lgy=0.22;
lim.forEach((c,i)=>{const col=i%2,row=Math.floor(i/2);
  const x=lx+col*(lw+lgx), y=lyy+row*(lh+lgy);
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:lw,h:lh,fill:{color:WHITE},rectRadius:0.06,shadow:shadow()});
  s.addText(c[0],{x:x+0.3,y:y+0.16,w:lw-0.6,h:0.4,fontFace:BF,fontSize:14.5,bold:true,color:TEAL,margin:0});
  s.addText(c[1],{x:x+0.3,y:y+0.58,w:lw-0.55,h:lh-0.66,fontFace:BF,fontSize:12.5,color:"45565B",lineSpacing:16,margin:0,valign:"top"});
});
pageno(s,12);

// ---------- 13 CONCLUSION (dark) ----------
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:H,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:H,fill:{color:AMBER}});
s.addText("CONCLUSION",{x:1.0,y:0.8,w:11,h:0.4,fontFace:BF,fontSize:14,bold:true,color:"9FC0C4",charSpacing:3,margin:0});
s.addText([
  {text:"Across acquisition-matched biopsy MASLD, raw-count donor-level snRNA shows ",options:{color:WHITE}},
  {text:"no detectable marker-count de-zonation",options:{bold:true,color:TEAL}},
  {text:" — excluding near-total collapse, but underpowered for moderate/focal change. The end-stage signal is confined to heterogeneous explants and is ",options:{color:WHITE}},
  {text:"inseparable from organ-wide procurement stress",options:{bold:true,color:AMBER}},
  {text:" — not identifiable as progressive disease.",options:{color:WHITE}}
],{x:1.0,y:1.4,w:11.4,h:2.4,fontFace:HF,fontSize:23,lineSpacing:32,margin:0});
s.addShape(p.shapes.LINE,{x:1.0,y:3.95,w:11.3,h:0,line:{color:"35515A",width:1.5}});
s.addText("The transferable lesson",{x:1.0,y:4.2,w:11,h:0.4,fontFace:BF,fontSize:14,bold:true,color:AMBER,charSpacing:2,margin:0});
s.addText("Relative summary statistics — marker correlations, spreads, z-scores — on cohorts where disease stage tracks tissue acquisition can manufacture biology. Count-based, depth-matched, donor-level analysis with an explicit confound audit is the more conservative standard.",
  {x:1.0,y:4.65,w:11.3,h:1.6,fontFace:BF,fontSize:16.5,italic:true,color:"D7E6E8",lineSpacing:24,margin:0});
pageno(s,13);

// ---------- 15 METHODS APPENDIX ----------
s=content(); label(s,"appendix · methods");
title(s,"Methods, in brief");
const mm=[
  ["Raw molecule counts","Extracted the RNA-assay counts from the Seurat object — the shipped matrix is an SCT model output, not molecules. 45-gene panel + full library size per nucleus."],
  ["Depth-matched","Downsample every nucleus to a common budget (1,000 / 1,500 / 3,000 UMIs) by binomial thinning, averaged over 8 draws — the standard count-preserving depth control."],
  ["Anchor census","Classify each nucleus PC / PP / dual / null on the canonical landmarks (GLUL, CYP3A4 vs ASS1, CPS1, PCK1, HAL, ALDOB); sweep thresholds, anchor genes, and programs."],
  ["Donor-level inference","Donor is the unit (~47): per-donor medians + ranges by stage. Two axes — fibrosis F0–F4 and NAS. Minimum detectable effect estimated at donor level."]
];
let mx=0.7, my=2.25, mw=6.0, mh=1.95, mgx=0.35, mgy=0.3;
mm.forEach((c,i)=>{const col=i%2,row=Math.floor(i/2);
  const x=mx+col*(mw+mgx), y=my+row*(mh+mgy);
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w:mw,h:mh,fill:{color:WHITE},rectRadius:0.07,shadow:shadow()});
  s.addShape(p.shapes.RECTANGLE,{x,y,w:0.12,h:mh,fill:{color:i%2?AMBER:TEAL}});
  s.addText(c[0],{x:x+0.35,y:y+0.22,w:mw-0.6,h:0.5,fontFace:HF,fontSize:17,bold:true,color:INK,margin:0});
  s.addText(c[1],{x:x+0.35,y:y+0.78,w:mw-0.6,h:mh-0.95,fontFace:BF,fontSize:13,color:"45565B",lineSpacing:18,margin:0,valign:"top"});
});
s.addText("GSE202379 (Gribben et al., Nature 2024) · 47 donors · 69,426 hepatocyte nuclei · full numeric record in FINDINGS.md",
  {x:0.7,y:6.45,w:11.9,h:0.4,fontFace:BF,fontSize:11.5,italic:true,color:MUTE,margin:0});
pageno(s);

p.writeFile({fileName:"Zonation_Reanalysis.pptx"}).then(f=>console.log("wrote",f));
