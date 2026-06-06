import fs from "node:fs";
import { fileURLToPath } from "node:url";

export const C = {
  ink: "#181818",
  paper: "#FFFFFF",
  white: "#FFFFFF",
  fog: "#F9F9F9",
  linen: "#F3F3F3",
  line: "#EDEDED",
  muted: "#5D605E",
  graphite: "#282828",
  smoke: "#8F8F8F",
  blueSoft: "#DDEBFF",
  blue: "#336CFF",
  codexDeep: "#2636B8",
  codexViolet: "#6547F5",
  green: "#282828",
  red: "#282828",
  amber: "#282828",
  amberSoft: "#F3F3F3",
  greenSoft: "#F9F9F9",
  redSoft: "#FFFFFF",
  darkPanel: "#17191A",
};

export function setup(slide, notes, mode = "light") {
  slide.background.fill = mode === "blue" ? C.codexDeep : C.paper;
  if (mode === "blue") {
    addImageBackground(slide, "dark");
  } else if (mode === "soft") {
    addImageBackground(slide, "soft");
  }
  if (notes) slide.speakerNotes.setText(notes);
}

function readImageBlob(relativePath) {
  const imagePath = fileURLToPath(new URL(relativePath, import.meta.url));
  const bytes = fs.readFileSync(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

export function addImageBackground(slide, variant = "dark") {
  const rel = variant === "soft" ? "../assets/codex-gradient-soft.png" : "../assets/codex-gradient-dark.png";
  const image = slide.images.add({
    blob: readImageBlob(rel),
    fit: "cover",
    alt: variant === "soft" ? "Soft Codex blue white gradient background" : "Codex blue violet gradient background",
    name: `codex-${variant}-background`,
  });
  image.position = { left: 0, top: 0, width: 1280, height: 720 };
  return image;
}

export function addImageAsset(slide, relativePath, x, y, w, h, alt, name) {
  const image = slide.images.add({
    blob: readImageBlob(relativePath),
    fit: "cover",
    alt,
    name,
  });
  image.position = { left: x, top: y, width: w, height: h };
  return image;
}

export function addText(slide, text, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: w, height: h },
    fill: options.fill || "none",
    line: { fill: options.line || "none", width: options.lineWidth || 0 },
    borderRadius: options.radius || 0,
  });
  shape.text.set(text);
  shape.text.typeface = options.font || "Inter";
  shape.text.fontSize = options.size || 20;
  shape.text.color = options.color || C.ink;
  shape.text.insets = options.insets || { top: 4, right: 4, bottom: 4, left: 4 };
  shape.text.wrap = "square";
  shape.text.autoFit = options.autoFit || "none";
  if (options.bold) shape.text.bold = true;
  if (options.align) shape.text.alignment = options.align;
  if (options.valign) shape.text.verticalAlignment = options.valign;
  return shape;
}

export function addBox(slide, x, y, w, h, fill = C.white, line = C.line, radius = 6) {
  return slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { fill: line, width: line === "none" ? 0 : 1 },
    borderRadius: radius,
  });
}

export function addRule(slide, x, y, w, color = C.line, width = 1) {
  slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: w, height: width },
    fill: color,
    line: { fill: "none", width: 0 },
  });
}

export function addKicker(slide, kicker, title, source, page, mode = "light") {
  const inverse = mode === "blue";
  addText(slide, kicker.toUpperCase(), 72, 44, 300, 24, {
    size: 13,
    color: inverse ? "#EAF2FF" : C.muted,
    bold: true,
    insets: { top: 2, right: 0, bottom: 0, left: 0 },
  });
  addText(slide, title, 70, 76, 920, 112, {
    size: 40,
    color: inverse ? C.white : C.ink,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  if (source) {
    addText(slide, source, 72, 684, 760, 18, {
      size: 10,
      color: inverse ? "#DCE7FF" : C.muted,
      insets: { top: 0, right: 0, bottom: 0, left: 0 },
    });
  }
  if (page) {
    addText(slide, String(page).padStart(2, "0"), 1180, 684, 40, 18, {
      size: 10,
      color: inverse ? "#DCE7FF" : C.muted,
      align: "right",
      insets: { top: 0, right: 0, bottom: 0, left: 0 },
    });
  }
}

export function addPill(slide, label, x, y, w, color, fill) {
  addBox(slide, x, y, w, 34, fill, color, 17);
  addText(slide, label, x + 12, y + 7, w - 24, 18, {
    size: 12,
    color,
    bold: true,
    align: "center",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
}

export function addArrow(slide, x, y, w, color = C.line) {
  slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y + 4, width: w - 12, height: 2 },
    fill: color,
    line: { fill: "none", width: 0 },
  });
  slide.shapes.add({
    geometry: "triangle",
    position: { left: x + w - 14, top: y, width: 14, height: 10 },
    fill: color,
    line: { fill: "none", width: 0 },
  });
}

export function agendaTile(slide, x, y, w, h, label, status, detail = "") {
  const map = {
    agreed: [C.fog, C.line, "CLEARED"],
    crux: [C.white, C.graphite, "CRUX"],
    fake: [C.linen, C.graphite, "FAKE AGREEMENT"],
    open: [C.white, C.line, "OPEN"],
  };
  const [fill, color, tag] = map[status];
  addBox(slide, x, y, w, h, fill, color, 7);
  addText(slide, tag, x + 14, y + 12, w - 28, 16, {
    size: 10,
    color: status === "agreed" ? C.muted : C.graphite,
    bold: true,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  addText(slide, label, x + 14, y + 34, w - 28, 44, {
    size: 17,
    color: C.ink,
    bold: status !== "agreed",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  if (detail) {
    addText(slide, detail, x + 14, y + h - 30, w - 28, 18, {
      size: 11,
      color: C.muted,
      insets: { top: 0, right: 0, bottom: 0, left: 0 },
    });
  }
}
