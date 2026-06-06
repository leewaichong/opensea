# Hackathon Pitch Deck

This directory contains the editable source and current generated output for the
PerMyLastEmail / Mochi hackathon pitch deck.

## Current output

- PowerPoint: `output/per-my-last-email-hackathon-pitch.pptx`
- Contact sheet: `preview/contact-sheet.png`
- Slide previews: `preview/slide-01.png` through `preview/slide-08.png`

## Edit the deck

Edit the slide modules in `slides/`:

- `slides/deck-helpers.mjs` contains shared colors, typography helpers, image
  background helpers, and repeated components.
- `slides/slide-01.mjs` through `slides/slide-08.mjs` contain the individual
  slide content and speaker notes.
- `assets/` contains the Codex-style generated backgrounds and rounded Mochi
  mascot image.

The visible deck should stay pitch-facing. Avoid putting demo switches, cached
fallbacks, live-boundary details, raw eval caveats, or unmeasured time-saved
claims on slides. Keep missing data in speaker notes or this README unless the
data is measured and sourced.

## Rebuild

From the repo root:

```bash
scripts/build_pitch_deck.sh
```

The script regenerates:

- `docs/pitch-deck/output/per-my-last-email-hackathon-pitch.pptx`
- `docs/pitch-deck/preview/contact-sheet.png`
- `docs/pitch-deck/preview/slide-*.png`
- `docs/pitch-deck/layout/final/slide-*.layout.json`
- `docs/pitch-deck/output/artifact-build-manifest.json`

The build uses the Codex Presentations runtime script
`build_artifact_deck.mjs`. If it is not in the default local cache path, set:

```bash
CODEX_PRESENTATIONS_SKILL_DIR=/path/to/presentations/skill scripts/build_pitch_deck.sh
```

If Node cannot resolve `@oai/artifact-tool`, set `NODE_PATH` to the bundled
Codex runtime `node_modules` path before running the script.

## Verification checklist

After rebuilding:

1. Open `preview/contact-sheet.png` and check the deck reads at thumbnail size.
2. Open any changed `preview/slide-*.png` files and check for clipped text,
   crowded layouts, or unreadable small type.
3. Open the PPTX and confirm text remains editable and speaker notes are present.
4. Do not add invented metrics. Missing final-submission data currently includes
   GitHub/demo URLs, raw test output, live trace artifact, latency/reliability,
   and adoption or time-saved metrics unless those are measured.

