import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium, type Page } from "playwright";

export type AdapterAction =
  | { type: "goto"; path: string }
  | { type: "click"; selector: string }
  | { type: "fill"; selector: string; value: string }
  | { type: "wait"; selector: string };

const ALLOWED = new Set(["goto", "click", "fill", "wait"]);

export async function captureSurface(options: {
  url: string;
  outDir: string;
  width: number;
  height: number;
  selector?: string;
  adapterPath?: string;
  storageState?: string;
}): Promise<{ appPng: string; text: string }> {
  await mkdir(options.outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({
      viewport: { width: options.width, height: options.height },
      deviceScaleFactor: 1,
      locale: "en-US",
      timezoneId: "UTC",
      colorScheme: "light",
      reducedMotion: "reduce",
      storageState: options.storageState,
    });
    const page = await context.newPage();
    await page.emulateMedia({ reducedMotion: "reduce", colorScheme: "light" });
    await page.goto(options.url, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.addStyleTag({
      content:
        "*,*::before,*::after{animation:none !important;transition:none !important;caret-color:transparent !important}",
    });
    if (options.adapterPath) await runAdapter(page, options.adapterPath, options.url);
    const target = options.selector ? page.locator(options.selector) : page;
    const appPng = path.join(options.outDir, "app.png");
    await target.screenshot({ path: appPng, animations: "disabled", caret: "hide" });
    const text = options.selector
      ? await page.locator(options.selector).innerText()
      : await page.locator("body").innerText();
    await writeFile(path.join(options.outDir, "text.txt"), text, "utf8");
    return { appPng, text };
  } finally {
    await browser.close();
  }
}

async function runAdapter(page: Page, adapterPath: string, baseUrl: string): Promise<void> {
  const payload = JSON.parse(await readFile(adapterPath, "utf8")) as { actions?: AdapterAction[] };
  for (const action of payload.actions ?? []) {
    if (!action || !ALLOWED.has(action.type)) {
      throw new Error(`adapter action is not allowed: ${JSON.stringify(action)}`);
    }
    if (action.type === "goto") {
      const next = new URL(action.path, baseUrl);
      if (next.origin !== new URL(baseUrl).origin) throw new Error("adapter goto cannot leave the app origin");
      await page.goto(next.toString(), { waitUntil: "load" });
    } else if (action.type === "click") {
      await page.locator(action.selector).click();
    } else if (action.type === "fill") {
      await page.locator(action.selector).fill(action.value);
    } else if (action.type === "wait") {
      await page.locator(action.selector).waitFor();
    }
  }
}
