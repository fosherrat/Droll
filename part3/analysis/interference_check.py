"""Step 4 check: interference and clearance of the wheel module in its 3 states.

States: rolling (lift 0), bump (lift 0, carriage +10 mm), lifted (lift 22.5).

Method (robust with multi-solid vendor compounds):
  * exact minimum distance (BRepExtrema) for every pair whose bounding boxes are
    within 5 mm;
  * pairs at distance 0 that are NOT meant to touch are reported as collisions;
  * pairs meant to touch (bearing in its seat, shaft in its bore …) are checked
    solid-by-solid for overlap volume, which must stay below 0.5 mm³.
Writes docs/part3/generated/interference.md
"""
import itertools
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from build123d import Compound, Pos  # noqa: E402
from droll import params as P  # noqa: E402
from part3.cad import wheel_module as W  # noqa: E402

OUT = ROOT / "docs" / "part3" / "generated" / "interference.md"

# label pairs (same pod or shared) that are designed to touch
CONTACT = {frozenset(p) for p in [
    ("685ZZ", "carriage"), ("685ZZ", "axle Ø5"), ("axle Ø5", "wheel bevel gear"), ("axle Ø5", "wheel flange"),
    ("axle Ø5", "spacer"), ("axle Ø5", "omni wheel Nexus 14135"), ("omni wheel Nexus 14135", "wheel flange"),
    ("omni wheel Nexus 14135", "spacer"), ("wheel flange", "685ZZ"), ("spacer", "685ZZ"),
    ("LM4UU", "carriage"), ("LM4UU", "rod Ø4"), ("rod Ø4", "stop collar"), ("rod Ø4", "tower"),
    ("spring", "carriage"), ("spring", "tower"), ("spring", "rod Ø4"), ("pinion bevel gear", "gearmotor Pololu 4843"),
    ("gearmotor Pololu 4843", "carriage"), ("bump pad", "tower"), ("hub plate", "tower"),
    ("hub plate", "Tr8×1.5 flange nut"), ("LM6UU housing", "hub plate"), ("LM6UU", "LM6UU housing"),
    ("LM6UU", "rod Ø6"), ("rod Ø6", "battery shelf"), ("carbon post Ø6", "battery shelf"),
    ("6S 2200 battery", "battery shelf"), ("Tr8×1.5 lead screw (Part 2)", "Tr8×1.5 flange nut"),
    ("Tr8×1.5 lead screw (Part 2)", "battery shelf"), ("wheel bevel gear", "pinion bevel gear"),
    ("stop collar", "carriage"), ("rod Ø6", "hub plate"), ("carbon post Ø6", "hub plate"),
    ("Tr8×1.5 lead screw (Part 2)", "hub plate"),
]}


def base(label):
    return re.sub(r"@\d+$", "", label or "")


def world_parts(lift, bump):
    items = []
    for az in P.WHEEL_AZIMUTHS:
        moving, fixed = W.pod(lift, bump)
        for m in moving + fixed:
            items.append((f"{m.label}@{az}", az, W.to_world(m, az, lift)))
        items.append((f"tower@{az}", az, W.tower_world(az, lift)))
    for h in [W.hub_plate(), W.nut()] + W.lm6_housings():
        items.append((h.label, None, Pos(0, lift, 0) * h))
    for f in [W.shelf(), W.battery(), W.lead_screw()] + W.guide_rods():
        items.append((f.label, None, f))
    return items


def bb_gap(a, b):
    A, B = a.bounding_box(), b.bounding_box()
    g = -1e9
    for lo1, hi1, lo2, hi2 in ((A.min.X, A.max.X, B.min.X, B.max.X), (A.min.Y, A.max.Y, B.min.Y, B.max.Y),
                               (A.min.Z, A.max.Z, B.min.Z, B.max.Z)):
        g = max(g, lo2 - hi1, lo1 - hi2)
    return g


def overlap_volume(a, b):
    v = 0.0
    for sa in a.solids():
        for sb in b.solids():
            if bb_gap(sa, sb) > 0:
                continue
            i = sa.intersect(sb)
            if i is not None:
                v += sum(q.volume for q in (i.solids() if hasattr(i, "solids") else []))
    return v


def check_state(lift, bump):
    items = world_parts(lift, bump)
    collisions, tight_contacts, near = [], [], []
    for (na, aza, a), (nb, azb, b) in itertools.combinations(items, 2):
        if bb_gap(a, b) > 5:
            continue
        same_pod = aza is None or azb is None or aza == azb
        d = a.distance_to(b)
        pair = frozenset((base(na), base(nb)))
        if d < 1e-3:
            if same_pod and pair in CONTACT:
                v = overlap_volume(a, b)
                if v > 0.5:
                    tight_contacts.append((na, nb, v))
            else:
                v = overlap_volume(a, b)
                collisions.append((na, nb, v))
        elif d < 3.0:
            near.append((na, nb, d))
    ctx = {}
    pods = {az: Compound(children=[s for n, z, s in items if z == az]) for az in P.WHEEL_AZIMUTHS}
    for cname, c in (("cage strut", W.cage_struts()), ("prop disc", W.props()), ("shell", W.shell_lower())):
        ctx[cname] = [pods[az].distance_to(c) for az in P.WHEEL_AZIMUTHS]
    pp = []
    for a1, a2 in itertools.combinations(P.WHEEL_AZIMUTHS, 2):
        pp.append((f"pod {a1}° ↔ pod {a2}°", pods[a1].distance_to(pods[a2])))
    centre = [s for n, z, s in items if z is None and any(k in n for k in ("screw", "rod Ø6", "carbon", "LM6"))]
    for az in P.WHEEL_AZIMUTHS:
        pp.append((f"pod {az}° ↔ centre rods / screw", min(pods[az].distance_to(c) for c in centre)))
    return collisions, tight_contacts, near, ctx, pp


def main():
    lines = ["# DRL-P3 interference check\n",
             "Exact distances (BRepExtrema). Designed contacts are checked for overlap volume.\n"]
    for state, lift, bump in (("rolling", 0.0, 0.0), ("bump +10", 0.0, P.POD_BUMP_TRAVEL),
                              ("lifted", P.LIFT_STROKE, 0.0)):
        t = time.time()
        coll, tight, near, ctx, pp = check_state(lift, bump)
        lines.append(f"## {state} (lift {lift} mm, bump {bump} mm)\n")
        lines.append(f"- Collisions: **{len(coll)}**")
        for na, nb, v in coll:
            lines.append(f"  - ❌ {na} ↔ {nb} (overlap {v:.1f} mm³)")
        lines.append(f"- Designed contacts with overlap > 0.5 mm³: **{len(tight)}**")
        for na, nb, v in tight:
            lines.append(f"  - ⚠️ {na} ↔ {nb}: {v:.1f} mm³")
        lines.append(f"- Pairs closer than 3 mm (not touching): {len(near)}")
        for na, nb, d in sorted(near, key=lambda x: x[2])[:12]:
            lines.append(f"  - {na} ↔ {nb}: {d:.2f} mm")
        lines.append("\n| Pod vs context (mm) | 0° | 120° | 240° |\n|---|---|---|---|")
        for k, v in ctx.items():
            lines.append(f"| {k} | " + " | ".join(f"{x:.1f}" for x in v) + " |")
        lines.append("\n| Clearance | mm |\n|---|---|")
        for n, d in pp:
            lines.append(f"| {n} | {d:.1f} |")
        lines.append("")
        print(state, round(time.time() - t), "s", "collisions", len(coll), "tight", len(tight), flush=True)
        OUT.write_text("\n".join(lines) + "\n")
    lines.append("Shell distance is 0 in the rolling states by design (wheel contact).")
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT.read_text())


if __name__ == "__main__":
    main()
