import { C, setup, addText, addBox, addKicker, addImageAsset } from "./deck-helpers.mjs";

export async function slide08(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Close. Bring the judges back to the sentence from the live script: meetings do not fail because people think they agree. Mochi catches the fake agreement before the hour is gone, inside Slack. Stop at the generated pre-meeting brief; do not imply a final influencer decision. Missing for final submission: GitHub/demo URLs, raw test output, live trace artifact, latency/reliability, and measured adoption/time-saved only if measured.`, "soft");
  addKicker(slide, "Close", "Mochi catches fake agreement\nbefore the hour is gone.", "Sources: docs/pitch-script.md, docs/submission-checklist.md", 8);

  addText(slide, "Not after-meeting summary.\nBefore-meeting crux.\nInside Slack.", 92, 214, 620, 132, {
    size: 36,
    color: C.ink,
  });
  addImageAsset(slide, "../assets/mochi-mascot-rounded.png", 790, 212, 176, 176, "Mochi mascot", "mochi-mascot-close");

  addBox(slide, 92, 388, 694, 136, C.white, C.line, 8);
  addText(slide, "The owner still decides. The meeting just starts at the crux.", 124, 420, 610, 56, {
    size: 22,
    color: C.ink,
    bold: true,
  });
  addText(slide, "Shopee 11.11 creator mix: objective first, role split second, provenance preserved.", 124, 484, 610, 24, {
    size: 16,
    color: C.muted,
  });

  const criteria = [
    ["Problem", "unprepared meetings waste time"],
    ["Technology", "persistent + ephemeral agents"],
    ["Outcome", "two decisions before the meeting"],
  ];
  criteria.forEach(([head, body], i) => {
    const y = 420 + i * 42;
    addText(slide, head, 842, y, 132, 20, { size: 15, bold: true, color: C.graphite });
    addText(slide, body, 982, y, 230, 20, { size: 15, color: C.muted });
  });

  addBox(slide, 92, 584, 1040, 54, C.darkPanel, "none", 8);
  addText(slide, "The vision", 124, 600, 140, 18, { size: 13, color: "#BFC5C9", bold: true });
  addText(slide, "Every recurring meeting gets a pre-meeting reasoning loop.", 284, 600, 760, 24, {
    size: 20,
    color: C.white,
    bold: true,
  });
  return slide;
}
