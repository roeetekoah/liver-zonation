// Standalone "Thank you — now QA" closing slide, in the deck's dark separator style.
// Inserted into the canonical after the conclusion via PowerPoint InsertFromFile. Run: node thankyou_qa.js
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const A = __dirname + "/assets/";
function pngSize(f){ const b=fs.readFileSync(f); return {w:b.readUInt32BE(16), h:b.readUInt32BE(20)}; }
const DARK="16242B", TEAL="1B6E78", AMBER="C0561B", WHITE="FFFFFF", SERIF="Georgia";
const p=new pptxgen(); p.layout="LAYOUT_WIDE";
const s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:13.333,h:7.5,fill:{color:DARK},line:{type:"none"}}); // full-bleed (survives import)
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.28,h:7.5,fill:{color:TEAL}});
s.addShape(p.shapes.RECTANGLE,{x:0.28,y:0,w:0.12,h:7.5,fill:{color:AMBER}});
// liver-lobule zonation motif, on the right
const d=pngSize(A+"thankyou_art.png"), box=4.4; let aw=box, ah=box*d.h/d.w; if(ah>box){ ah=box; aw=box*d.w/d.h; }
s.addImage({path:A+"thankyou_art.png", x:8.6+(box-aw)/2, y:1.6+(box-ah)/2, w:aw, h:ah});
// text, on the left
s.addText("Thank you",{x:0.95,y:2.35,w:7.5,h:1.3,fontSize:52,bold:true,color:WHITE,fontFace:SERIF,align:"left",valign:"middle"});
s.addText("now — QA:  your questions",{x:0.98,y:3.82,w:7.5,h:0.55,fontSize:18,italic:true,color:"9FC0C4",align:"left"});
s.addText("No hepatocytes lost their identity in the making of this talk.",
  {x:0.98,y:4.58,w:7.5,h:0.5,fontSize:13.5,italic:true,color:"C0561B",align:"left"});
s.addText("Roee Tekoah  ·  Shira Gelbstein  ·  Computational Genomics 76553 · HUJI",
  {x:0.98,y:6.7,w:11.6,h:0.4,fontSize:13,color:"7E8F8B",align:"left"});
p.writeFile({fileName:__dirname+"/thankyou_qa.pptx"}).then(f=>console.log("WROTE",f));
