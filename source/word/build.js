const fs = require("fs");
const d = require("docx");
const {Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, LevelFormat, BorderStyle, ShadingType} = d;
const blocks = JSON.parse(fs.readFileSync("blocks.json", "utf8"));
const F = "Arial";
const R = (t, o = {}) => new TextRun({text: t, font: F, rightToLeft: true, ...o});
const para = (t, o = {}, ro = {}) => new Paragraph({bidirectional: true, alignment: AlignmentType.START, children: [R(t, ro)], ...o});
const H = [null, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3];
const box = {border: {top: {style: BorderStyle.SINGLE, size: 6, color: "B8901C", space: 4}, bottom: {style: BorderStyle.SINGLE, size: 6, color: "B8901C", space: 4},
  left: {style: BorderStyle.SINGLE, size: 6, color: "B8901C", space: 4}, right: {style: BorderStyle.SINGLE, size: 6, color: "B8901C", space: 4}},
  shading: {type: ShadingType.CLEAR, color: "auto", fill: "FBF4DC"}, spacing: {after: 60}};
const intro = [
  new Paragraph({heading: HeadingLevel.TITLE, bidirectional: true, alignment: AlignmentType.CENTER, children: [R("شجرة عائلة البشيراب")]}),
  para("نسخة للتصحيح والإضافة", {alignment: AlignmentType.CENTER, spacing: {after: 240}}, {size: 30, color: "66757B"}),
  para("طريقة التعديل", box, {bold: true, size: 30}),
  para("• عدّل أي اسم أو أضف مباشرة في هذا الملف كأي ملف عادي، ثم أعد إرساله. ما تكتبه أو تحذفه يظهر بلون مختلف تلقائياً.", box),
  para("• لإضافة ابن أو بنت: اكتب الاسم في سطر جديد تحت إخوته.", box),
  para("• إذا كان لشخص أبناء وليست له أسرة في الملف، اكتب بجانب اسمه كلمة «أبناؤه» ثم أسماءهم.", box),
  para("• العلامة (ر) تعني: متوفى، رحمه الله.", box),
];
const body = blocks.map(b => {
  if (b.t === "h") return new Paragraph({heading: H[b.lv], bidirectional: true, alignment: AlignmentType.START, children: [R(b.x)]});
  if (b.t === "g") return para(b.x, {spacing: {before: 120, after: 40}}, {bold: true, color: "1F4E5F"});
  if (b.t === "k") return new Paragraph({bidirectional: true, alignment: AlignmentType.START, numbering: {reference: "kids", level: 0}, children: [R(b.x)]});
  return para(b.x, {}, {color: "444444"});
});
const hs = (size, color, before) => ({run: {font: F, size, bold: true, color, rightToLeft: true}, paragraph: {spacing: {before, after: 100}, keepNext: true, bidirectional: true}});
const doc = new Document({
  features: {trackRevisions: true},
  styles: {default: {document: {run: {font: F, size: 28, rightToLeft: true}, paragraph: {spacing: {after: 60, line: 300}}}},
    paragraphStyles: [
      {id: "Title", name: "Title", basedOn: "Normal", run: {font: F, size: 52, bold: true, color: "1F4E5F", rightToLeft: true}, paragraph: {spacing: {before: 0, after: 80}, keepNext: true}},
      {id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, ...hs(36, "1F4E5F", 480), paragraph: {spacing: {before: 480, after: 120}, keepNext: true, outlineLevel: 0}},
      {id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, ...hs(32, "2C6A7D", 360), paragraph: {spacing: {before: 360, after: 100}, keepNext: true, outlineLevel: 1}},
      {id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, ...hs(28, "1F2D33", 280), paragraph: {spacing: {before: 280, after: 80}, keepNext: true, outlineLevel: 2}},
    ]},
  numbering: {config: [{reference: "kids", levels: [{level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.START,
    style: {paragraph: {indent: {start: 500, hanging: 300}}}}]}]},
  sections: [{properties: {page: {margin: {top: 1100, bottom: 1100, left: 1100, right: 1100}}}, children: [...intro, ...body]}]
});
Packer.toBuffer(doc).then(b => fs.writeFileSync("out.docx", b));
