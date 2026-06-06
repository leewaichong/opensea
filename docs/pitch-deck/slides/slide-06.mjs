import { C, setup, addText, addBox, addKicker, addArrow } from "./deck-helpers.mjs";

export async function slide06(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Technical slide. Sell the frontier technology, not the backstage demo switches. Explain persistent participant sessions and ephemeral meeting orchestration through the OpenAI Agents SDK. Slack is the human interface; managed agents hold stance context; a transient orchestrator compares assumptions and dissolves. Mention tracing as proof if shown live.`, "soft");
  addKicker(slide, "Build", "Managed agents make prep continuous,\nthen disappear.", "Sources: docs/pitch-script.md, docs/build-plan.md", 6);

  const lanes = [
    ["Slack", "natural-language prep\nstakeholder mentions\nbrief delivery", C.white, C.line],
    ["Persistent sessions", "one agent per person\nstance history\nstructured tools", C.white, C.line],
    ["Ephemeral session", "one orchestrator\nfor one meeting\nthen dissolves", C.linen, C.graphite],
    ["Traceable output", "assumption diff\nprovenance\nhuman-owned brief", C.white, C.line],
  ];
  lanes.forEach(([head, body, fill, line], i) => {
    const x = 94 + i * 268;
    addBox(slide, x, 226, 220, 242, fill, line, 8);
    addText(slide, head, x + 22, 254, 160, 28, { size: 24, bold: true, color: C.ink });
    addText(slide, body, x + 22, 304, 170, 110, { size: 20, leading: 120 });
    if (i < lanes.length - 1) addArrow(slide, x + 228, 340, 38, C.line);
  });
  addBox(slide, 96, 480, 1020, 34, C.fog, C.line, 8);
  addText(slide, "58 tests passing  ·  pydantic v2 contracts  ·  SQLiteSession persistence  ·  Block Kit digest  ·  assumption-aware vs naive baseline", 112, 488, 992, 20, {
    size: 13,
    color: C.graphite,
    bold: true,
  });
  addBox(slide, 96, 528, 1020, 64, C.darkPanel, "none", 8);
  addText(slide, "OpenAI Agents SDK", 124, 544, 220, 18, { size: 13, color: "#BFC5C9", bold: true });
  addText(slide, "Persistent context + ephemeral orchestration is the product pattern.", 360, 536, 700, 34, {
    size: 22,
    color: C.white,
    bold: true,
  });
  return slide;
}
