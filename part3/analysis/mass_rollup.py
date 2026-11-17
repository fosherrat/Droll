"""Step 4: mass roll-up from the CAD solids (volumes × assumed densities).

Prints a table and writes docs/part3/generated/mass.md + mass.json.
Printed parts: PETG 1.27 g/cm³ × 0.55 (walls + 25 % infill). Plates: 3 mm plywood 0.68.
Vendor parts with a known catalogue mass use that instead of the model volume.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from build123d import Rot  # noqa: E402
from droll import params as P  # noqa: E402
from part3.cad import wheel_module as W  # noqa: E402

OUT = ROOT / "docs" / "part3" / "generated"
PRINT = 1.27 * 0.55
DENS = {  # g/cm³
    "carriage": PRINT, "tower": PRINT, "wheel flange": 1.27 * 0.8, "spacer": 1.27,
    "wheel bevel gear": 1.27 * 0.8, "pinion bevel gear": 1.27 * 0.8, "LM6UU housing": PRINT,
    "685ZZ": 7.85 * 0.75, "axle Ø5": 7.85, "rod Ø4": 7.85, "stop collar": 7.85, "LM4UU": 7.85 * 0.6,
    "spring": 7.85, "bump pad": 1.2, "hub plate": 0.68, "battery shelf": 0.68, "base plate": 0.68,
    "rod Ø6": 7.85, "carbon post Ø6": 1.6 * 0.45, "LM6UU": 7.85 * 0.6, "Tr8×1.5 flange nut": 8.5,
}
FIXED_G = {"gearmotor Pololu 4843": 100.0}   # catalogue (Pololu 25D HP + encoder)
WHEEL_PLASTIC, WHEEL_RUBBER = 1.15, 1.25     # nylon/PP plates, TPR rollers


def wheel_mass():
    w = W.wheel_drilled()
    g = 0.0
    for s in w.solids():
        v = s.volume / 1000
        g += v * (WHEEL_RUBBER if abs(s.volume - 1698.3) < 5 else WHEEL_PLASTIC)
    return g


def main():
    rows = {}

    def add(label, grams, group):
        k = (group, label)
        rows[k] = rows.get(k, [0, 0.0])
        rows[k][0] += 1
        rows[k][1] += grams

    wm = wheel_mass()
    for az in P.WHEEL_AZIMUTHS:
        moving, fixed = W.pod(0, 0)
        for m in moving + fixed:
            if "omni" in m.label:
                add(m.label, wm, "pod (×3)")
            elif m.label in FIXED_G:
                add(m.label, FIXED_G[m.label], "pod (×3)")
            else:
                add(m.label, m.volume / 1000 * DENS[m.label], "pod (×3)")
        t = W.tower_world(az, 0)
        add("tower", t.volume / 1000 * DENS["tower"], "pod (×3)")
        add("motor cable 6-wire + JST-PH", 5.0, "pod (×3)")
        add("fasteners (M2.5/M3, set screws)", 6.0, "pod (×3)")
    for h in [W.hub_plate(), W.nut()] + W.lm6_housings():
        add(h.label, h.volume / 1000 * DENS[h.label], "lift")
    for f in [W.shelf()] + W.guide_rods():
        add(f.label, f.volume / 1000 * DENS[f.label], "fixed")
    bp = 0.68 * (P.BOTTOM_SQUARE + 6) ** 2 * W.BASE_T / 1000 * 0.55     # ~45 % cut away by the pod windows
    add("base plate (est., windows ~45 %)", bp, "fixed")

    total = sum(v[1] for v in rows.values())
    unsprung = sum(v[1] for (g, l), v in rows.items() if l in (
        "omni wheel Nexus 14135", "gearmotor Pololu 4843", "carriage", "wheel flange", "spacer", "685ZZ",
        "axle Ø5", "wheel bevel gear", "pinion bevel gear", "rod Ø4", "stop collar")) / 3
    lines = ["# DRL-P3 mass roll-up (from CAD volumes)\n",
             "| Group | Part | Qty | Total g |", "|---|---|---|---|"]
    data = []
    for (g, l), (n, gr) in sorted(rows.items(), key=lambda kv: (kv[0][0], -kv[1][1])):
        lines.append(f"| {g} | {l} | {n} | {gr:.0f} |")
        data.append(dict(group=g, part=l, qty=n, grams=round(gr, 1)))
    lines += [f"| | **Total** | | **{total:.0f}** |", "",
              f"Unsprung mass per pod (moves with the carriage): **{unsprung:.0f} g**.",
              f"Omni-wheel (from vendor STEP volume): {wm:.0f} g each. Motor: catalogue 100 g.",
              "Densities: PETG prints 1.27 × 0.55 (gears, flange 0.8), steel 7.85, plywood 0.68."]
    (OUT / "mass.md").write_text("\n".join(lines) + "\n")
    (OUT / "mass.json").write_text(json.dumps(dict(total_g=round(total), unsprung_per_pod_g=round(unsprung),
                                                   wheel_g=round(wm, 1), rows=data), indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
