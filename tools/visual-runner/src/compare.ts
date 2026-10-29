import pixelmatch from "pixelmatch";
import { PNG } from "pngjs";

export type Mask = {
  x: number;
  y: number;
  width: number;
  height: number;
  reason: string;
};

export type CompareResult = {
  status: "pass" | "fail";
  reason?: string;
  width?: number;
  height?: number;
  mismatchedPixels?: number;
  diffRatio?: number;
  diffPng?: Buffer;
};

const MAX_MASK_RATIO = 0.02;

export function comparePng(
  figma: Buffer,
  app: Buffer,
  options: { maxDiffRatio?: number; masks?: Mask[] } = {},
): CompareResult {
  const left = PNG.sync.read(figma);
  const right = PNG.sync.read(app);
  if (left.width !== right.width || left.height !== right.height) {
    return {
      status: "fail",
      reason: "dimensions",
      width: right.width,
      height: right.height,
    };
  }
  const masks = options.masks ?? [];
  if (masks.some((mask) => !mask.reason.trim())) {
    return { status: "fail", reason: "mask-without-reason", width: left.width, height: left.height };
  }
  const area = left.width * left.height;
  const maskArea = masks.reduce((sum, mask) => sum + mask.width * mask.height, 0);
  if (maskArea > area * MAX_MASK_RATIO) {
    return { status: "fail", reason: "mask-too-large", width: left.width, height: left.height };
  }
  for (const mask of masks) applyMask(left, mask);
  for (const mask of masks) applyMask(right, mask);
  const diff = new PNG({ width: left.width, height: left.height });
  const mismatchedPixels = pixelmatch(left.data, right.data, diff.data, left.width, left.height, {
    threshold: 0.1,
  });
  const diffRatio = area === 0 ? 1 : mismatchedPixels / area;
  const limit = options.maxDiffRatio ?? 0.002;
  return {
    status: diffRatio <= limit ? "pass" : "fail",
    reason: diffRatio <= limit ? undefined : "pixel-diff",
    width: left.width,
    height: left.height,
    mismatchedPixels,
    diffRatio,
    diffPng: PNG.sync.write(diff),
  };
}

function applyMask(png: PNG, mask: Mask): void {
  for (let y = mask.y; y < mask.y + mask.height; y += 1) {
    for (let x = mask.x; x < mask.x + mask.width; x += 1) {
      if (x < 0 || y < 0 || x >= png.width || y >= png.height) continue;
      const offset = (png.width * y + x) << 2;
      png.data[offset] = 0;
      png.data[offset + 1] = 0;
      png.data[offset + 2] = 0;
      png.data[offset + 3] = 255;
    }
  }
}

export function solidPng(width: number, height: number, rgba: [number, number, number, number]): Buffer {
  const png = new PNG({ width, height });
  for (let index = 0; index < width * height; index += 1) {
    png.data[index * 4] = rgba[0];
    png.data[index * 4 + 1] = rgba[1];
    png.data[index * 4 + 2] = rgba[2];
    png.data[index * 4 + 3] = rgba[3];
  }
  return PNG.sync.write(png);
}
