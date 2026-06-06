import { C, setup, addText, addBox, addRule, addPill, addImageAsset } from "./deck-helpers.mjs";

export async function slide01(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Cold open. Lead with the outcome, not the mechanism: Mochi helps teams meet less and decide faster by clearing the items that do not need a live meeting and starting the room at the real crux. The Shopee SG 11.11 creator-mix demo compresses a nine-item agenda to two live decisions. Do not claim measured time savings or adoption; those are not in the source docs. The 9 to 2 figure is the demo artifact, not a time metric.`, "soft");

  addText(slide, "PerMyLastEmail / Mochi", 74, 60, 320, 24, { size: 17, bold: true, color: C.muted });
  addPill(slide, "BUILD DIRECTION  ·  AI-NATIVE PRODUCTS & OPERATIONS", 74, 94, 480, C.codexDeep, C.blueSoft);
  addText(slide, "Cut the meeting,\nnot the decision.", 70, 142, 660, 142, {
    size: 54,
    color: C.ink,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  addText(slide, "Meet less, decide faster. Mochi clears the easy items in Slack before you meet, so the room opens on the real crux.", 74, 300, 690, 60, {
    size: 20,
    color: C.graphite,
    leading: 124,
  });
  addRule(slide, 74, 374, 560, C.line);
  addText(slide, "Demo decision", 76, 398, 160, 20, { size: 12, color: C.muted, bold: true });
  addText(slide, "Prepare Shopee SG 11.11 creator mix", 76, 424, 410, 36, { size: 24, color: C.ink });
  addImageAsset(slide, "../assets/mochi-mascot-rounded.png", 496, 388, 144, 144, "Mochi mascot", "mochi-mascot-cover");
  addText(slide, "Mochi lives in Slack", 496, 542, 144, 22, { size: 13, color: C.graphite, bold: true, align: "center" });

  addBox(slide, 775, 108, 360, 444, C.white, "none", 8);
  addText(slide, "Shorter meeting, fewer items", 808, 142, 300, 22, { size: 13, color: C.muted, bold: true });
  addText(slide, "9", 810, 202, 115, 96, { size: 96, color: C.ink, bold: true, align: "center" });
  addText(slide, "items", 820, 302, 95, 22, { size: 16, color: C.muted, align: "center" });
  addText(slide, "->", 940, 240, 40, 34, { size: 30, color: C.muted, align: "center" });
  addText(slide, "2", 1000, 202, 95, 96, { size: 96, color: C.graphite, bold: true, align: "center" });
  addText(slide, "meeting items", 982, 302, 130, 22, { size: 16, color: C.muted, align: "center" });
  addRule(slide, 810, 350, 280, C.line);
  addText(slide, "objective: fake agreement\nrole mix: unresolved crux\n3 action items resolved", 812, 376, 270, 94, {
    size: 21,
    color: C.ink,
    leading: 120,
  });
  addText(slide, "Sources: README, docs/overview.md, docs/pitch-script.md", 72, 684, 700, 18, { size: 10, color: C.muted });
  addText(slide, "01", 1180, 684, 40, 18, { size: 10, color: C.muted, align: "right" });
  return slide;
}
