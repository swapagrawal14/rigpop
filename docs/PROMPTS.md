# Prompts

## A. Paste this to any coding agent (with the repo open and your image attached)
```
Read AGENTS.md, docs/PROJECT_FORMAT.md and docs/ANIMATION_COOKBOOK.md in this repo first.
Then animate my attached image: <WHAT YOU WANT, e.g. "she walks in place, looking at the camera, backpack bouncing slightly">.
Subject faces: <left/right/camera>. Style: <subtle / natural / exaggerated>. Loop length: about <N> seconds.
Follow the workflow in AGENTS.md exactly: cut out the subject if the background is busy, read joint coordinates from a grid image,
write projects/<name>.json, run tools/check.py, look at check.png, fix problems, and repeat until it is clean.
Show me the final check.png and tell me the command to preview it.
```

## B. Make the request specific (this is what separates good from mediocre results)
- **Name the motion as beats with times**: "0 to 0.4 s raise right arm, 0.4 to 2 s wave, 2 to 2.4 s lower".
- **Say which way the subject faces** and which limbs are visible.
- **Give an intensity**: subtle (rot under 10), natural (10 to 30), exaggerated (30 to 60).
- **Ask for a loop** and a length, or say "one shot, no loop".
- **Say what must stay still** ("keep the background and feet planted").
- **Ask for variants**: "also export a subtle and an exaggerated version".
- **Insist on verification**: "do not stop until check.png shows no tearing".
- **Name the principles**: "use follow-through on hair and backpack, anticipation before the step".

## C. Prompts for the in-app "Generate with AI" box
The in-app model never sees the image. It only sees joint names and positions, so name joints well and put facing direction in the prompt.
- `character faces left; walking in place at a relaxed pace, arms swinging slightly, 1.2 s loop`
- `idle breathing with a slow head tilt, very subtle, 3 s loop`
- `waves hello with the right arm (hanging on the screen's right side), then lowers it, 2.5 s, no loop needed`
- `tail wags with a lagging wave from base to tip, 1 s loop`
- If it returns something off, paste its JSON into the Animation box, fix by hand, press **Apply JSON**. Edit one number at a time and watch the preview.
