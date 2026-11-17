"""Part 3 (wheel module) — step 0 requirements check.

Recomputes, independently of the HTML part sheet:
  * contact / wheel-centre geometry
  * 3D clearance of a wheel envelope against cage struts, prop discs and the
    lead-screw axis over the lift stroke
  * how much room a motor pointing inward has (max body length)
  * the pendulum-limited drive torque, wheel load, speed and power
  * derived motor / encoder requirements

Run:  python3 part3/analysis/requirements_check.py
Writes docs/part3/generated/{requirements.json, req_tables.md, envelope.png, envelope.svg}
"""
import json
import sys
from math import asin, cos, degrees, pi, radians, sin, sqrt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from droll import params as P  # noqa: E402

OUT = ROOT / "docs" / "part3" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

UP = np.array([0.0, 1.0, 0.0])
th = radians(P.CONTACT_ANGLE)
RW = P.WHEEL_D / 2


def frame(az_deg):
    a = radians(az_deg)
    er = np.array([cos(a), 0.0, sin(a)])
    eaz = np.array([-sin(a), 0.0, cos(a)])
    return er, eaz


def pod_geom(az_deg, lift=0.0):
    """Contact point, outward normal, wheel centre, axle dir, drive dir."""
    er, eaz = frame(az_deg)
    n = sin(th) * er - cos(th) * UP              # outward normal at contact
    contact = P.SHELL_R_IN * n
    axle = cos(th) * er + sin(th) * UP           # meridian tangent
    c = (P.SHELL_R_IN - RW) * n
    if lift > 0:                                 # unloaded carriage returns to stop
        c = c + P.POD_SPRING_TRAVEL_STATIC * n + lift * UP
    return dict(contact=contact, n=n, c=c, axle=axle, drive=eaz)


def wheel_points(g, n_psi=72, n_s=7):
    pts = []
    for psi in np.linspace(0, 2 * pi, n_psi, endpoint=False):
        rim = RW * (cos(psi) * g["n"] + sin(psi) * g["drive"])
        for s in np.linspace(-P.WHEEL_W / 2, P.WHEEL_W / 2, n_s):
            pts.append(g["c"] + rim + s * g["axle"])
    return np.array(pts)


# ------------------------------------------------------------- cage struts
def cage_struts():
    h = P.BOTTOM_SQUARE / 2
    yb = P.BOTTOM_SQUARE_Y
    X, e = P.SIDE_FACE_X, P.EQUATOR_SQUARE_HALF
    yt = P.LOWER_SIDE_TOP_Y
    segs = []
    corners = [(sx * h, yb, sz * h) for sx in (1, -1) for sz in (1, -1)]
    # bottom square edges
    sq = [(h, yb, h), (h, yb, -h), (-h, yb, -h), (-h, yb, h)]
    for i in range(4):
        segs.append(("bottom-square", np.array(sq[i]), np.array(sq[(i + 1) % 4])))
    # slanted edges of the 4 lower side faces, and the lower triangles' top edges
    for (cx, cy, cz) in corners:
        sx, sz = np.sign(cx), np.sign(cz)
        top_x = np.array([sx * X, yt, sz * e])   # on the ±x side face
        top_z = np.array([sx * e, yt, sz * X])   # on the ±z side face
        segs.append(("lower-face edge", np.array([cx, cy, cz]), top_x))
        segs.append(("lower-face edge", np.array([cx, cy, cz]), top_z))
        segs.append(("lower triangle", top_x, top_z))
    return segs


def seg_dist(pts, a, b):
    ab = b - a
    t = np.clip(((pts - a) @ ab) / (ab @ ab), 0, 1)
    proj = a + t[:, None] * ab
    return np.linalg.norm(pts - proj, axis=1)


def prop_dist(pts, az):
    a = radians(az)
    c = np.array([P.PROP_HUB_R * cos(a), P.PROP_PLANE_Y, P.PROP_HUB_R * sin(a)])
    d = pts - c
    rh = np.linalg.norm(d[:, [0, 2]], axis=1)
    dy = np.abs(d[:, 1])
    out = np.maximum(rh - P.PROP_D / 2, 0)
    return np.sqrt(out ** 2 + dy ** 2)


STRUTS = cage_struts()


def clearances(lift):
    res = {"strut": 1e9, "strut_name": "", "prop": 1e9, "shell_in": 1e9}
    for az in P.WHEEL_AZIMUTHS:
        g = pod_geom(az, lift)
        pts = wheel_points(g)
        for name, a, b in STRUTS:
            d = seg_dist(pts, a, b).min() - P.CAGE_STRUT_D / 2
            if d < res["strut"]:
                res["strut"], res["strut_name"] = d, f"{name} (wheel @{az}°)"
        for paz in P.PROP_AZIMUTHS:
            res["prop"] = min(res["prop"], prop_dist(pts, paz).min())
        if lift > 0:
            r = np.linalg.norm(pts, axis=1)
            res["shell_in"] = min(res["shell_in"], P.SHELL_R_IN - r.max())
    return res


# ------------------------------------------------------------- motor room
MOTOR_D = 25.0          # 25 mm gearmotor class (envelope incl. gearbox)
BEVEL_OFFSET = P.WHEEL_W / 2 + 10.0   # motor axis offset from wheel centre along axle
NUT_FLANGE_R = 11.0     # T8 flange nut


def motor_room(side):
    """Max motor body length if its axis runs along -n from beside the wheel.

    side=+1: bevel/motor on the equator side of the wheel, -1: on the pole side.
    Body starts 12 mm in from the axle line (bevel pinion + mount)."""
    s0 = 12.0
    lim = {}
    axes = []
    for az in P.WHEEL_AZIMUTHS:
        g = pod_geom(az)
        origin = g["c"] + side * BEVEL_OFFSET * g["axle"]
        axes.append((origin, -g["n"]))
    o0, d0 = axes[0]
    for L in np.arange(10, 200, 0.5):
        tip = o0 + d0 * (s0 + L)
        seg = np.linspace(o0 + d0 * s0, tip, 40)
        # 1) top of body vs hub plate underside (plate 3 mm thick at HUB_Y_DOWN)
        y_top = seg[:, 1].max() + MOTOR_D / 2 * sin(th)
        if "hub plate" not in lim and y_top > P.HUB_Y_DOWN - 3 - 3:
            lim["hub plate"] = L
        # 2) lead screw / nut on the axis
        r_axis = np.linalg.norm(seg[:, [0, 2]], axis=1).min()
        if "lead-screw nut" not in lim and r_axis < MOTOR_D / 2 + NUT_FLANGE_R + 2:
            lim["lead-screw nut"] = L
        # 3) neighbouring motors
        for o1, d1 in axes[1:]:
            seg1 = np.linspace(o1 + d1 * s0, o1 + d1 * (s0 + L), 40)
            dmin = np.min(np.linalg.norm(seg[:, None, :] - seg1[None, :, :], axis=2))
            if "other motors" not in lim and dmin < MOTOR_D + 2:
                lim["other motors"] = L
        # 4) prop disc
        if "prop disc" not in lim and prop_dist(seg, 0).min() < MOTOR_D / 2 + P.PROP_CLEAR_MIN:
            lim["prop disc"] = L
        if len(lim) == 4:
            break
    first = min(lim.items(), key=lambda kv: kv[1])
    return first, lim


# ------------------------------------------------------------- dynamics
def dynamics(v_target, m=P.HANGING_MASS, d_mm=P.COM_BELOW_CENTRE, phi_deg=P.FRAME_TILT_MAX):
    g = 9.81
    R = P.SHELL_R_OUT / 1000
    Ri = P.SHELL_R_IN / 1000
    rw = RW / 1000
    ms = P.SHELL_MASS
    d = d_mm / 1000
    phi = radians(phi_deg)
    M = m + ms
    Is = 2 / 3 * ms * R ** 2
    den = Is / R + M * R - m * d * cos(phi)
    a = m * g * d * sin(phi) / den
    T = m * d * (g * sin(phi) + a * cos(phi))           # shell drive torque
    F = 2 / 3 * T / (Ri * cos(th))                        # worst wheel tangential force
    tw = F * rw
    N = m * g / (3 * cos(th))
    Om = v_target / R
    vw = Om * Ri * cos(th) + radians(P.YAW_RATE) * Ri * sin(th)
    rpm = vw / (2 * pi * rw) * 60
    slope = degrees(asin(min(1, m * d * sin(phi) / (M * R))))
    slope_max = degrees(asin(min(1, m * d / (M * R))))
    return dict(
        accel=a, t_to_v=v_target / a, shell_torque=T, wheel_force=F,
        wheel_torque=tw, wheel_torque_peak=tw * P.LOSS_FACTOR,
        normal_load=N, traction_margin=P.MU_ROLLER * N / F,
        wheel_rpm=rpm, wheel_surface_speed=vw,
        power_peak=tw * P.LOSS_FACTOR * vw / rw,
        slope_at_tilt=slope, slope_abs_max=slope_max,
    )


def main():
    out = {}
    g0 = pod_geom(0)
    out["geometry"] = dict(
        contact_r=float(np.hypot(g0["contact"][0], g0["contact"][2])),
        contact_y=float(g0["contact"][1]),
        wheel_centre_r=float(np.hypot(g0["c"][0], g0["c"][2])),
        wheel_centre_y=float(g0["c"][1]),
        bottom_square_y=P.BOTTOM_SQUARE_Y,
        lower_face_height=float(np.hypot(P.SIDE_FACE_X - P.BOTTOM_SQUARE / 2,
                                         P.LOWER_SIDE_TOP_Y - P.BOTTOM_SQUARE_Y)),
    )
    # prop tip to shell
    tip = np.array([P.PROP_HUB_R + P.PROP_D / 2, P.PROP_PLANE_Y])
    out["geometry"]["prop_tip_to_shell"] = float(P.SHELL_R_IN - np.linalg.norm(tip))

    sweep = []
    first_strut_hit = None
    for L in np.arange(0, 40.5, 0.5):
        c = clearances(L)
        hub_gap = P.BATTERY_SHELF_Y - (P.HUB_Y_DOWN + L)
        sweep.append(dict(lift=float(L), strut=c["strut"], strut_name=c["strut_name"],
                          prop=c["prop"], shell_gap=c["shell_in"], hub_to_shelf=hub_gap))
        if first_strut_hit is None and c["strut"] < 0:
            first_strut_hit = float(L)
    out["sweep"] = sweep
    out["lift_limits"] = dict(
        wheel_hits_strut_at=first_strut_hit,
        hub_hits_shelf_at=P.BATTERY_SHELF_Y - P.HUB_Y_DOWN,
    )

    rooms = {}
    for side, name in ((1, "equator side"), (-1, "pole side")):
        first, lim = motor_room(side)
        rooms[name] = dict(max_len=first[1], limited_by=first[0], all=lim)
    out["motor_room"] = rooms

    out["dynamics"] = {f"v={v}": dynamics(v) for v in (P.V_NOMINAL, P.V_MAX)}
    out["sensitivity"] = {
        f"d={d}mm": dynamics(P.V_MAX, d_mm=d) for d in (30, 50, 80, 120)
    }

    dyn = out["dynamics"][f"v={P.V_MAX}"]
    # yaw alignment: 1.5° of shell yaw = this much tread at the wheel
    tread_align = P.SHELL_R_IN * sin(th) * radians(P.ALIGN_TOL)
    out["motor_req"] = dict(
        rpm_loaded=dyn["wheel_rpm"],
        rpm_noload_min=dyn["wheel_rpm"] / 0.75,
        torque_cont=dyn["wheel_torque"],
        torque_peak=dyn["wheel_torque_peak"],
        stall_min=3 * dyn["wheel_torque_peak"],
        power_peak=dyn["power_peak"],
        tread_for_align_tol=tread_align,
        tread_per_count_max=tread_align / 5,
        counts_per_wheel_rev_min=pi * P.WHEEL_D / (tread_align / 5),
    )
    (OUT / "requirements.json").write_text(json.dumps(out, indent=2, default=float))
    write_tables(out)
    draw(out)
    print((OUT / "req_tables.md").read_text())


def write_tables(o):
    g = o["geometry"]
    L = []
    L.append("### Geometry (computed)\n")
    L.append("| Item | Value |\n|---|---|")
    L.append(f"| Contact point | r {g['contact_r']:.1f}, y {g['contact_y']:.1f} |")
    L.append(f"| Wheel centre | r {g['wheel_centre_r']:.1f}, y {g['wheel_centre_y']:.1f} |")
    L.append(f"| Bottom square plane | y {g['bottom_square_y']:.1f} |")
    L.append(f"| Lower side face height | {g['lower_face_height']:.1f} |")
    L.append(f"| Prop tip to shell inner | {g['prop_tip_to_shell']:.1f} |")
    L.append("\n### Lift sweep (worst of 3 wheels; wheel envelope "
             f"Ø{P.WHEEL_D:.0f} × {P.WHEEL_W:.0f})\n")
    L.append("| Lift | Wheel→strut | Nearest strut | Wheel→prop disc | Wheel→shell | Hub→shelf |")
    L.append("|---|---|---|---|---|---|")
    for s in o["sweep"]:
        if s["lift"] in (0, 10, 15, 20, 22.5, 25, 30, 35, 40):
            sg = "contact" if s["lift"] == 0 else f"{s['shell_gap']:.1f}"
            L.append(f"| {s['lift']:.1f} | {s['strut']:.1f} | {s['strut_name']} | "
                     f"{s['prop']:.1f} | {sg} | {s['hub_to_shelf']:.1f} |")
    ll = o["lift_limits"]
    L.append(f"\nWheel envelope touches a strut at **{ll['wheel_hits_strut_at']} mm** lift; "
             f"hub meets battery shelf at **{ll['hub_hits_shelf_at']:.0f} mm**.\n")
    L.append("### Room for a motor pointing inward (25 mm class)\n")
    L.append("| Bevel side | Max body length | Limited by | Other limits |\n|---|---|---|---|")
    for k, r in o["motor_room"].items():
        others = ", ".join(f"{n} {v:.0f}" for n, v in r["all"].items() if n != r["limited_by"])
        L.append(f"| {k} | **{r['max_len']:.0f} mm** | {r['limited_by']} | {others} |")
    L.append("\n### Drive (pendulum-limited, frame tilt "
             f"{P.FRAME_TILT_MAX:.0f}°, hanging {P.HANGING_MASS:.2f} kg, COM −{P.COM_BELOW_CENTRE:.0f} mm)\n")
    L.append("| Case | Accel m/s² | Shell torque N·m | Wheel force N | Wheel torque peak N·m | "
             "Wheel rpm | Normal load N | Traction margin | Peak W |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for k, d in o["dynamics"].items():
        L.append(f"| {k} m/s | {d['accel']:.2f} | {d['shell_torque']:.2f} | {d['wheel_force']:.2f} | "
                 f"{d['wheel_torque_peak']:.3f} | {d['wheel_rpm']:.0f} | {d['normal_load']:.1f} | "
                 f"{d['traction_margin']:.1f}× | {d['power_peak']:.1f} |")
    L.append("\nCOM height sensitivity (v = 1.0 m/s):\n")
    L.append("| COM below centre | Accel m/s² | Wheel torque peak N·m | Max slope at 30° tilt |")
    L.append("|---|---|---|---|")
    for k, d in o["sensitivity"].items():
        L.append(f"| {k} | {d['accel']:.2f} | {d['wheel_torque_peak']:.3f} | {d['slope_at_tilt']:.1f}° |")
    m = o["motor_req"]
    L.append("\n### Derived motor requirements (per wheel, at the wheel axle)\n")
    L.append("| Requirement | Value |\n|---|---|")
    L.append(f"| Loaded speed | {m['rpm_loaded']:.0f} rpm |")
    L.append(f"| No-load speed (buy) | ≥ {m['rpm_noload_min']:.0f} rpm |")
    L.append(f"| Continuous torque | {m['torque_cont']:.3f} N·m |")
    L.append(f"| Peak torque incl. losses | {m['torque_peak']:.3f} N·m |")
    L.append(f"| Stall torque (buy) | ≥ {m['stall_min']:.2f} N·m |")
    L.append(f"| Peak mechanical power | {m['power_peak']:.1f} W |")
    L.append(f"| Tread for ±{P.ALIGN_TOL}° shell yaw | {m['tread_for_align_tol']:.2f} mm |")
    L.append(f"| Encoder: tread per count | ≤ {m['tread_per_count_max']:.2f} mm "
             f"(≥ {m['counts_per_wheel_rev_min']:.0f} counts / wheel rev) |")
    (OUT / "req_tables.md").write_text("\n".join(L) + "\n")


def draw(o):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon, Rectangle

    ink, mut, acc, warn, crit, ok = "#141821", "#8a93a3", "#2456d3", "#b26a00", "#c4352b", "#1f8a4c"
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 7.6), gridspec_kw=dict(width_ratios=[1.25, 1]))
    plt.rcParams["font.family"] = "monospace"

    # ---------------- section at azimuth 0 (x–y plane)
    t = np.linspace(-pi, 0.15, 300)
    ax.plot(P.SHELL_R_IN * np.cos(t), P.SHELL_R_IN * np.sin(t), color=acc, lw=2, label="shell inner r244")
    ax.plot(P.SHELL_R_OUT * np.cos(t), P.SHELL_R_OUT * np.sin(t), color=acc, lw=0.8, alpha=0.5)
    # cage section (z = 0)
    h, yb, X, yt = P.BOTTOM_SQUARE / 2, P.BOTTOM_SQUARE_Y, P.SIDE_FACE_X, P.LOWER_SIDE_TOP_Y
    for sx in (1, -1):
        ax.plot([sx * h, sx * X], [yb, yt], color=mut, lw=1.2, ls="--")
        ax.plot([sx * X, sx * X], [yt, 20], color=mut, lw=1.2, ls="--")
        ax.add_patch(Circle((sx * h, yb), 3, color=ink))
    ax.plot([-h, h], [yb, yb], color=mut, lw=0.8, ls=":")
    ax.text(0, yb - 9, f"bottom square plane y {yb:.1f}", ha="center", fontsize=8, color=mut)
    # prop discs (level) + clearance band
    for sx in (1, -1):
        x0, x1 = sx * (P.PROP_HUB_R - P.PROP_D / 2), sx * (P.PROP_HUB_R + P.PROP_D / 2)
        ax.add_patch(Rectangle((min(x0, x1), P.PROP_PLANE_Y - P.PROP_CLEAR_MIN), P.PROP_D,
                               2 * P.PROP_CLEAR_MIN, color=crit, alpha=0.12, lw=0))
        ax.plot([x0, x1], [P.PROP_PLANE_Y] * 2, color=crit, lw=2.5)
    ax.text(P.PROP_HUB_R, P.PROP_PLANE_Y + 14, '5" prop (keep-out ±10)', ha="center", fontsize=8, color=crit)
    # lead screw, hub, shelf, battery
    ax.plot([0, 0], [-130, 40], color=ink, lw=2.5)
    for L, sty in ((0, "-"), (P.LIFT_STROKE, "--")):
        ax.add_patch(Rectangle((-70, P.HUB_Y_DOWN - 3 + L), 140, 3,
                               facecolor=warn if sty == "-" else "none",
                               edgecolor=warn, ls=sty, lw=1.2))
    ax.annotate(f"hub plate y {P.HUB_Y_DOWN:.0f}", (-60, P.HUB_Y_DOWN - 1.5), (-150, -135),
                fontsize=8, color=warn, arrowprops=dict(arrowstyle="-", color=warn))
    ax.annotate(f"hub lifted +{P.LIFT_STROKE}", (-60, P.HUB_Y_DOWN + P.LIFT_STROKE - 1.5), (-150, -60),
                fontsize=8, color=warn, arrowprops=dict(arrowstyle="-", color=warn))
    ax.add_patch(Rectangle((-65, P.BATTERY_SHELF_Y), 130, 3, color=mut))
    ax.add_patch(Rectangle((10, P.BATTERY_SHELF_Y + 3), 35, 38, facecolor="none", edgecolor=ink, lw=1))
    ax.text(48, P.BATTERY_SHELF_Y + 20, "6S battery\n(end view)", fontsize=7.5, color=ink)
    # wheel at az 0, down and lifted
    for L, sty, col in ((0, "-", ink), (P.LIFT_STROKE, "--", mut)):
        g = pod_geom(0, L)
        n2 = np.array([g["n"][0], g["n"][1]])
        a2 = np.array([g["axle"][0], g["axle"][1]])
        c2 = np.array([g["c"][0], g["c"][1]])
        corners = [c2 + sn * RW * n2 + sa * P.WHEEL_W / 2 * a2 for sn, sa in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        ax.add_patch(Polygon(corners, closed=True, facecolor="#e9edf3" if L == 0 else "none",
                             edgecolor=col, ls=sty, lw=1.4))
    g = pod_geom(0)
    ax.plot(*g["contact"][[0, 1]], "o", color=crit, ms=5)
    ax.annotate(f"contact {P.CONTACT_ANGLE:.0f}° · r {o['geometry']['contact_r']:.0f}, "
                f"y {o['geometry']['contact_y']:.0f}", g["contact"][[0, 1]], (40, -262),
                fontsize=8, arrowprops=dict(arrowstyle="-", color=mut))
    # motor envelope (pole side and equator side)
    for side, col in ((1, ok), (-1, acc)):
        name = "equator side" if side == 1 else "pole side"
        Lm = o["motor_room"][name]["max_len"]
        org = g["c"] + side * BEVEL_OFFSET * g["axle"] - 12 * g["n"]
        tipp = org - Lm * g["n"]
        nn = np.array([-g["n"][1], g["n"][0]])[[0, 1]]
        perp = np.array([g["axle"][0], g["axle"][1]])
        poly = [org[[0, 1]] + perp * MOTOR_D / 2, tipp[[0, 1]] + perp * MOTOR_D / 2,
                tipp[[0, 1]] - perp * MOTOR_D / 2, org[[0, 1]] - perp * MOTOR_D / 2]
        ax.add_patch(Polygon(poly, closed=True, facecolor=col, alpha=0.15, edgecolor=col, lw=1))
        mid = (org + tipp)[[0, 1]] / 2
        ax.annotate(f"motor room ({name})\n≤ {Lm:.0f} mm, {o['motor_room'][name]['limited_by']}",
                    mid, (150, -150) if side == 1 else (-30, -215), fontsize=7.5, color=col,
                    ha="left" if side == 1 else "right",
                    arrowprops=dict(arrowstyle="-", color=col))
    ax.set_aspect("equal")
    ax.set_xlim(-255, 255)
    ax.set_ylim(-262, 40)
    ax.set_title("Section through wheel @0° (x–y), mm, origin = sphere centre", fontsize=10)
    ax.grid(alpha=0.15)

    # ---------------- top view
    ax2.add_patch(Circle((0, 0), P.SHELL_R_IN, fill=False, color=acc, lw=2))
    oct_pts = [(h, h), (X, P.EQUATOR_SQUARE_HALF), (X, -P.EQUATOR_SQUARE_HALF), (h, -h)]
    sq = Rectangle((-h, -h), 2 * h, 2 * h, fill=False, color=mut, ls="--")
    ax2.add_patch(sq)
    for sx in (1, -1):
        for sz in (1, -1):
            ax2.plot([sx * h, sx * X], [sz * h, sz * P.EQUATOR_SQUARE_HALF], color=mut, lw=1)
            ax2.plot([sx * h, sx * P.EQUATOR_SQUARE_HALF], [sz * h, sz * X], color=mut, lw=1)
            ax2.plot([sx * X, sx * P.EQUATOR_SQUARE_HALF], [sz * P.EQUATOR_SQUARE_HALF, sz * X], color=mut, lw=1)
        ax2.plot([sx * X, sx * X], [-P.EQUATOR_SQUARE_HALF, P.EQUATOR_SQUARE_HALF], color=mut, lw=1)
        ax2.plot([-P.EQUATOR_SQUARE_HALF, P.EQUATOR_SQUARE_HALF], [sx * X, sx * X], color=mut, lw=1)
    for paz in P.PROP_AZIMUTHS:
        a = radians(paz)
        ax2.add_patch(Circle((P.PROP_HUB_R * cos(a), P.PROP_HUB_R * sin(a)), P.PROP_D / 2,
                             color=crit, alpha=0.12))
    for az in P.WHEEL_AZIMUTHS:
        g = pod_geom(az)
        c = g["c"][[0, 2]]
        dv = g["drive"][[0, 2]]
        ax2_pts = [c + sd * RW * dv + sa * P.WHEEL_W / 2 * cos(th) * g["axle"][[0, 2]] / max(1e-9, np.linalg.norm(g["axle"][[0, 2]]))
                   for sd, sa in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        ax2.add_patch(Polygon(ax2_pts, closed=True, facecolor="#e9edf3", edgecolor=ink))
        ax2.annotate("", c + 32 * dv, c, arrowprops=dict(arrowstyle="->", color=crit))
        ax2.text(*(c * 0.55), f"{az}°", fontsize=8, ha="center")
    for raz in P.GUIDE_ROD_AZ:
        a = radians(raz)
        ax2.add_patch(Circle((P.GUIDE_ROD_R * cos(a), P.GUIDE_ROD_R * sin(a)), 3, color=ink))
    ax2.add_patch(Circle((0, 0), 4, color=ink))
    ax2.add_patch(Rectangle((10, -53), 35, 106, fill=False, color=ink, ls=":"))
    ax2.text(48, 40, "battery\n(on shelf)", fontsize=7.5)
    ax2.set_aspect("equal")
    ax2.set_xlim(-255, 255)
    ax2.set_ylim(-255, 255)
    ax2.set_xlabel("x")
    ax2.set_ylabel("z")
    ax2.set_title("Top view: cage (grey), props (red), wheels + drive dir", fontsize=10)
    ax2.grid(alpha=0.15)
    fig.suptitle("DRL-P3 · step 0 · available envelope (status: draft, values from droll/params.py)",
                 fontsize=11, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "envelope.png", dpi=150)
    fig.savefig(OUT / "envelope.svg")


if __name__ == "__main__":
    main()
