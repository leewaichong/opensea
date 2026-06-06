import { C, setup, addText, addBox, addKicker, addRule } from "./deck-helpers.mjs";

export async function slide02(presentation) {
  const slide = presentation.slides.add();
  setup(slide, `Problem framing. Meetings do not fail only because people disagree. They fail because dangerous disagreement hides behind shared language. Walk judges through the Shopee creator-mix interpretations of "younger shoppers": Growth wants acquisition, Commerce wants GMV, and the Campaign Lead wants mainstream-safe youth relevance.`, "soft");
  addKicker(slide, "Problem", "Poor prep turns meetings into\nambiguity cleanup.", "Sources: docs/overview.md, docs/pitch-script.md", 2);

  addBox(slide, 84, 206, 520, 244, C.white, C.line, 8);
  addText(slide, "\"Reach younger\nshoppers.\"", 114, 236, 440, 88, { size: 32, bold: true, leading: 105 });
  addText(slide, "A normal summarizer sees one phrase repeated and marks the objective as aligned.", 116, 336, 420, 48, {
    size: 20,
    color: C.muted,
  });
  addText(slide, "But the success criteria underneath do not match.", 116, 398, 420, 24, { size: 18, color: C.ink, bold: true });

  const roles = [
    ["Growth", "Acquisition, app installs, first purchases", C.fog, C.line],
    ["Commerce", "GMV, voucher redemption, live conversion", C.fog, C.line],
    ["Campaign Lead", "Mainstream-safe youth reach", C.linen, C.line],
    ["Naive baseline", "Marks the objective agreed", C.white, C.graphite],
  ];
  roles.forEach(([role, assumption, fill, color], i) => {
    const x = 670 + (i % 2) * 242;
    const y = 220 + Math.floor(i / 2) * 132;
    addBox(slide, x, y, 214, 94, fill, color, 8);
    addText(slide, role, x + 18, y + 16, 160, 18, { size: 12, color: C.graphite, bold: true });
    addText(slide, assumption, x + 18, y + 38, 178, 52, { size: 15, color: C.ink, leading: 102 });
  });
  addRule(slide, 670, 500, 456);
  addText(slide, "Product wedge: preserve meeting time for decisions, not assumption discovery.", 670, 526, 460, 40, {
    size: 23,
    bold: true,
  });
  return slide;
}
