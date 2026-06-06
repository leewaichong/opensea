#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DECK_DIR="$ROOT/docs/pitch-deck"
SLIDES_DIR="$DECK_DIR/slides"
OUTPUT_DIR="$DECK_DIR/output"
PREVIEW_DIR="$DECK_DIR/preview"
LAYOUT_DIR="$DECK_DIR/layout/final"
FINAL_PPTX="$OUTPUT_DIR/per-my-last-email-hackathon-pitch.pptx"
CONTACT_SHEET="$PREVIEW_DIR/contact-sheet.png"

DEFAULT_SKILL_DIR="$HOME/.codex/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations"
SKILL_DIR="${CODEX_PRESENTATIONS_SKILL_DIR:-$DEFAULT_SKILL_DIR}"
BUILD_SCRIPT="$SKILL_DIR/scripts/build_artifact_deck.mjs"

if [[ ! -f "$BUILD_SCRIPT" ]]; then
  echo "Cannot find build_artifact_deck.mjs at: $BUILD_SCRIPT" >&2
  echo "Set CODEX_PRESENTATIONS_SKILL_DIR to the installed Presentations skill directory." >&2
  exit 1
fi

BUNDLED_NODE="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
NODE_BIN="${CODEX_NODE_BIN:-node}"
if [[ -x "$BUNDLED_NODE" ]]; then
  NODE_BIN="${CODEX_NODE_BIN:-$BUNDLED_NODE}"
fi

BUNDLED_NODE_MODULES="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
if [[ -d "$BUNDLED_NODE_MODULES" ]]; then
  export NODE_PATH="${NODE_PATH:+$NODE_PATH:}$BUNDLED_NODE_MODULES"
fi

BUNDLED_PYTHON="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
if [[ -z "${PYTHON:-}" && -x "$BUNDLED_PYTHON" ]]; then
  export PYTHON="$BUNDLED_PYTHON"
fi

mkdir -p "$OUTPUT_DIR" "$PREVIEW_DIR" "$LAYOUT_DIR"

"$NODE_BIN" "$BUILD_SCRIPT" \
  --workspace "$DECK_DIR" \
  --slides-dir "$SLIDES_DIR" \
  --out "$FINAL_PPTX" \
  --preview-dir "$PREVIEW_DIR" \
  --layout-dir "$LAYOUT_DIR" \
  --contact-sheet "$CONTACT_SHEET" \
  --slide-count 9 \
  --scale 1

