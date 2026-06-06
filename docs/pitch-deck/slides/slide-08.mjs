import { C, setup, addText, addBox, addKicker, addArrow, addPill } from "./deck-helpers.mjs";

export async function slide08(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Vision slide, framed as architecture and roadmap, not a shipped demo feature. Mochi is an orchestration layer: it coordinates agents rather than replacing them. The structured stance contract (position, rationale, assumptions, confidence) is the open interface. Today, managed agents fill that contract for each participant. The roadmap is bring-your-own-agent: a user points their own personal agent at Mochi; it negotiates their stance in their voice, keeps their context private, and emits only a structured stance. Do not claim BYOA is demoed; label it roadmap. The point is that Mochi is the protocol for pre-meeting agent reasoning, not a silo.`, "soft");
  addKicker(slide, "Vision", "An orchestration layer.\nBring your own agent.", "Sources: docs/design-spec.md, AGENTS.md", 8);

  const lanes = [
    ["Your agents", "one per participant\nyour model + context\nyour tools", C.white, C.line],
    ["Stance contract", "position\nrationale, assumptions\nconfidence", C.linen, C.graphite],
    ["Mochi orchestrator", "compares assumptions\nclears easy items\nthen dissolves", C.white, C.line],
    ["Compressed brief", "only real cruxes\nprovenance\nhuman-owned", C.white, C.line],
  ];
  lanes.forEach(([head, body, fill, line], i) => {
    const x = 94 + i * 268;
    addBox(slide, x, 224, 220, 176, fill, line, 8);
    addText(slide, head, x + 22, 250, 176, 26, { size: 21, bold: true, color: C.ink });
    addText(slide, body, x + 22, 296, 176, 96, { size: 17, color: C.graphite, leading: 122 });
    if (i < lanes.length - 1) addArrow(slide, x + 228, 308, 38, C.line);
  });

  addBox(slide, 94, 424, 500, 134, C.white, C.line, 8);
  addText(slide, "Today", 120, 446, 200, 20, { size: 13, color: C.muted, bold: true });
  addText(slide, "Managed agents fill the stance contract for each person.", 120, 472, 446, 60, {
    size: 19,
    color: C.ink,
    leading: 124,
  });

  addBox(slide, 612, 424, 500, 134, C.fog, C.graphite, 8);
  addPill(slide, "ROADMAP", 638, 442, 112, C.codexDeep, C.blueSoft);
  addText(slide, "Bring your own agent", 762, 446, 330, 22, { size: 15, color: C.graphite, bold: true });
  addText(slide, "Point your own agent at Mochi. It speaks the stance contract, keeps your context private, and emits only a structured stance.", 638, 482, 452, 70, {
    size: 17,
    color: C.ink,
    leading: 120,
  });

  addBox(slide, 94, 584, 1018, 56, C.darkPanel, "none", 8);
  addText(slide, "The protocol", 122, 602, 150, 18, { size: 13, color: "#BFC5C9", bold: true });
  addText(slide, "Mochi is the protocol for pre-meeting agent reasoning, not the silo.", 288, 600, 800, 24, {
    size: 20,
    color: C.white,
    bold: true,
  });
  return slide;
}
