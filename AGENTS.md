# Agent guide: animate an image with Rigpop

You are given a picture and a request ("make her walk", "make the dragon flap its wings").
Your deliverable is **one project JSON** that the user opens in Rigpop to preview.
Format: `docs/PROJECT_FORMAT.md`. Animation craft and tricks: `docs/ANIMATION_COOKBOOK.md`. Read both first.

Setup (once): `pip install opencv-python pillow numpy playwright && playwright install chromium`

## Workflow. Do every step, in order.
1. **Look at the image.** Note which way the subject faces, what should move, and what hides behind what.
2. **Choose the coordinate space.** Scale so the longest side is 600 to 1000 px (e.g. `"size": [600, 800]`). Origin is top-left, y points down. Every x/y you write lives in this space.
3. **Layers.** If the subject sits on a busy background, split it so only the subject deforms:
   `python tools/cutout.py photo.jpg --size 600x800 --rect x0,y0,x1,y1 --fg "x,y;x,y@30" --out projects/name`
   (trace the head, torso and limbs with `--fg`; add `--poly` for a rough outline). Open both outputs and look; if the cutout leaks or misses parts, add `--fg` lines and re-run. Skip this for plain or transparent backgrounds (then omit `"background"`).
4. **Read coordinates off a grid, never from memory.**
   `python tools/grid.py photo.jpg --size 600x800 --out grid.png`, then open `grid.png` and read each joint's x/y.
5. **Write the joints** (cookbook section 1): root first, parents before children, a joint at every pivot, a leaf joint at every limb tip.
6. **Write the animation** (cookbook sections 3 to 6): keyframes per joint, loop-safe, small and believable.
7. **Verify visually, at least twice.**
   `python tools/check.py projects/name.json --frames 8` writes `check.png`. Open it and LOOK. Fix what you see using the cookbook's symptom table, then re-run.
   Do not hand over a file you have not rendered.
8. **Deliver** `projects/name.json` plus its image files. Tell the user:
   `npx serve .` then open `http://localhost:3000/?project=projects/name.json`, or open `index.html` and use **Open project (.json)**.

## Hard rules
- `rot` is degrees, **positive = clockwise on screen**. A bone pointing down swings its tip LEFT for positive; pointing up, RIGHT; pointing right, DOWN; pointing left, UP.
- `dx` / `dy` only move **root** joints (`parent: null`). Everything else moves by rotation. There is no scale, no skew, no face or eye animation.
- Joint names are unique and used as track keys. Use descriptive names (`thigh_l`, `knee_l`, `tail_2`) because AI models read them.
- Loops: the last keyframe equals the first, and `duration` equals the last `t`.
- Keyframes are interpolated **linearly**. For smooth motion use 8 to 12 keyframes per second; for snappy motion put two keys close together.
- Keep rotations under about 60 degrees per joint and split big turns across a chain. Large single rotations tear the image.
- Nothing fills the gap behind a moving part. Keep motion modest or use the layer split.
- Image paths in the JSON are relative to `index.html`. Remote URLs must allow CORS. Data URIs always work. Opening `index.html` by double-click (`file://`) blocks image paths and `?project=`; serve it over http.

## Definition of done
`check.py` prints no errors and no "no matching joint" warnings, the contact sheet shows the subject intact (no torn limbs, no sliding background), frame 0 looks like the original at rest, and the loop wraps without a jump.
