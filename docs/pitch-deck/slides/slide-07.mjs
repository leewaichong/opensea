import { C, setup, addText, addBox, addKicker, addRule } from "./deck-helpers.mjs";

export async function slide07(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Demo flow slide. This is for the presenter to keep the six-minute story tight: start with pain, show Mochi in Slack, show the agent fan-out, show the brief, contrast the naive baseline, then close on the vision. Mention raw eval output and metrics are not in the source docs only if asked.`, "soft");
  addKicker(slide, "Pitch Flow", "Six minutes, one narrative arc.", "Sources: docs/pitch-script.md, docs/judging-alignment.md", 7);

  const beats = [
    ["1", "Name the pain", "Meetings waste time resolving vague assumptions."],
    ["2", "Start in Slack", "John asks Mochi to prep the Shopee creator mix."],
    ["3", "Agents fan out", "Persistent sessions collect each stakeholder stance."],
    ["4", "Show the brief", "Nine items become two decisions."],
  ];
  beats.forEach(([num, title, body], i) => {
    const x = 88 + i * 282;
    addBox(slide, x, 244, 236, 210, i === 3 ? C.linen : C.white, i === 3 ? C.graphite : C.line, 8);
    addText(slide, num, x + 24, 268, 48, 46, { size: 42, color: C.ink, bold: true });
    addText(slide, title, x + 24, 330, 180, 26, { size: 22, color: C.ink, bold: true });
    addText(slide, body, x + 24, 374, 180, 54, { size: 17, color: C.graphite, leading: 128 });
  });

  addRule(slide, 110, 500, 990, C.line);
  addText(slide, "Narrative turn", 112, 532, 150, 20, { size: 14, color: C.muted, bold: true });
  addText(slide, "A summarizer sees agreement. Mochi sees the assumptions that would waste the meeting.", 270, 528, 760, 28, {
    size: 22,
    color: C.ink,
    bold: true,
  });
  return slide;
}
