# Animation and rigging cookbook

Written for AI agents (and humans). Most bad results come from joint placement and units, not from the keyframes.

## 1. Placing joints
- **Joint = pivot.** Put it where the body part really turns: shoulder socket, elbow, hip, knee, ankle, base of a tail, base of the neck. Not the middle of the part.
- **Follow the centerline** of each limb. Use the grid image and read the x/y of the middle of the limb at each pivot.
- **Always include a body chain**: `pelvis` (root) then `spine`, `neck`, `head`. Without a torso bone the torso follows whichever limb is nearest and gets dragged.
- **Leaf joints matter.** A joint with no child has no bone, so its part cannot bend. Add `hand`, `toe`, `tail_tip`, `head` (or `nose`) at the tips.
- **Parent order = motion order.** Root (hips or base) at the centre of mass; shoulders and hips are children of the spine or pelvis; elbows of shoulders; hands of elbows.
- **Spacing.** Joints closer than about 3% of the image size blend into mush. Joints much farther apart than about 40% make stiff limbs; add a middle joint.
- **Anchor joints.** To keep an area still (a belt buckle, a sign), put an unanimated joint on it.
- **Soft parts** (hair, cloth, tails, ears): a chain of 2 to 4 joints down the part, each a child of the previous, animated with phase delay (section 5).
- **Hidden limbs**: if a limb is mostly hidden, rig only what is visible.
- **Name joints for meaning**: `thigh_f`, `knee_f`, `ankle_f`, `toe_f`. `_f` / `_b` or `_l` / `_r` suffixes help a model reason about the pose.

## 2. Rotation signs (the most common mistake)
Positive `rot` is **clockwise on screen**. The tip of a bone turns like a clock hand:
down becomes left, left becomes up, up becomes right, right becomes down.

| Situation | Facing left | Facing right |
|---|---|---|
| Leg or arm hanging down, swing FORWARD | positive | negative |
| Same, swing BACK | negative | positive |
| Knee bends (shin goes back) | negative | positive |
| Elbow bends (forearm goes up in front) | positive | negative |
| Arm hanging down, raise it sideways away from the body | toward the screen side it points to: left arm side positive, right arm side negative |
| Head nods down (looking at ground) | negative-ish small | positive-ish small |

When unsure, render one frame with `rot: 30` on that joint and look. Do this for every limb type once.

## 3. Timing and keyframes
- Linear interpolation only, so **sample curves densely**: 8 to 12 keys per second (`n = round(duration * 8)`). A sine with 8 keys per cycle looks smooth.
- **Loops**: last key equals first key, `duration` = last `t`. Make the cycle length a whole number of beats.
- **Durations**: idle breathing 3 to 4 s, walk cycle 1.0 to 1.4 s (one full cycle is two steps), run 0.6 to 0.8 s, wave 2 to 3 s, blink-like quick actions 0.15 to 0.3 s.
- **Holds**: repeat the same value in two keys to pause.
- **Snap**: two keys 0.05 to 0.1 s apart make a fast move.

## 4. Amplitude table (degrees unless noted)
| Motion | Joint | Amount |
|---|---|---|
| Breathing | spine / chest | 1 to 2 rot; root `dy` 1 to 3 px |
| Idle sway | root `dx` 4 to 10 px, rot 1 to 2; others 3 to 6 with delay |
| Head nod | neck 4 to 8, head 4 to 8 |
| Head turn feel | head 3 to 6 plus neck 2 to 4 (no true 3D turn) |
| Wave | shoulder 120 to 160 raise; elbow +/-20 to 35 at 2 to 3 Hz |
| Walk | thigh +/-25 to 35, knee 30 to 45 (swing phase only), body bob 5 to 8 px |
| Run | thigh +/-45 to 60, knee 70 to 100, bob 10 to 16 px, lean spine 5 to 10 |
| Jump | crouch dy +8, launch dy -40 to -90, land dy +6 with knees bent 30 to 50 |
| Tail wag | each tail joint 10 to 25, delay 0.08 s per joint |
| Wing flap | shoulder joint +/-35 to 60, wrist +/-15 to 30 with 0.1 s delay |
| Hair or cloth sway | 3 to 10 per joint, delay 0.1 s per joint |
Stay under about 60 degrees per joint where you can; add a middle joint and share the turn instead.

## 5. The twelve-principle shortcuts that work here
- **Follow-through and overlap**: children lag parents by 0.05 to 0.15 s. Implement by shifting the sine phase: `rot = amp * sin(2*pi*t/T - depth*0.6)`.
- **Anticipation**: before a big move, add a small opposite move over 0.1 to 0.2 s (crouch before a jump, arm back before a throw).
- **Overshoot and settle**: go 15% past the target, then back, within 0.2 s.
- **Arcs**: tips of limbs should travel in curves; rotating a chain gives arcs for free, so prefer rotation over `dx`/`dy`.
- **Opposition**: arms swing opposite to the same-side leg; shoulders counter-rotate to hips by 2 to 4 degrees.
- **Weight**: heavy things move less and later; light things (hair, tail tips) move more and later.
- **Root stays home** for loops: avoid net `dx`/`dy` drift so the loop does not slide. Walk in place.
- **Hierarchy of effort**: first get the main action right (legs for a walk), then add 2 or 3 secondary motions (torso, head, hair). Stop there.

## 6. Recipes (rest pose = original image)
Let `p = 2*pi*i/n` for keyframe i of n. The image's rest pose is one extreme of the motion, so write values as offsets from it.

**Walk (side view, facing left, rest pose mid-stride with leg F forward and leg B back)** (exactly what the hiker demo uses, see `walk()` in `index.html`)
```
duration 1.2, n = 24
thigh_F rot = 30*(cos p - 1)      thigh_B rot = 30*(1 - cos p)
knee_F  rot = -40*max(0, -sin p)  knee_B  rot = -40*max(0,  sin p)
ankle_x rot = -0.5*(thigh_x + knee_x)       # keeps feet roughly flat
pelvis  dy  = -7*sin(p)^2, rot = 2*sin p    # two bobs per cycle
spine rot = 3*sin(2p+0.5); neck = -2*sin(2p+0.5); head = 2*sin(2p+1)
arm: shoulder 5*sin p; elbow 4*sin(p+0.8)
```
If the rest pose is not mid-stride (legs together), use `thigh_F = 25*sin p`, `thigh_B = -25*sin p` and adjust knees the same way.

**Idle / breathe (3 s)**: `spine rot = 1.5*sin p`, `pelvis dy = -2*sin p`, `head rot = -1*sin(p-0.6)`, arms `2*sin(p-0.8)`.

**Wave (2.4 s)**: shoulder 0 to -150 (raise, if the arm hangs on the screen-right side of a front view) in 0.4 s, hold, then back in 0.4 s; elbow alternates +28 / -28 every 0.3 s while raised; add spine -3 and a small body dy.

**Bounce / jump loop (1 s)**: root `dy = -20*|sin(pi*t)|`; knees bend most at the bottom; arms lag 0.1 s.

**Tail or hair chain**: for joint k of K: `rot_k = amp*sin(p - 0.7*k)`, amp growing toward the tip.

## 7. Symptom to fix
| You see | Cause | Fix |
|---|---|---|
| A limb folds the wrong way | sign error | flip the sign of that joint's rot |
| Whole body drags when one arm moves | no torso/spine bones near the torso | add `pelvis`/`spine` and put joints inside the torso |
| Limb tears or looks like a twisted candy wrapper | rotation too large at one joint | split across joints, add a middle joint, reduce angle |
| Part does not move at all | it is a leaf joint with no child, or the track name is misspelled | add a child/tip joint; check `check.py` for "no matching joint" |
| Background slides with the subject | no `background` layer | run `tools/cutout.py` and use two layers |
| Ghost copy of a limb left behind | nothing fills the original spot (single layer) | lower amplitude or use the layer split |
| Loop jumps at the wrap | first and last keys differ, or duration is wrong | copy key 0 to the end, set duration to last t |
| Motion looks robotic | all joints in phase | add 0.05 to 0.15 s delay per child, secondary motion |
| Motion is jittery | too few or too many keys | 8 to 12 per second, no duplicate times |
| Everything is tiny | amplitudes too small for the image size | scale rot/dx/dy; at 600x800, 5 to 10 px is visible, 1 px is not |
| Nothing loads from a URL | CORS or `file://` | serve over http, use a relative path or a data URI |

## 8. Verification loop
`python tools/check.py projects/name.json --frames 8` then open `check.png`. Check frame 0 (looks like the original), the extremes (no tearing), and that frame 7 leads smoothly back to frame 0.
Use `--no-joints` for a clean look. Re-run after every edit. Two or three passes is normal.
