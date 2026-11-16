// 슬라이드 한 장을 Figma에서 편집할 수 있는 SVG로 뽑는다.
//   node tools/export-figma.mjs 15            → figma/unit01-slide15.svg
//   node tools/export-figma.mjs 15 day02      → figma/day02-slide15.svg
// 브라우저(Chrome)로 실제 렌더링한 뒤, 상자는 <rect>, 글자는 줄마다 <text>로 옮긴다.
// Figma는 <foreignObject>(HTML)를 읽지 못하므로 이렇게 풀어서 써야 글자를 고칠 수 있다.
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const [num = "1", day = "unit01"] = process.argv.slice(2);
const url = pathToFileURL(join(ROOT, "dist", "slides", day + ".html")).href + "#" + num;
const out = join(ROOT, "figma", `${day}-slide${num}.svg`);
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9334;

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, "--window-size=1400,900",
  "--user-data-dir=" + join(process.env.TMPDIR || "/tmp", "figma-export-profile"), "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms));

// 페이지 안에서 실행할 변환 코드
function toSvg() {
  const deck = document.querySelector(".deck");
  deck.style.transform = "none";                       // 화면 맞춤 배율을 풀어 1280×720 좌표 그대로 쓴다
  const sl = document.querySelector(".slide.active");
  const B = sl.getBoundingClientRect();
  const parts = [];
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const n = v => Math.round(v * 100) / 100;
  const visible = c => c && c !== "transparent" && !/rgba\(.*,\s*0\)$/.test(c);
  const fontOf = cs => /mono|Consolas|D2Coding|Menlo/i.test(cs.fontFamily) ? "JetBrains Mono, D2Coding, monospace" : "Pretendard, Apple SD Gothic Neo, sans-serif";

  function box(el, cs) {
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    const x = r.left - B.left, y = r.top - B.top, rad = parseFloat(cs.borderTopLeftRadius) || 0;
    if (visible(cs.backgroundColor))
      parts.push(`<rect x="${n(x)}" y="${n(y)}" width="${n(r.width)}" height="${n(r.height)}" rx="${n(rad)}" fill="${cs.backgroundColor}"/>`);
    const sides = ["Top", "Right", "Bottom", "Left"].map(s => ({ s, w: parseFloat(cs["border" + s + "Width"]), c: cs["border" + s + "Color"], st: cs["border" + s + "Style"] }));
    const on = sides.filter(d => d.w > 0 && d.st !== "none" && visible(d.c));
    if (!on.length) return;
    if (on.length === 4 && on.every(d => d.w === on[0].w && d.c === on[0].c)) {
      const w = on[0].w, dash = on[0].st === "dashed" ? ` stroke-dasharray="${w * 4} ${w * 3}"` : "";
      parts.push(`<rect x="${n(x + w / 2)}" y="${n(y + w / 2)}" width="${n(r.width - w)}" height="${n(r.height - w)}" rx="${n(rad)}" fill="none" stroke="${on[0].c}" stroke-width="${w}"${dash}/>`);
    } else {
      for (const d of on) {
        const g = { Top: [x, y, r.width, d.w], Bottom: [x, y + r.height - d.w, r.width, d.w], Left: [x, y, d.w, r.height], Right: [x + r.width - d.w, y, d.w, r.height] }[d.s];
        parts.push(`<rect x="${n(g[0])}" y="${n(g[1])}" width="${n(g[2])}" height="${n(g[3])}" fill="${d.c}"/>`);
      }
    }
  }

  // 형광펜(굵은 글씨 밑 라임 띠)
  function highlight(el, cs) {
    if (!/gradient/.test(cs.backgroundImage)) return;
    const color = (cs.backgroundImage.match(/rgb[a]?\([^)]*\)/g) || []).find(c => !/,\s*0\)$/.test(c)) || "#C9D863";
    for (const r of el.getClientRects())
      parts.push(`<rect x="${n(r.left - B.left)}" y="${n(r.top - B.top + r.height * 0.55)}" width="${n(r.width)}" height="${n(r.height * 0.37)}" fill="${color}"/>`);
  }

  // 글자: 한 글자씩 위치를 재서 같은 줄끼리 묶는다(줄바꿈이 브라우저와 똑같이 나온다).
  function text(node, cs) {
    const s = node.textContent;
    if (!s.trim()) return;
    const range = document.createRange(), lines = [];
    for (let i = 0; i < s.length; i++) {
      range.setStart(node, i); range.setEnd(node, i + 1);
      const r = range.getClientRects()[0];
      if (!r) continue;
      let line = lines.find(l => Math.abs(l.top - r.top) < r.height / 2);
      if (!line) lines.push(line = { top: r.top, left: r.left, h: r.height, str: "" });
      line.str += s[i];
    }
    const scale = sl.getBoundingClientRect().width / sl.offsetWidth;          // 1
    const fit = parseFloat(sl.getAttribute("data-scale") || "1");
    const inFit = node.parentElement.closest(".s-fit");
    const size = parseFloat(cs.fontSize) * (inFit ? fit : 1) * scale;
    for (const l of lines) {
      const str = l.str.replace(/\s+$/, "");
      if (!str.trim()) continue;
      const lead = l.str.length - l.str.trimStart().length;
      const x = l.left - B.left, base = l.top - B.top + l.h * 0.8;
      parts.push(`<text x="${n(x)}" y="${n(base)}" font-family="${fontOf(cs)}" font-size="${n(size)}" font-weight="${cs.fontWeight}" fill="${cs.color}" xml:space="preserve">${esc(str.slice(lead) ? str : str)}</text>`);
    }
  }

  function marker(li, cs) {
    const p = li.parentElement;
    if (!p || !/^(UL|OL)$/.test(p.tagName) || cs.listStyleType === "none" || getComputedStyle(p).listStyleType === "none") return;
    const r = li.getClientRects()[0];
    if (!r) return;
    const fit = parseFloat(sl.getAttribute("data-scale") || "1");
    const size = parseFloat(cs.fontSize) * (li.closest(".s-fit") ? fit : 1);
    const label = p.tagName === "OL" ? (Array.prototype.indexOf.call(p.children, li) + 1) + "." : "•";
    const lineH = parseFloat(cs.lineHeight) * (li.closest(".s-fit") ? fit : 1) || size * 1.6;
    parts.push(`<text x="${n(r.left - B.left - size * 1.1)}" y="${n(r.top - B.top + (lineH + size * 0.7) / 2)}" font-family="${fontOf(cs)}" font-size="${n(size)}" fill="${cs.color}">${label}</text>`);
  }

  function walk(el) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") return;
    if (el.tagName === "BUTTON" || el.tagName === "SCRIPT") return;
    if (el.tagName === "svg") {                       // Mermaid 그림은 그대로 넣는다
      const r = el.getBoundingClientRect();
      const c = el.cloneNode(true);
      c.setAttribute("x", n(r.left - B.left)); c.setAttribute("y", n(r.top - B.top));
      c.setAttribute("width", n(r.width)); c.setAttribute("height", n(r.height));
      c.removeAttribute("style");
      parts.push(new XMLSerializer().serializeToString(c));
      return;
    }
    box(el, cs);
    highlight(el, cs);
    if (el.tagName === "LI") marker(el, cs);
    for (const ch of el.childNodes) {
      if (ch.nodeType === 3) text(ch, cs);
      else if (ch.nodeType === 1) walk(ch);
    }
  }
  walk(sl);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">\n` + parts.join("\n") + `\n</svg>\n`;
}

let ws;
for (let i = 0; i < 40 && !ws; i++) {
  try {
    const page = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).find(t => t.type === "page");
    if (page) ws = new WebSocket(page.webSocketDebuggerUrl);
  } catch { /* 아직 크롬이 뜨는 중 */ }
  if (!ws) await sleep(250);
}
await new Promise(r => (ws.onopen = r));
let id = 0;
const pending = {};
ws.onmessage = e => { const m = JSON.parse(e.data); if (pending[m.id]) { pending[m.id](m); delete pending[m.id]; } };
const send = (method, params = {}) => new Promise(r => { pending[++id] = r; ws.send(JSON.stringify({ id, method, params })); });

try {
  await send("Page.enable");
  await send("Page.navigate", { url });
  await sleep(4000);                                   // 웹폰트·Mermaid 그리기 기다림
  const res = await send("Runtime.evaluate", { expression: `(${toSvg})()`, returnByValue: true });
  if (res.result.exceptionDetails) throw new Error(res.result.exceptionDetails.exception.description);
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, res.result.result.value);
  console.log("saved", out);
} finally {
  ws.close();
  chrome.kill();
}
