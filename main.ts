#!/usr/bin/env node
/**
 * Tuesday 24 November 2026 — The World in One Page
 *
 * make.fun bounty "news-image-20261124": sum up 24 November's world news
 * in one image. The image is entry.png, drawn by tools/render.py
 * (Python + Pillow, original flat vector art, no photographs). This
 * program is the entrypoint the harness runs: it places entry.png at
 * $MAKEFUN_OUTPUT_DIR/entry.png.
 *
 * Node 22, standard library only. No network, no dependencies.
 * The copy is byte-for-byte, so repeated runs write identical bytes.
 */

import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const source = join(here, "entry.png");
const target = join(outDir, "entry.png");

if (!existsSync(source)) {
  console.error("entry.png is missing; render it first with: python3 tools/render.py");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);
console.log(`wrote ${target} — Tuesday 24 November 2026 — The World in One Page`);
