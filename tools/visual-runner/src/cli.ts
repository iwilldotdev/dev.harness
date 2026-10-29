import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { captureSurface } from "./capture.js";
import { comparePng, type Mask } from "./compare.js";

type Command = "capture" | "compare" | "verify-manifest";

const args = process.argv.slice(2);
const command = args[0] as Command | undefined;

main().catch((err: unknown) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});

async function main(): Promise<void> {
  if (command === "capture") {
    const captured = await captureSurface({
      url: required("--url"),
      outDir: required("--out"),
      width: numberArg("--width"),
      height: numberArg("--height"),
      selector: optional("--selector"),
      adapterPath: optional("--adapter"),
      storageState: optional("--storage-state"),
    });
    console.log(captured.appPng);
    return;
  }
  if (command === "compare") {
    const outDir = required("--out");
    await mkdir(outDir, { recursive: true });
    const figma = await readFile(required("--figma"));
    const app = await readFile(required("--app"));
    const copies = optional("--copies")?.split("|").filter(Boolean) ?? [];
    if (copies.length) {
      const text = await readFile(path.join(path.dirname(required("--app")), "text.txt"), "utf8").catch(() => "");
      const missing = copies.filter((copy) => !text.includes(copy));
      if (missing.length) {
        await writeResult(outDir, { status: "fail", reason: "copy", missing });
        process.exitCode = 1;
        return;
      }
    }
    const masks = optional("--masks") ? (JSON.parse(await readFile(optional("--masks") as string, "utf8")) as Mask[]) : [];
    const compared = comparePng(figma, app, { maxDiffRatio: optionalNumber("--max-diff-ratio"), masks });
    if (compared.diffPng) await writeFile(path.join(outDir, "diff.png"), compared.diffPng);
    await copyDistinct(required("--figma"), path.join(outDir, "figma.png"));
    await copyDistinct(required("--app"), path.join(outDir, "app.png"));
    await writeResult(outDir, {
      schemaVersion: 1,
      status: compared.status,
      reason: compared.reason,
      entryId: required("--entry-id"),
      gitSha: required("--git-sha"),
      figmaRevision: required("--figma-revision"),
      width: compared.width,
      height: compared.height,
      mismatchedPixels: compared.mismatchedPixels,
      diffRatio: compared.diffRatio,
    });
    if (compared.status !== "pass") process.exitCode = 1;
    return;
  }
  if (command === "verify-manifest") {
    const manifestPath = required("--manifest");
    const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as {
      schemaVersion?: number;
      entries?: Array<{ id: string; evidence: string; figmaRevision: string }>;
    };
    if (manifest.schemaVersion !== 1) throw new Error("visual-manifest schemaVersion must be 1");
    const root = path.dirname(manifestPath);
    const errors: string[] = [];
    for (const entry of manifest.entries ?? []) {
      const resultPath = path.join(root, entry.evidence);
      const result = JSON.parse(await readFile(resultPath, "utf8")) as {
        status?: string;
        entryId?: string;
        gitSha?: string;
        figmaRevision?: string;
      };
      if (result.status !== "pass") errors.push(`${entry.id}: status ${result.status}`);
      if (result.entryId !== entry.id) errors.push(`${entry.id}: entryId mismatch`);
      if (result.figmaRevision !== entry.figmaRevision) errors.push(`${entry.id}: stale figma revision`);
      if (optional("--git-sha") && result.gitSha !== optional("--git-sha")) errors.push(`${entry.id}: gitSha mismatch`);
    }
    if (errors.length) {
      console.error(errors.join("\n"));
      process.exitCode = 1;
      return;
    }
    console.log("OK");
    return;
  }
  throw new Error("usage: visual-runner capture|compare|verify-manifest");
}

async function copyDistinct(from: string, to: string): Promise<void> {
  if (path.resolve(from) !== path.resolve(to)) await copyFile(from, to);
}

async function writeResult(outDir: string, result: Record<string, unknown>): Promise<void> {
  await writeFile(path.join(outDir, "result.json"), `${JSON.stringify(result, null, 2)}\n`, "utf8");
}

function required(name: string): string {
  const value = optional(name);
  if (!value) throw new Error(`missing ${name}`);
  return value;
}

function optional(name: string): string | undefined {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
}

function numberArg(name: string): number {
  const value = Number(required(name));
  if (!Number.isFinite(value) || value <= 0) throw new Error(`${name} must be a positive number`);
  return value;
}

function optionalNumber(name: string): number | undefined {
  const value = optional(name);
  return value === undefined ? undefined : Number(value);
}
