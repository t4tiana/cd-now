/** Export the investment committee memo as a paginated PDF. */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const root = path.resolve(import.meta.dirname, "..");
const nodeModules = [
  path.join(root, "node_modules"),
  process.env.CODEX_RUNTIME_NODE_MODULES,
  path.join(os.homedir(), ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules"),
].find((candidate) => candidate && fs.existsSync(path.join(candidate, "marked")) && fs.existsSync(path.join(candidate, "playwright")));
if (!nodeModules) throw new Error("marked and playwright are required to export this PDF");
const { marked } = require(path.join(nodeModules, "marked"));
const { chromium } = require(path.join(nodeModules, "playwright"));

const deliverables = path.join(root, "final_deliverables");
const source = path.join(deliverables, "investment_committee_memo.md");
const output = path.join(deliverables, "investment_committee_memo.pdf");
const markdown = fs.readFileSync(source, "utf8");

let body = marked.parse(markdown, { gfm: true });
body = body.replace(/<img\s+([^>]*?)src="([^"]+\.svg)"([^>]*?)>/g, (_match, before, name, after) => {
  const svg = fs.readFileSync(path.join(deliverables, name), "utf8");
  const encoded = Buffer.from(svg).toString("base64");
  return `<img ${before}src="data:image/svg+xml;base64,${encoded}"${after}>`;
});

const base = pathToFileURL(`${deliverables}${path.sep}`).href;
const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><base href="${base}">
<style>
  @page { size: letter; margin: 0.55in 0.62in 0.6in; }
  * { box-sizing: border-box; }
  html { color: #1b2638; font-family: Arial, Helvetica, sans-serif; font-size: 9.2pt; }
  body { margin: 0; line-height: 1.3; }
  h1, h2 { color: #17253d; break-after: avoid; }
  h1 { font-size: 19pt; line-height: 1.15; margin: 0 0 11pt; }
  h2 { font-size: 12.4pt; border-bottom: 1px solid #d8e1e9; padding-bottom: 3pt;
       margin: 14.5pt 0 6pt; }
  p { margin: 0 0 6.5pt; orphans: 3; widows: 3; break-inside: avoid; }
  h1 + p { color: #475569; }
  strong { color: #14233a; }
  a { color: #1d6287; text-decoration: none; }
  img { display: block; width: 100%; max-width: 100%; height: auto; }
  img[alt^="Observed percentage"] { width: 90%; margin: 0 auto; }
  p:has(> img) { break-inside: avoid; break-after: avoid; margin: 9pt 0 3pt; }
  p:has(> img) + p { break-before: avoid; font-size: 8.3pt; color: #475569; }
  table { width: 100%; border-collapse: collapse; font-size: 8.4pt;
          margin: 8pt 0 11pt; break-inside: avoid; }
  thead { display: table-header-group; }
  th, td { padding: 5pt 5.5pt; border-bottom: 1px solid #dce4eb; vertical-align: top; }
  th { background: #eaf1f6; color: #17253d; text-align: left; }
  td[align="right"], th[align="right"] { text-align: right; }
  tr { break-inside: avoid; }
  ol { padding-left: 17pt; margin: 5pt 0 9pt; }
  li { margin: 0 0 5pt; padding-left: 2pt; }
  li p { margin: 0; }
  em { color: #3e4f62; }
</style></head><body>${body}</body></html>`;

fs.mkdirSync(path.dirname(output), { recursive: true });
const executablePath = [
  process.env.MEMO_PDF_BROWSER,
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
].find((candidate) => candidate && fs.existsSync(candidate));
const browser = await chromium.launch({
  ...(executablePath ? { executablePath } : {}),
  headless: true,
  args: ["--no-sandbox", "--disable-gpu"],
});
try {
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: "load" });
  await page.pdf({
    path: output,
    format: "Letter",
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: "<span></span>",
    footerTemplate: `<div style="font:8px Arial;color:#64748b;width:100%;margin:0 0.66in;display:flex;justify-content:space-between;"><span>CDNow investment committee memo</span><span><span class="pageNumber"></span></span></div>`,
  });
} finally {
  await browser.close();
}
process.stdout.write(`${output}\n`);
