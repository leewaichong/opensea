import { C, setup, addText, addBox, addRule, addImageAsset } from "./deck-helpers.mjs";

export async function slide01(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Cold open. Everyone says "reach younger shoppers" for Shopee SG 11.11. A summarizer marks alignment. Growth means acquisition and app installs; Commerce means GMV and voucher redemption; the Campaign Lead means mainstream-safe youth reach. Same phrase, different assumptions. Introduce Mochi as the Slack-native pre-meeting crux finder. Do not claim measured time savings or adoption; those are not in the source docs.`, "soft");

  addText(slide, "PerMyLastEmail / Mochi", 74, 64, 320, 24, { size: 17, bold: true, color: C.muted });
  addText(slide, "Same phrase,\ndifferent goals.", 70, 128, 650, 142, {
    size: 54,
    color: C.ink,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  addText(slide, "Persistent personal agents + transient meeting orchestrator", 74, 306, 660, 32, {
    size: 20,
    color: C.graphite,
  });
  addRule(slide, 74, 360, 560, C.line);
  addText(slide, "Demo decision", 76, 386, 160, 20, { size: 12, color: C.muted, bold: true });
  addText(slide, "Prepare Shopee SG 11.11 creator mix", 76, 412, 560, 36, { size: 24, color: C.ink });
  addImageAsset(slide, "../assets/mochi-mascot-rounded.png", 496, 388, 144, 144, "Mochi mascot", "mochi-mascot-cover");
  addText(slide, "Mochi lives in Slack", 496, 542, 144, 22, { size: 13, color: C.graphite, bold: true, align: "center" });

  addBox(slide, 775, 108, 360, 444, C.white, "none", 8);
  addText(slide, "Slack pre-meeting digest", 808, 142, 280, 22, { size: 13, color: C.muted, bold: true });
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
