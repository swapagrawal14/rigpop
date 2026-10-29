# Project JSON format (v2)

One file holds the image reference, the skeleton and the animation. Open it with **Open project (.json)** in the app,
or load it by URL: `index.html?project=projects/name.json` (served over http).

```json
{
 "v": 2,
 "name": "hiker walk",
 "size": [600, 800],
 "image": "examples/hiker-char.webp",
 "background": "examples/hiker-bg.jpg",
 "joints": [
  {"name": "pelvis", "x": 322, "y": 425, "parent": null},
  {"name": "spine",  "x": 300, "y": 330, "parent": "pelvis"}
 ],
 "animation": {
  "duration": 1.2,
  "tracks": {
   "spine":  [{"t": 0}, {"t": 0.6, "rot": -3}, {"t": 1.2}],
   "pelvis": [{"t": 0}, {"t": 0.3, "dy": -7}, {"t": 0.6}, {"t": 0.9, "dy": -7}, {"t": 1.2}]
  }
 }
}
```

| Field | Required | Meaning |
|---|---|---|
| `v` | no | Format version, currently 2 |
| `name` | no | Shown in the status line |
| `size` | strongly advised | `[width, height]` of the coordinate space. The image is scaled to exactly this (longest side capped at 1000). All joint x/y use it. If missing, the image's natural size is used |
| `image` | for a first load | The layer that gets deformed. Relative path, `https://` URL (must allow CORS) or `data:` URI. PNG/WebP with alpha is best |
| `background` | no | A static layer drawn behind `image`, same framing. Use it when the subject was cut out |
| `joints` | yes | Array of `{name, x, y, parent}`. `parent` is another joint's name or `null` for a root. Rest pose = these positions, all rotations 0 |
| `animation.duration` | no | Seconds. Defaults to the last keyframe time |
| `animation.tracks` | yes | `{ "<joint name>": [ {t, rot?, dx?, dy?}, ... ] }`. Missing values are 0. Keys need not be sorted |

An animation-only file (no `image`, no `joints`) is valid once an image and rig are already open. `anim` is accepted as an alias for `animation`.

## Keyframe fields
- `t` seconds from the start.
- `rot` degrees relative to the rest pose, positive = clockwise on screen. Rotates the joint's child bones and everything skinned to them around the joint.
- `dx`, `dy` pixels, root joints only.

## Skinning model (why joint placement matters)
Each piece of the image follows the nearest bones. Bones are the lines from a joint to each of its children; a joint with no children acts as a point.
So a limb only bends where you put joints, and anything far from every bone follows the closest one.
