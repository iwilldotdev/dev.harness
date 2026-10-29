import { spawn, spawnSync } from "node:child_process";
import { createServer } from "node:http";
import { mkdtemp, mkdir, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import assert from "node:assert/strict";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const harness = path.resolve(root, "../..");
const cli = path.join(root, "dist", "cli.js");
const fixture = path.join(root, "fixtures", "page.html");

function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("exit", (status) => resolve({ status, stdout, stderr }));
  });
}

test("pilot UI ticket: capture, compare, and readiness consume the same evidence", async () => {
  const html = await readFile(fixture);
  const server = createServer((_req, res) => {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    res.end(html);
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  const dir = await mkdtemp(path.join(tmpdir(), "visual-pilot-"));
  const repo = path.join(dir, "repo");
  const flow = path.join(repo, ".dev", "features", "pilot");
  const evidence = path.join(flow, "evidence", "visual", "203-13054", "default", "320x180");
  await mkdir(evidence, { recursive: true });
  try {
    const capture = await run(process.execPath, [
      cli, "capture", "--url", `http://127.0.0.1:${port}/`, "--out", evidence,
      "--width", "320", "--height", "180",
    ]);
    assert.equal(capture.status, 0, capture.stderr);
    spawnSync("git", ["init", "-q"], { cwd: repo });
    spawnSync("git", ["config", "user.email", "pilot@example.com"], { cwd: repo });
    spawnSync("git", ["config", "user.name", "Pilot"], { cwd: repo });
    await writeFile(path.join(repo, "app.txt"), "pilot\n");
    spawnSync("git", ["add", "app.txt"], { cwd: repo });
    spawnSync("git", ["-c", "commit.gpgsign=false", "commit", "-q", "-m", "feat: pilot"], { cwd: repo });
    const sha = spawnSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).stdout.trim();
    const revision = "2026-10-29T10:00:00Z";
    const compare = await run(process.execPath, [
      cli, "compare",
      "--figma", path.join(evidence, "app.png"),
      "--app", path.join(evidence, "app.png"),
      "--out", evidence,
      "--entry-id", "REQ-001/203:13054/default/320x180",
      "--git-sha", sha,
      "--figma-revision", revision,
      "--copies", "Pay now",
    ]);
    assert.equal(compare.status, 0, compare.stderr);
    const manifest = {
      schemaVersion: 1,
      unresolved: [],
      entries: [{
        id: "REQ-001/203:13054/default/320x180",
        jiraKey: "DEV-1",
        requirement: "REQ-001",
        fileKey: "abc",
        nodeId: "203:13054",
        state: "default",
        viewport: { width: 320, height: 180 },
        route: "/",
        figmaRevision: revision,
        evidence: "evidence/visual/203-13054/default/320x180/result.json",
      }],
    };
    await writeFile(path.join(flow, "visual-manifest.json"), JSON.stringify(manifest, null, 2));
    await writeFile(path.join(flow, "design.md"), [
      "# Design",
      "",
      "## Visual contract",
      "",
      "| Region | node-id | Facts |",
      "| --- | --- | --- |",
      "| Pilot | 203:13054 | 320x180 |",
      "",
    ].join("\n"));
    await mkdir(path.join(flow, "reviews"), { recursive: true });
    await writeFile(path.join(flow, "reviews", "readiness.md"), [
      "MR verdict: APPROVE",
      "MR open rows: 0",
      `MR reviewed: ${sha}`,
      "QA verdict: APPROVE",
      "QA open rows: 0",
      `QA reviewed: ${sha}`,
      "QA figma-screens: 1/1",
      "",
    ].join("\n"));
    const verify = await run(process.execPath, [cli, "verify-manifest", "--manifest", path.join(flow, "visual-manifest.json"), "--git-sha", sha]);
    assert.equal(verify.status, 0, verify.stderr);
    const readiness = await run("python3", [
      path.join(harness, "skills/dev-shared/scripts/validate_readiness.py"),
      flow,
      "--repo",
      repo,
    ]);
    assert.equal(readiness.status, 0, `${readiness.stdout}\n${readiness.stderr}`);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
