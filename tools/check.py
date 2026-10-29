#!/usr/bin/env python3
"""Render frames of a project into ONE contact sheet so you can SEE the animation. Run it after every change.
  python tools/check.py projects/foo.json [--frames 8] [--out check.png] [--no-joints]
Needs: pip install playwright pillow && playwright install chromium
Also prints load errors and tracks that name joints that don't exist."""
import argparse, asyncio, functools, http.server, io, pathlib, threading
from PIL import Image
from playwright.async_api import async_playwright
root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--frames", type=int, default=8); ap.add_argument("--out", default="check.png"); ap.add_argument("--no-joints", action="store_true")
a = ap.parse_args()
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(root))); threading.Thread(target=srv.serve_forever, daemon=True).start()
rel = pathlib.Path(a.project).resolve().relative_to(root).as_posix()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 480, "height": 1000}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto(f"http://127.0.0.1:{srv.server_port}/index.html?project={rel}")
        try: await pg.wait_for_function("typeof anim!=='undefined'&&anim&&J.length&&img", timeout=15000)
        except Exception: print("PROJECT DID NOT LOAD:", await pg.inner_text("#msg"), errs); await b.close(); return
        await pg.wait_for_timeout(400); print("status:", await pg.inner_text("#msg"))
        print("duration:", await pg.evaluate("anim.duration"), "| joints:", await pg.evaluate("J.map(j=>j.name).join(', ')"))
        await pg.evaluate("playing=false;mode='pose';sel=null;rec=" + ("1" if a.no_joints else "0")); d = await pg.evaluate("anim.duration"); shots = []
        for i in range(a.frames):
            await pg.evaluate(f"evalAnim({i / a.frames * d})"); await pg.wait_for_timeout(120)
            shots.append(Image.open(io.BytesIO(await (await pg.query_selector("#cv")).screenshot())))
        w, h = shots[0].size; cols = min(4, len(shots)); rows = -(-len(shots) // cols); sheet = Image.new("RGB", (w * cols, h * rows), "white")
        for i, s in enumerate(shots): sheet.paste(s, (i % cols * w, i // cols * h))
        sheet.save(a.out); print("wrote", a.out, "| frame i is at t = i/%d*%s s" % (a.frames, d), "| errors:", errs or "none"); await b.close()
asyncio.run(main())
