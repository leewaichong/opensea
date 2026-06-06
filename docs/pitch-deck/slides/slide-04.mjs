import { C, setup, addText, addBox, addKicker, addArrow } from "./deck-helpers.mjs";

export async function slide04(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `This is the core originality slide, placed before the demo proof so judges know what to watch for. The naive baseline looks only at positions, so it marks "support reaching younger shoppers" as agreed. The assumption-aware classifier compares success criteria and surfaces fake agreement: acquisition, GMV, and mainstream-safe youth reach are different objectives. Both paths are implemented and tested in src/pmle/crux_engine.py, so this is a verifiable build artifact, not a claim.`, "soft");
  addKicker(slide, "Wedge", "Position-only classification misses\nthe dangerous case.", "Sources: docs/design-spec.md, docs/pitch-script.md", 4);

  addBox(slide, 92, 222, 430, 262, C.white, C.line, 8);
  addText(slide, "Naive baseline", 124, 252, 260, 26, { size: 18, bold: true });
  addText(slide, "Input", 124, 310, 70, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "Everyone supports reaching younger shoppers.", 124, 332, 320, 44, { size: 22 });
  addText(slide, "Output", 124, 400, 80, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "AGREED", 124, 426, 150, 34, { size: 27, color: C.graphite, bold: true });

  addArrow(slide, 552, 346, 80, C.line);

  addBox(slide, 660, 222, 464, 262, C.fog, C.graphite, 8);
  addText(slide, "Assumption-aware classifier", 692, 252, 330, 26, { size: 18, color: C.graphite, bold: true });
  addText(slide, "Input", 692, 310, 70, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "Growth: app installs\nCommerce: GMV\nLead: safe youth reach", 692, 328, 342, 72, { size: 20, leading: 110 });
  addText(slide, "Output", 692, 412, 80, 16, { size: 11, color: C.muted, bold: true });
  addText(slide, "FAKE AGREEMENT", 692, 438, 282, 34, { size: 27, color: C.graphite, bold: true });

  addText(slide, "Both paths shipped and tested — naive_baseline vs classify_item in src/pmle/crux_engine.py", 92, 500, 1032, 20, {
    size: 13,
    color: C.muted,
  });

  addBox(slide, 112, 536, 940, 78, C.darkPanel, "none", 8);
  addText(slide, "Judge takeaway: Mochi catches the objective mismatch before the creator decision meeting.", 128, 552, 900, 50, { size: 22, bold: true, color: C.white });
  return slide;
}
