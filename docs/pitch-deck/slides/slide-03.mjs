import { C, setup, addText, addBox, addKicker, addArrow } from "./deck-helpers.mjs";

export async function slide03(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Product explanation. Mochi starts from a free-form Slack DM. John mentions the Shopee brief and Growth, Commerce, and Lead stakeholders. Mochi parses the roster, fans out to persistent participant agents, then a transient orchestrator compiles the compressed brief. Stop at the pre-meeting brief; do not show a final influencer decision.`, "soft");
  addKicker(slide, "Product", "Mochi turns one Slack DM into\na pre-meeting brief.", "Sources: docs/design-spec.md, docs/pitch-script.md", 3);

  const steps = [
    ["Free-form DM", "John writes prep\n+ teammate mentions"],
    ["Roster parse", "Growth, Commerce,\nCampaign Lead"],
    ["Participant DMs", "persistent agents collect\nstructured stances"],
    ["Assumption diff", "objective mismatch\n+ role-mix crux"],
    ["Block Kit brief", "9 -> 2 agenda,\nprovenance, actions"],
  ];
  steps.forEach(([title, body], i) => {
    const x = 70 + i * 232;
    addBox(slide, x, 242, 182, 176, i === 3 ? C.linen : C.white, i === 3 ? C.graphite : C.line, 8);
    addText(slide, title, x + 18, 268, 146, 22, { size: 15, color: C.graphite, bold: true });
    addText(slide, body, x + 18, 308, 146, 68, { size: 18, color: C.ink, leading: 110 });
    if (i < steps.length - 1) addArrow(slide, x + 190, 322, 42, C.line);
  });
  addText(slide, "Trust boundary", 88, 498, 170, 22, { size: 13, color: C.muted, bold: true });
  addText(slide, "Mochi compresses what needs discussion. John Taylor still owns the creator-mix decision with logged dissents.", 88, 528, 930, 54, {
    size: 22,
    color: C.ink,
  });
  return slide;
}
