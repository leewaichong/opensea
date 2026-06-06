import { C, setup, addText, addBox, addKicker } from "./deck-helpers.mjs";

export async function slide07(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Use of Codex slide. Codex was a build partner, not just autocomplete. Map concrete Codex contributions to concrete artifacts in this repo: it pivoted the scenario to a Slack-native pre-meeting crux finder, built the transient orchestrator and free-form DM routing, kept the docs and code in sync, and wrote the deterministic test suite and demo hardening. Keep claims grounded in AGENTS.md and the pitch script; do not overstate. Keep cached/live boundary details in notes, not on the slide.`, "soft");
  addKicker(slide, "Use of Codex", "Codex shaped the product and\nwrote the build.", "Sources: AGENTS.md, docs/pitch-script.md", 7);

  const cards = [
    ["Scenario pivot", "Reframed the project into a Slack-native pre-meeting crux finder."],
    ["Orchestrator + Slack path", "Built the transient orchestrator and free-form DM routing on the OpenAI Agents SDK."],
    ["Docs in sync with code", "Kept README, specs, and implementation aligned as the design changed."],
    ["Tests + hardening", "Wrote 58 deterministic offline tests and hardened the demo fallback."],
  ];
  cards.forEach(([head, body], i) => {
    const x = 88 + (i % 2) * 524;
    const y = 236 + Math.floor(i / 2) * 154;
    addBox(slide, x, y, 500, 138, i === 3 ? C.linen : C.white, i === 3 ? C.graphite : C.line, 8);
    addText(slide, head, x + 26, y + 22, 448, 28, { size: 22, color: C.ink, bold: true });
    addText(slide, body, x + 26, y + 64, 448, 60, { size: 18, color: C.graphite, leading: 124 });
  });

  addBox(slide, 88, 556, 1024, 62, C.darkPanel, "none", 8);
  addText(slide, "Built with Codex", 120, 578, 180, 18, { size: 13, color: "#BFC5C9", bold: true });
  addText(slide, "From scenario pivot to test suite, Codex built alongside — not just autocomplete.", 312, 576, 788, 24, {
    size: 19,
    color: C.white,
    bold: true,
  });
  return slide;
}
