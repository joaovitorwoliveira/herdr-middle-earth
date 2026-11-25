// Run with: node --test tests/themes.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { inflateSync } from "node:zlib";

const ROOT = new URL("../", import.meta.url);
const json = (path) => JSON.parse(readFileSync(new URL(path, ROOT), "utf8"));
const THEMES = { light: json("themes/shire.json"), dark: json("themes/mordor.json") };
const LAYOUT = json("layouts/middle-earth.json");
const SURFACES = ["chrome", "canvas", "popover", "selected"];
const TEXT = 4.5; // WCAG AA, body text
const SECONDARY = 3; // WCAG AA, large text and non-text UI: dim labels, accents
// The backdrop's brightest dots may pass under a word; the glow itself may not.
const SPECKS = 0.01;
const BACKDROP_SIZE = [2400, 1400];

const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));

function luminance(color) {
  const [r, g, b] = color.map((c) => c / 255).map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a, b) {
  const [low, high] = [luminance(a), luminance(b)].sort((x, y) => x - y);
  return (high + 0.05) / (low + 0.05);
}

// The pixels of an 8-bit RGB PNG, as tools/halftone.py writes them.
function pixels(path) {
  const png = readFileSync(new URL(path, ROOT));
  const [width, height, depth, type] = [png.readUInt32BE(16), png.readUInt32BE(20), png[24], png[25]];
  assert.deepEqual([depth, type], [8, 2], `${path}: expected 8-bit RGB`);
  const data = [];
  for (let at = 8; at < png.length; at += 12 + png.readUInt32BE(at)) {
    if (png.toString("ascii", at + 4, at + 8) === "IDAT") data.push(png.subarray(at + 8, at + 8 + png.readUInt32BE(at)));
  }
  const raw = inflateSync(Buffer.concat(data));
  const stride = width * 3;
  const out = Buffer.alloc(height * stride);
  for (let y = 0; y < height; y++) {
    const filter = raw[y * (stride + 1)];
    for (let x = 0; x < stride; x++) {
      const a = x >= 3 ? out[y * stride + x - 3] : 0;
      const b = y ? out[(y - 1) * stride + x] : 0;
      const c = x >= 3 && y ? out[(y - 1) * stride + x - 3] : 0;
      const p = a + b - c;
      const paeth = Math.abs(p - a) <= Math.abs(p - b) && Math.abs(p - a) <= Math.abs(p - c) ? a : Math.abs(p - b) <= Math.abs(p - c) ? b : c;
      const predictor = [0, a, b, (a + b) >> 1, paeth][filter];
      out[y * stride + x] = (raw[y * (stride + 1) + 1 + x] + predictor) & 255;
    }
  }
  const list = [];
  for (let i = 0; i < out.length; i += 3) list.push([out[i], out[i + 1], out[i + 2]]);
  return { width, height, list };
}

for (const [appearance, t] of Object.entries(THEMES)) {
  test(`${appearance}: text reads on every panel`, () => {
    for (const surface of SURFACES) {
      const on = rgb(t.colors[surface]);
      for (const role of ["foreground", "muted"]) {
        const ratio = contrast(rgb(t[role] ?? t.colors[role]), on);
        assert.ok(ratio >= TEXT, `${role} on ${surface}: ${ratio.toFixed(2)}:1`);
      }
      for (const role of ["dim", "accent"]) {
        const ratio = contrast(rgb(t.colors[role]), on);
        assert.ok(ratio >= SECONDARY, `${role} on ${surface}: ${ratio.toFixed(2)}:1`);
      }
    }
  });

  test(`${appearance}: terminal text reads over the backdrop`, () => {
    const opacity = LAYOUT.terminal_opacity;
    const bg = rgb(t.background);
    const fg = rgb(t.foreground);
    const path = `backgrounds/middle-earth/${appearance}.png`;
    const { width, height, list } = pixels(path);
    assert.deepEqual([width, height], BACKDROP_SIZE, path);
    const seen = new Map();
    const ratios = list.map((px) => {
      const key = px.join();
      if (!seen.has(key)) seen.set(key, contrast(fg, bg.map((c, i) => opacity * c + (1 - opacity) * px[i])));
      return seen.get(key);
    }).sort((a, b) => a - b);
    const ratio = ratios[Math.floor(ratios.length * SPECKS)];
    assert.ok(ratio >= TEXT, `${path}: ${ratio.toFixed(2)}:1`);
  });
}
