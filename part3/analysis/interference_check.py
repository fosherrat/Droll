"""Step 4 check: interference and clearance of the wheel module in its 3 states.

States: rolling (lift 0), bump (lift 0, carriage +10 mm), lifted (lift 22.5).
Reports any solid overlap > 0.5 mm³ between different components, and the
minimum clearance for the pairs that matter. Writes docs/part3/generated/interference.md
"""
import itertools
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from build123d import Compound  # noqa: E402
from droll import params as P  # noqa: E402
from part3.cad import wheel_module as W  # noqa: E402

OUT = ROOT / "docs" / "part3" / "generated" / "interference.md"


def world_parts(lift, bump):
    items = []
    for az in P.WHEEL_AZIMUTHS:
        moving, fixed = W.pod(lift, bump)
        for m in moving + fixed:
            items.append((f"{m.label}@{az}", az, W.to_world(m, az, lift)))
        items.append((f"tower@{az}", az, W.tower_world(az, lift)))
    from build123d import Pos
    for h in [W.hub_plate(), W.nut()] + W.lm6_housings():
        items.append((h.label, None, Pos(0, lift, 0) * h))
    for f in [W.shelf(), W.battery(), W.lead_screw()] + W.guide_rods():
        items.append((f.label, None, f))
    return items


def context():
    return [("cage strut", W.cage_struts()), ("prop disc", W.props()), ("shell", W.shell_lower())]


def bb_gap(a, b):
    A, B = a.bounding_box(), b.bounding_box()
    g = 0.0
    for lo1, hi1, lo2, hi2 in ((A.min.X, A.max.X, B.min.X, B.max.X), (A.min.Y, A.max.Y, B.min.Y, B.max.Y),
                               (A.min.Z, A.max.Z, B.min.Z, B.max.Z)):
        g = max(g, lo2 - hi1, lo1 - hi2)
    return g


def main():
    lines = ["# DRL-P3 interference check\n"]
    worst = {}
    for state, lift, bump in (("rolling", 0.0, 0.0), ("bump +10", 0.0, P.POD_BUMP_TRAVEL), ("lifted", P.LIFT_STROKE, 0.0)):
        t = time.time()
        items = world_parts(lift, bump)
        hits = []
        for (na, aza, a), (nb, azb, b) in itertools.combinations(items, 2):
            if bb_gap(a, b) > 0.05:
                continue
            i = a & b
            v = i.volume if i is not None else 0.0
            if v > 0.5:
                hits.append((na, nb, v))
        ctx_rows = []
        for cname, c in context():
            for az in P.WHEEL_AZIMUTHS:
                pod_parts = [s for n, z, s in items if z == az]
                comp = Compound(children=pod_parts)
                d = comp.distance_to(c) if bb_gap(comp, c) < 60 else bb_gap(comp, c)
                ctx_rows.append((cname, az, d))
        # pod-to-pod and pod-to-centre clearances
        pp = []
        pods = {az: Compound(children=[s for n, z, s in items if z == az]) for az in P.WHEEL_AZIMUTHS}
        for a1, a2 in itertools.combinations(P.WHEEL_AZIMUTHS, 2):
            pp.append((f"pod {a1}° ↔ pod {a2}°", pods[a1].distance_to(pods[a2])))
        centre = [s for n, z, s in items if z is None and ("screw" in n or "rod Ø6" in n or "carbon" in n or "LM6" in n)]
        for az in P.WHEEL_AZIMUTHS:
            pp.append((f"pod {az}° ↔ lead screw / guide rods", min(pods[az].distance_to(c) for c in centre)))
        lines.append(f"## {state} (lift {lift} mm, bump {bump} mm)\n")
        lines.append("Overlaps > 0.5 mm³: " + ("**none**" if not hits else "") + "\n")
        for na, nb, v in hits:
            lines.append(f"- ❌ {na} ↔ {nb}: {v:.1f} mm³")
        lines.append("\n| Pod vs context | 0° | 120° | 240° |\n|---|---|---|---|")
        for cname in ("cage strut", "prop disc", "shell"):
            r = [d for c, az, d in ctx_rows if c == cname]
            lines.append(f"| {cname} | " + " | ".join(f"{x:.1f}" for x in r) + " |")
        lines.append("\n| Clearance | mm |\n|---|---|")
        for n, d in pp:
            lines.append(f"| {n} | {d:.1f} |")
        lines.append("")
        print(state, "done", round(time.time() - t), "s, overlaps:", len(hits))
        for h in hits:
            print("  ", h)
    lines.append("Shell clearance in the rolling states is 0 by design (wheel contact).")
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT.read_text())


if __name__ == "__main__":
    main()
