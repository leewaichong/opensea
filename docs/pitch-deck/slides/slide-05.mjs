import { C, setup, addText, addBox, addKicker, addArrow } from "./deck-helpers.mjs";

export async function slide05(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `This is the core originality slide. The naive baseline looks only at positions, so it marks "support reaching younger shoppers" as agreed. The assumption-aware classifier compares success criteria and surfaces fake agreement: acquisition, GMV, and mainstream-safe youth reach are different objectives.`, "soft");
  addKicker(slide, "Wedge", "Position-only classification misses\nthe dangerous case.", "Sources: docs/design-spec.md, docs/pitch-script.md", 5);

  addBox(slide, 92, 230, 430, 270, C.white, C.line, 8);
  addText(slide, "Naive baseline", 124, 260, 260, 26, { size: 18, bold: true });
  addText(slide, "Input", 124, 318, 70, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "Everyone supports reaching younger shoppers.", 124, 340, 320, 44, { size: 22 });
  addText(slide, "Output", 124, 408, 80, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "AGREED", 124, 434, 150, 34, { size: 27, color: C.graphite, bold: true });

  addArrow(slide, 552, 354, 80, C.line);

  addBox(slide, 660, 230, 464, 270, C.fog, C.graphite, 8);
  addText(slide, "Assumption-aware classifier", 692, 260, 330, 26, { size: 18, color: C.graphite, bold: true });
  addText(slide, "Input", 692, 318, 70, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "Growth: app installs\nCommerce: GMV\nLead: safe youth reach", 692, 336, 342, 72, { size: 20, leading: 110 });
  addText(slide, "Output", 692, 420, 80, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "FAKE AGREEMENT", 692, 446, 282, 34, { size: 27, color: C.graphite, bold: true });
  addBox(slide, 112, 536, 940, 78, C.darkPanel, "none", 8);
  addText(slide, "Judge takeaway: Mochi catches the objective mismatch before the creator decision meeting.", 128, 552, 900, 50, { size: 22, bold: true, color: C.white });
  return slide;
}
