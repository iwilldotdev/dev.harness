import assert from "node:assert/strict";
import test from "node:test";
import { PNG } from "pngjs";
import { comparePng, solidPng } from "../dist/compare.js";

test("identical images pass", () => {
  const png = solidPng(20, 10, [10, 20, 30, 255]);
  const result = comparePng(png, png);
  assert.equal(result.status, "pass");
  assert.equal(result.mismatchedPixels, 0);
});

test("different dimensions fail before pixel comparison", () => {
  const result = comparePng(solidPng(8, 8, [0, 0, 0, 255]), solidPng(9, 8, [0, 0, 0, 255]));
  assert.equal(result.status, "fail");
  assert.equal(result.reason, "dimensions");
});

test("a real region mismatch fails", () => {
  const result = comparePng(solidPng(30, 20, [255, 255, 255, 255]), solidPng(30, 20, [0, 0, 0, 255]));
  assert.equal(result.status, "fail");
  assert.equal(result.reason, "pixel-diff");
});

test("one antialiased pixel stays inside the calibrated limit", () => {
  const image = PNG.sync.read(solidPng(40, 40, [255, 255, 255, 255]));
  image.data[0] = 250;
  const result = comparePng(solidPng(40, 40, [255, 255, 255, 255]), PNG.sync.write(image));
  assert.equal(result.status, "pass");
});

test("a justified small mask can cover a dynamic corner and a full-surface mask cannot", () => {
  const base = PNG.sync.read(solidPng(50, 50, [255, 255, 255, 255]));
  const changed = PNG.sync.read(solidPng(50, 50, [255, 255, 255, 255]));
  for (let y = 0; y < 7; y += 1) {
    for (let x = 0; x < 7; x += 1) changed.data[(y * 50 + x) * 4] = 0;
  }
  const uncovered = comparePng(PNG.sync.write(base), PNG.sync.write(changed));
  assert.equal(uncovered.status, "fail");
  const covered = comparePng(PNG.sync.write(base), PNG.sync.write(changed), {
    masks: [{ x: 0, y: 0, width: 7, height: 7, reason: "clock" }],
  });
  assert.equal(covered.status, "pass");
  const huge = comparePng(solidPng(50, 50, [255, 0, 0, 255]), solidPng(50, 50, [0, 0, 255, 255]), {
    masks: [{ x: 0, y: 0, width: 50, height: 50, reason: "entire surface is not a mask" }],
  });
  assert.equal(huge.reason, "mask-too-large");
});
