"""Layout, contrast and animation check for every page.

Each page is loaded in an iframe of an exact width (375 px phone, 1280 px desktop), in light and dark
mode, served over a local http server. The check scrolls the page like a reader so figures animate in
for real, then reports: figures that never appeared, horizontal scroll, text overlaps, things sticking
out of a figure, clipped text, low contrast, tiny text, leftover mermaid.

Usage: python tools/check_pages.py . [page.html ...]   -> prints problems, exit 1 if any.
"""
import functools, http.server, json, pathlib, re, socketserver, subprocess, sys, threading

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = pathlib.Path(sys.argv[1]).resolve()
PAGES = [ROOT / p for p in sys.argv[2:]] or sorted(
    p for p in ROOT.rglob("*.html") if ".git" not in p.parts and not p.name.startswith("_check"))

CHECK = r"""
(async () => {
  const w = window, d = document, sleep = ms => new Promise(r => setTimeout(r, ms));
  const out = { dark: w.matchMedia('(prefers-color-scheme: dark)').matches, w: w.innerWidth, issues: [] };
  const add = (k, m) => out.issues.push(k + ': ' + m);
  // read like a person: scroll down in half-screens
  for (let y = 0; y <= d.documentElement.scrollHeight; y += w.innerHeight / 2) { w.scrollTo(0, y); w.dispatchEvent(new Event('scroll')); await sleep(120); }
  await sleep(300);
  // headless may not run CSS transitions; jump them to their end state before measuring
  const st = d.createElement('style'); st.textContent = '*,*::before,*::after{transition:none!important;animation:none!important}'; d.head.appendChild(st);
  await sleep(50);
  d.querySelectorAll('.fig').forEach((f, fi) => {
    if (d.documentElement.classList.contains('js') && !f.classList.contains('in')) add('fig' + fi, 'never animated in');
    f.querySelectorAll('.flow > li, .vs > div, .stats > div, .timeline > li').forEach(el => {
      if (+getComputedStyle(el).opacity < 0.99) add('fig' + fi, 'item still invisible "' + el.textContent.trim().slice(0, 30) + '"');
    });
  });
  w.scrollTo(0, 0);
  if (d.documentElement.scrollWidth > w.innerWidth + 1) add('page', 'horizontal scroll ' + d.documentElement.scrollWidth + '>' + w.innerWidth);
  const lum = c => { const v = c.match(/[\d.]+/g).slice(0, 3).map(x => { x /= 255; return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; }); return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
  const bgOf = el => { for (; el; el = el.parentElement) { const c = getComputedStyle(el).backgroundColor; const a = c.match(/[\d.]+/g); if (a && (a.length < 4 || +a[3] > .5)) return c; } return 'rgb(255,255,255)'; };
  const name = el => el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : '') + ' "' + el.textContent.trim().slice(0, 30) + '"';
  const main = d.querySelector('main'), mr = main && main.getBoundingClientRect();
  d.querySelectorAll('main *').forEach(el => {  // anything wider than the text column (tables/pre may scroll)
    const r = el.getBoundingClientRect();
    if (r.width && r.right > w.innerWidth + 1 && !el.closest('table, pre')) add('page', 'off screen ' + name(el));
  });
  d.querySelectorAll('.fig').forEach((f, fi) => {
    const fr = f.getBoundingClientRect(), boxes = [];
    f.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width && (r.right > fr.right + 1 || r.left < fr.left - 1)) add('fig' + fi, 'sticks out ' + name(el));
      if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflowX !== 'auto') add('fig' + fi, 'text clipped ' + name(el));
      for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) {
        const rg = d.createRange(); rg.selectNodeContents(n);
        for (const q of rg.getClientRects()) boxes.push({ el, q });
        const cs = getComputedStyle(el), L1 = lum(cs.color), L2 = lum(bgOf(el)), ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
        const big = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.6 && +cs.fontWeight >= 700);
        if (ratio < (big ? 3 : 4.5)) add('fig' + fi, 'low contrast ' + ratio.toFixed(2) + ' ' + name(el));
        if (parseFloat(cs.fontSize) < 12) add('fig' + fi, 'tiny text ' + cs.fontSize + ' ' + name(el));
      }
    });
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      if (boxes[i].el === boxes[j].el) continue;
      const a = boxes[i].q, b = boxes[j].q;
      if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2)
        add('fig' + fi, 'text overlap ' + name(boxes[i].el) + ' x ' + name(boxes[j].el));
    }
  });
  if (d.querySelector('pre.mermaid')) add('page', 'still has mermaid');
  return out;
})()"""

HARNESS = """<!DOCTYPE html><html><body style="margin:0">
<iframe id="f" src="{src}" style="border:0;width:{w}px;height:800px"></iframe>
<pre id="__check"></pre>
<script>
document.getElementById('f').addEventListener('load', async () => {{
  const fw = document.getElementById('f').contentWindow;
  await new Promise(r => setTimeout(r, 400));
  let res; try {{ res = await fw.eval({check}); }} catch (e) {{ res = {{ issues: ['harness error ' + e] }}; }}
  document.getElementById('__check').textContent = JSON.stringify(res);
}});
</script></body></html>"""

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
PROFILE = __import__("tempfile").mkdtemp(prefix="checkpages_")  # own Chrome profile, so parallel runs don't clash
harness = ROOT / f"_check_harness_{__import__('os').getpid()}.html"
bad = 0
try:
    for page in PAGES:
        rel = page.relative_to(ROOT).as_posix()
        for w in (375, 1280):
            harness.write_text(HARNESS.format(src="/" + rel, w=w, check=json.dumps(CHECK)), encoding="utf8")
            for mode in ("light", "dark"):
                flag = "--force-dark-mode" if mode == "dark" else "--blink-settings=preferredColorScheme=1"
                dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--window-size=1400,900", f"--user-data-dir={PROFILE}", "--virtual-time-budget=30000",
                                      flag, "--dump-dom", f"http://127.0.0.1:{port}/{harness.name}"],
                                     capture_output=True, text=True, encoding="utf8").stdout
                m = re.search(r'<pre id="__check">(.*?)</pre>', dom, re.S)
                raw = m.group(1) if m else ""
                for a, b in (("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")):
                    raw = raw.replace(a, b)
                res = json.loads(raw) if raw.strip() else {"issues": ["no result"]}
                if "w" in res and res["w"] != w:
                    res["issues"].append(f"viewport was {res['w']}px, not {w}")
                if res.get("dark") is not None and res["dark"] != (mode == "dark"):
                    res["issues"].append(f"mode not applied (asked {mode})")
                for i in dict.fromkeys(res["issues"]):
                    bad += 1
                    print(f"{rel} [{w}px {mode}] {i}")
finally:
    harness.unlink(missing_ok=True)
    srv.shutdown()
    __import__("shutil").rmtree(PROFILE, ignore_errors=True)
print("OK, no issues" if not bad else f"{bad} issue(s)")
sys.exit(1 if bad else 0)
