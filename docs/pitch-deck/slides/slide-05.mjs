import { C, setup, addText, addBox, addKicker, agendaTile } from "./deck-helpers.mjs";

export async function slide05(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Demo proof. Show the actual Mochi digest shape from docs/pitch-script.md: the agenda compresses to one fake-agreement objective, one unresolved role-mix crux, and three cleared action items. That leaves two live decisions: align the primary objective, then decide the creator role mix. Do not show a final influencer decision. Do not claim measured time savings; no such metric is in the docs.`, "soft");
  addKicker(slide, "Demo Proof", "The room starts with two real decisions.", "Sources: docs/pitch-script.md, docs/build-plan.md", 5);

  addBox(slide, 82, 206, 448, 350, C.white, C.line, 8);
  addText(slide, "Mochi pre-meeting digest", 110, 224, 320, 22, { size: 14, color: C.muted, bold: true });
  addText(slide, "Slack DM · agenda compressed 9 -> 2", 110, 248, 360, 20, { size: 13, color: C.muted });
  agendaTile(slide, 102, 282, 408, 80, "Objective: success criteria differ", "fake", "Growth · Commerce · Campaign Lead");
  agendaTile(slide, 102, 372, 408, 80, "Creator role split unresolved", "crux", "Hero face vs hero + Shopee Live");
  agendaTile(slide, 102, 462, 408, 80, "Action items cleared: 3", "agreed", "0 need an owner · owner: John Taylor");

  addBox(slide, 554, 206, 560, 162, C.linen, C.graphite, 8);
  addText(slide, "1. Align the success objective", 586, 236, 460, 30, { size: 24, color: C.ink, bold: true });
  addText(slide, "Growth wants acquisition. Commerce wants GMV. The campaign lead wants mainstream-safe youth reach.", 586, 284, 470, 64, {
    size: 18,
    color: C.graphite,
    leading: 130,
  });

  addBox(slide, 554, 392, 560, 164, C.white, C.graphite, 8);
  addText(slide, "2. Decide the creator role split", 586, 422, 460, 30, { size: 24, color: C.ink, bold: true });
  addText(slide, "One hero face, or hero plus Shopee Live conversion partner. John owns the final call.", 586, 470, 470, 44, {
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
