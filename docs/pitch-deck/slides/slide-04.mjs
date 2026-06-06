import { C, setup, addText, addBox, addKicker, addRule } from "./deck-helpers.mjs";

export async function slide04(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Demo proof. Show the final Mochi brief shape. The brief compresses nine agenda items to two live agenda items: align the primary objective, then decide the creator role mix. Action items are three resolved and zero need an owner. Do not show a final influencer decision. Do not claim measured time savings; no such metric is in the docs.`, "soft");
  addKicker(slide, "Demo Proof", "The room starts with two real decisions.", "Sources: docs/pitch-script.md, docs/build-plan.md", 4);

  addBox(slide, 82, 214, 410, 302, C.white, C.line, 8);
  addText(slide, "Mochi pre-meeting brief", 116, 246, 320, 24, { size: 18, color: C.muted, bold: true });
  addText(slide, "9", 116, 294, 112, 96, { size: 92, color: C.ink, bold: true, align: "center" });
  addText(slide, "agenda items", 118, 394, 112, 24, { size: 16, color: C.muted, align: "center" });
  addText(slide, "->", 254, 326, 54, 34, { size: 30, color: C.muted, align: "center" });
  addText(slide, "2", 332, 294, 94, 96, { size: 92, color: C.ink, bold: true, align: "center" });
  addText(slide, "live decisions", 318, 394, 122, 24, { size: 16, color: C.muted, align: "center" });
  addRule(slide, 116, 444, 326, C.line);
  addText(slide, "Action items: 3 resolved, 0 need an owner", 116, 466, 320, 24, { size: 18, color: C.graphite, bold: true });

  addBox(slide, 554, 214, 560, 160, C.linen, C.graphite, 8);
  addText(slide, "1. Align the success objective", 586, 244, 460, 30, { size: 24, color: C.ink, bold: true });
  addText(slide, "Growth wants acquisition. Commerce wants GMV. The campaign lead wants mainstream-safe youth reach.", 586, 292, 470, 64, {
    size: 18,
    color: C.graphite,
    leading: 130,
  });

  addBox(slide, 554, 398, 560, 146, C.white, C.graphite, 8);
  addText(slide, "2. Decide the creator role split", 586, 428, 460, 30, { size: 24, color: C.ink, bold: true });
  addText(slide, "One hero face, or hero plus Shopee Live conversion partner. John owns the final call.", 586, 476, 470, 44, {
    size: 19,
    color: C.graphite,
    leading: 130,
  });

  addText(slide, "Pre-read, not live debate", 90, 584, 220, 20, { size: 14, color: C.muted, bold: true });
  addText(slide, "Short-form + Shopee Live, tracking, hero categories, paid amplification, brand-safety review, backup creators.", 90, 612, 900, 28, {
    size: 17,
    color: C.graphite,
  });
  return slide;
}
