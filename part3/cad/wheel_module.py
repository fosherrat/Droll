"""DRL-P3 wheel module — full parametric assembly (step 3).

Pod frame (one per wheel), right-handed:
  origin  wheel centre in the loaded (rolling) state
  X       drive direction (azimuthal, the way the wheel pushes the shell)
  Y       wheel axle, along the meridian, + toward the equator
  Z       inward shell normal, + toward the sphere centre ("up" for the pod)
World: origin = sphere centre, +y up (see droll/params.py).

States:  lift = 0     rolling, carriage loaded 2.7 mm off its stop
         lift = 22.5  lifted, carriage on its stop (2.7 mm further out)

Run:  python3 part3/cad/wheel_module.py      → part3/cad/out/*.glb|step + report
"""
import json
import sys
from functools import lru_cache
from math import asin, atan2, cos, degrees, pi, radians, sin, sqrt, tan
from pathlib import Path

from build123d import (Align, Axis, Box, Color, Compound, Cylinder, Helix, Location, Plane, Pos,
                       Rot, Solid, Sphere, Vector, export_gltf, export_step, extrude, Circle, Rectangle,
                       sweep, Wire, Polygon, Face, make_face, offset, Polyline, fillet, chamfer)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from droll import params as P            # noqa: E402
from part3.cad.bevel import bevel_gear   # noqa: E402
from part3.cad.vendor_parts import MOTOR, gearmotor, omni_wheel  # noqa: E402

OUT = ROOT / "part3" / "cad" / "out"
CEN = (Align.CENTER, Align.CENTER, Align.CENTER)
MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)

# ------------------------------------------------------------------ design values (pod frame, mm)
RW = 29.75                 # mean rolling radius of Nexus 14135 (58.9–60.05 measured)
WHEEL_HALF = 14.0          # rollers ±14
BOSS_FACE = 13.0           # wheel hub boss faces at Y = ±13
ARM_IN, ARM_T = 17.0, 6.0  # fork arm inner face |Y|, thickness (room for the wheel flange)
ARM_W = 22.0               # arm width in X
BRG = dict(od=11.0, id=5.0, w=5.0)       # 685ZZ
AXLE_D = 5.0
GEAR = dict(m=1.0, z=20, face=5.0, hub_d=12.0, hub_l=6.0)
GEAR_GAP = 0.5             # washer between arm and gear hub
BRIDGE_Z0, BRIDGE_H = 33.0, 12.0          # carriage bridge above the wheel top (29.75)
BRIDGE_X = 28.0
ROD_X = 21.0               # guide rods at X = ±21, Y = 0
ROD_D = 4.0
LM4 = dict(od=8.0, l=12.0)
STATIC_DEFL = P.POD_SPRING_TRAVEL_STATIC  # 2.7
BUMP = P.POD_BUMP_TRAVEL                  # 10
SPRING = dict(od=6.0, wire=0.5, free=35.0, rate=0.3, preload_n=3.5)   # per spring
SPRING_LOADED_L = SPRING["free"] - SPRING["preload_n"] / SPRING["rate"] - STATIC_DEFL
TOWER_Z0 = BRIDGE_Z0 + BRIDGE_H + SPRING_LOADED_L          # tower underside
TOWER_Y = 9.0              # tower half-depth along Y
HUB_T = 3.0                # hub plate thickness, top face at HUB_Y_DOWN
SHELF_T = 3.0
BASE_T = 3.0

# derived gear placement: gear on the pole side (−Y), teeth pointing −Y
_g, GI = bevel_gear(m=GEAR["m"], z=GEAR["z"], face=GEAR["face"], hub_d=GEAR["hub_d"], hub_l=GEAR["hub_l"], bore=AXLE_D)
GEAR_BACK_Y = -(ARM_IN + ARM_T + GEAR_GAP + GEAR["hub_l"])   # back face of the wheel gear
APEX_Y = GEAR_BACK_Y - GI["apex_z"]                           # where the motor axis crosses the axle
PINION_BACK_Z = GI["apex_z"]                                  # pinion back face, on the motor axis
MOTOR_FACE_Z = PINION_BACK_Z + GEAR["hub_l"] + 3.0            # pinion hub (6) + boss clearance
MOUNT_T = 2.5


def col(shape, c, label):
    shape.color, shape.label = c, label
    return shape


C_PRINT = Color(0.93, 0.55, 0.16)      # PETG orange
C_PRINT2 = Color(0.95, 0.75, 0.30)
C_LASER = Color(0.55, 0.60, 0.66)      # plywood/acrylic plates
C_STEEL = Color(0.72, 0.73, 0.75)
C_DARK = Color(0.2, 0.21, 0.23)
C_BRASS = Color(0.80, 0.62, 0.26)
C_SPRING = Color(0.35, 0.55, 0.85)
C_NYLON = Color(0.92, 0.92, 0.88)
C_BATT = Color(0.15, 0.35, 0.65)


# ------------------------------------------------------------------ pod parts (pod frame)
def ycyl(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along Y from y0 to y1."""
    lo, hi = min(y0, y1), max(y0, y1)
    return Pos(x, lo, z) * Rot(-90, 0, 0) * Cylinder(r, hi - lo, align=MIN_Z)


def zcyl(r, z0, z1, x=0.0, y=0.0):
    lo, hi = min(z0, z1), max(z0, z1)
    return Pos(x, y, lo) * Cylinder(r, hi - lo, align=MIN_Z)


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


@lru_cache
def carriage():
    """Printed fork: two bearing arms + bridge with LM4UU bores + motor mount on the −Y side."""
    a0, a1 = ARM_IN, ARM_IN + ARM_T
    zt = BRIDGE_Z0 + BRIDGE_H
    body = Solid()
    arms = []
    for s in (1, -1):
        arm = box(-ARM_W / 2, ARM_W / 2, s * a0, s * a1, 0, zt)
        arm += ycyl(ARM_W / 2, s * a0, s * a1)                     # rounded lower end around the axle
        arms.append(arm)
    bridge = box(-BRIDGE_X, BRIDGE_X, -a1, a1, BRIDGE_Z0, zt)
    body = arms[0] + arms[1] + bridge
    # motor mount: plate under the motor face + two cheeks along the gearbox
    my = APEX_Y
    plate = box(-15, 15, my - 15, -a0, MOTOR_FACE_Z - MOUNT_T, MOTOR_FACE_Z)
    cheeks = box(-15, -12.8, my - 13, -a0, MOTOR_FACE_Z, zt) + box(12.8, 15, my - 13, -a0, MOTOR_FACE_Z, zt)
    web = box(-15, 15, -a1 - 4, -a0, MOTOR_FACE_Z, zt)               # ties mount into the −Y arm/bridge
    body = body + plate + cheeks + web
    # cuts: axle bearing seats, axle clearance, LM4UU bores, motor bore, boss hole, M3 screws
    for s in (1, -1):
        body -= ycyl(BRG["od"] / 2, s * (a0 + 0.5), s * (a0 + 0.5 + BRG["w"]))
        body -= ycyl(3.2, s * a0 - s * 1, s * a1 + s * 1)
    for sx in (1, -1):
        body -= zcyl(LM4["od"] / 2, BRIDGE_Z0 - 1, zt + 1, x=sx * ROD_X)
    body -= zcyl(MOTOR["gearbox_d"] / 2 + 0.3, MOTOR_FACE_Z, zt + 1, y=my)
    body -= zcyl(4.2, MOTOR_FACE_Z - MOUNT_T - 1, MOTOR_FACE_Z + 1, y=my)
    for sx in (1, -1):
        body -= zcyl(1.7, MOTOR_FACE_Z - MOUNT_T - 1, MOTOR_FACE_Z + 1, x=sx * MOTOR["m3_offset"], y=my)
    # wheel clearance (keeps the bridge underside off the rollers at any roller phase)
    body -= ycyl(RW + 2.5, -WHEEL_HALF - 0.5, WHEEL_HALF + 0.5)
    return col(body, C_PRINT, "carriage")


@lru_cache
def tower_raw(z_top=140.0):
    """Printed tower that holds the rod tops; cut later by the hub plate plane."""
    t = box(-BRIDGE_X, BRIDGE_X, -TOWER_Y, TOWER_Y, TOWER_Z0, z_top)
    # bump-stop boss between the rods, 2 mm urethane pad on it reaches the bridge at BUMP
    t += box(-7, 7, -6, 6, BRIDGE_Z0 + BRIDGE_H + BUMP + 2.0, TOWER_Z0 + 0.1)
    for sx in (1, -1):
        t -= zcyl(ROD_D / 2, TOWER_Z0 - 1, TOWER_Z0 + 22, x=sx * ROD_X)       # rod pockets (22 deep)
        t -= zcyl(SPRING["od"] / 2 + 0.4, TOWER_Z0 - 1, TOWER_Z0 + 4, x=sx * ROD_X)  # spring seat
    return t


def spring(length, x):
    pitch = length / 13.0
    h = Helix(pitch, length, SPRING["od"] / 2 - SPRING["wire"] / 2)
    prof = Plane(origin=h @ 0, z_dir=h % 0) * Circle(SPRING["wire"] / 2)
    s = sweep(prof, path=h)
    return col(Pos(x, 0, BRIDGE_Z0 + BRIDGE_H) * s, C_SPRING, "spring")


WHEEL_FACE = 11.6         # wheel plate face at r 10–18 (|Y|, measured); boss to 13.0 inside r 10


def wheel_flange():
    """Pole-side drive flange (stepped): ring r 10.2–16 seats on the plate face at Y −11.6,
    web over the boss (r < 10.2) from Y −13.1; 2×M2.5 at PCD 26 into the wheel's holes;
    D-bore on the axle. Ends 0.5 mm short of the bearing, with a Ø8 boss onto the inner race."""
    y_out = -ARM_IN + 0.5
    ring = ycyl(16, -WHEEL_FACE - 0.1, y_out) - ycyl(10.2, -WHEEL_FACE - 0.2, -BOSS_FACE - 0.1)
    web = ycyl(10.3, -BOSS_FACE - 0.1, y_out)
    f = ring + web
    f += ycyl(4.0, y_out, -ARM_IN)                            # 0.5 mm boss onto the bearing inner race
    f -= ycyl(AXLE_D / 2, -30, 0)
    for a in (0, 180):
        f -= ycyl(1.35, -30, 0, x=13 * cos(radians(a)), z=13 * sin(radians(a)))
    return col(f, C_PRINT2, "wheel flange")


@lru_cache
def wheel_drilled():
    """Vendor wheel with the hub insert drilled through Ø5 for the axle (build step)."""
    from build123d import Compound as _C
    w = omni_wheel()
    drill = Cylinder(AXLE_D / 2 + 0.05, 60)
    out = []
    for so in w.solids():
        c = so.color
        if so.bounding_box().size.X < 20:                     # hub insert only
            so = so - drill
            so.color = c
        out.append(so)
    return _C(children=out, label="omni wheel Nexus 14135")


def spacer():
    s = ycyl(4.0, BOSS_FACE, ARM_IN) - ycyl(AXLE_D / 2 + 0.1, 0, 20)
    return col(s, C_PRINT2, "spacer")


def pod(lift=0.0, bump=0.0):
    """All parts of one pod in the pod frame. Carriage group shifts by −STATIC_DEFL in Z when lifted,
    and by +bump (toward the tower) when a rolling bump compresses the springs."""
    dz = -STATIC_DEFL if lift > 0 else bump
    moving = []
    w = Rot(-90, 0, 0) * wheel_drilled()          # wheel axis Z → Y
    moving.append(w)
    moving.append(carriage())
    moving.append(wheel_flange())
    moving.append(spacer())
    for s in (1, -1):
        b = ycyl(BRG["od"] / 2, s * (ARM_IN + 0.5), s * (ARM_IN + 0.5 + BRG["w"])) - ycyl(BRG["id"] / 2, -30, 30)
        moving.append(col(b, C_STEEL, "685ZZ"))
    moving.append(col(ycyl(AXLE_D / 2, GEAR_BACK_Y - GI["apex_z"] + 6.4, ARM_IN + ARM_T + 2.0), C_STEEL, "axle Ø5"))
    g, _ = bevel_gear(m=GEAR["m"], z=GEAR["z"], face=GEAR["face"], hub_d=GEAR["hub_d"], hub_l=GEAR["hub_l"], bore=AXLE_D)
    wheel_gear = Pos(0, GEAR_BACK_Y, 0) * Rot(90, 0, 0) * g            # local +Z → −Y
    moving.append(col(wheel_gear, C_NYLON, "wheel bevel gear"))
    pin, _ = bevel_gear(m=GEAR["m"], z=GEAR["z"], face=GEAR["face"], hub_d=GEAR["hub_d"], hub_l=GEAR["hub_l"], bore=4.0)
    pinion = Pos(0, APEX_Y, PINION_BACK_Z) * Rot(180, 0, 0) * Rot(0, 0, 9) * pin   # local +Z → −Z
    moving.append(col(pinion, C_NYLON, "pinion bevel gear"))
    mot = Pos(0, APEX_Y, MOTOR_FACE_Z) * Rot(180, 0, 0) * Rot(0, 0, 90) * gearmotor()  # shaft → −Z, M3 holes on X
    moving.append(mot)
    for sx in (1, -1):
        moving.append(col(zcyl(LM4["od"] / 2, BRIDGE_Z0, BRIDGE_Z0 + LM4["l"], x=sx * ROD_X)
                          - zcyl(ROD_D / 2, 0, 100, x=sx * ROD_X), C_STEEL, "LM4UU"))
    moving = [Pos(0, 0, dz) * m for m in moving]

    fixed = []      # moves with the hub, not with the carriage
    rod_z0 = BRIDGE_Z0 - STATIC_DEFL - 3.0
    for sx in (1, -1):
        fixed.append(col(zcyl(ROD_D / 2, rod_z0, TOWER_Z0 + 22, x=sx * ROD_X), C_STEEL, "rod Ø4"))
        fixed.append(col(zcyl(4.0, rod_z0, rod_z0 + 3, x=sx * ROD_X) - zcyl(ROD_D / 2, 0, 200, x=sx * ROD_X),
                         C_DARK, "stop collar"))
        fixed.append(spring(TOWER_Z0 - (BRIDGE_Z0 + BRIDGE_H) - dz, sx * ROD_X) if dz == 0 else
                     Pos(0, 0, dz) * spring(TOWER_Z0 - (BRIDGE_Z0 + BRIDGE_H) - dz, sx * ROD_X))
    fixed.append(col(box(-7, 7, -6, 6, BRIDGE_Z0 + BRIDGE_H + BUMP, BRIDGE_Z0 + BRIDGE_H + BUMP + 2.0),
                     C_DARK, "bump pad"))
    return moving, fixed


# ------------------------------------------------------------------ world placement
def pod_plane(az_deg):
    th = radians(P.CONTACT_ANGLE)
    a = radians(az_deg)
    er = Vector(cos(a), 0, sin(a))
    up = Vector(0, 1, 0)
    n = er * sin(th) - up * cos(th)                 # outward normal at contact
    axle = er * cos(th) + up * sin(th)
    t = Vector(-sin(a), 0, cos(a))
    c = n * (P.SHELL_R_IN - RW)
    return Plane(origin=c, x_dir=t, z_dir=-n), axle


def to_world(shape, az, lift):
    pl, _ = pod_plane(az)
    return Pos(0, lift, 0) * (Location(pl) * shape)


def hub_cut_world(lift):
    """Half-space below the hub plate underside (world)."""
    y = P.HUB_Y_DOWN - HUB_T + lift
    return Pos(0, y - 500, 0) * Box(2000, 1000, 2000)


def tower_world(az, lift):
    t = to_world(tower_raw(), az, lift) & hub_cut_world(lift)
    # 2×M3 vertical screws into the hub plate
    pl, _ = pod_plane(az)
    for sx in (1, -1):
        p = to_world(Pos(sx * (ROD_X - 9), 0, 0) * Box(0.1, 0.1, 0.1), az, lift).center()
        t -= Pos(p.X, P.HUB_Y_DOWN - HUB_T + lift - 12, p.Z) * Rot(-90, 0, 0) * Cylinder(1.25, 13, align=MIN_Z)
    return col(t, C_PRINT, "tower")


def tower_top_xz(az):
    """World x/z of a tower centre at the hub plate plane, for hub plate holes."""
    pl, _ = pod_plane(az)
    pts = []
    for sx in (1, -1):
        p = to_world(Pos(sx * (ROD_X - 9), 0, 0) * Box(0.1, 0.1, 0.1), az, 0).center()
        pts.append((p.X, p.Z))
    return pts


def polar(r, az):
    return r * cos(radians(az)), r * sin(radians(az))


def hplate(y_top, t, shape2d):
    """Horizontal plate in world: 2D shape in the x/z plane (sketch x → world x, sketch y → world z)."""
    f = Plane.XZ * shape2d
    s = extrude(f, amount=-t)                         # Plane.XZ normal is −y; extrude toward +y … check below
    bb = s.bounding_box()
    return Pos(0, y_top - bb.max.Y, 0) * s


@lru_cache
def hub_plate():
    sk = Circle(66)
    s = hplate(P.HUB_Y_DOWN, HUB_T, sk)
    holes = [Pos(0, 0, 0) * Circle(5.4)]
    for k in range(4):                                       # T8 flange nut, 4× M3 on PCD 16
        holes.append(Pos(*_skxy(polar(8, 45 + 90 * k))) * Circle(1.7))
    for az in P.GUIDE_ROD_AZ:                               # LM6UU (Ø12 × 19) bores
        holes.append(Pos(*_skxy(polar(P.GUIDE_ROD_R, az))) * Circle(6.0))
    holes.append(Pos(*_skxy(polar(P.GUIDE_ROD_R, 60))) * Circle(4.5))   # carbon post clearance
    for az in P.WHEEL_AZIMUTHS:
        for xz in tower_top_xz(az):
            holes.append(Pos(*_skxy(xz)) * Circle(1.7))
    for h in holes:
        s -= hplate(P.HUB_Y_DOWN + 1, HUB_T + 2, h)
    return col(s, C_LASER, "hub plate")


def _skxy(xz):
    """World (x, z) → sketch coords on Plane.XZ (sketch y maps to world −z)."""
    return xz[0], -xz[1]


@lru_cache
def lm6_housings():
    parts = []
    for az in P.GUIDE_ROD_AZ:
        x, z = polar(P.GUIDE_ROD_R, az)
        h = Pos(x, P.HUB_Y_DOWN - HUB_T - 19, z) * Rot(-90, 0, 0) * Cylinder(6.0, 19, align=MIN_Z)
        h -= Pos(x, -300, z) * Rot(-90, 0, 0) * Cylinder(3.0, 600, align=MIN_Z)
        boss = Pos(x, P.HUB_Y_DOWN - HUB_T - 19, z) * Rot(-90, 0, 0) * Cylinder(9.0, 19, align=MIN_Z) - h
        parts.append(col(h, C_STEEL, "LM6UU"))
        parts.append(col(boss - Pos(x, -300, z) * Rot(-90, 0, 0) * Cylinder(6.0, 600, align=MIN_Z), C_PRINT, "LM6UU housing"))
    return parts


@lru_cache
def nut():
    y = P.HUB_Y_DOWN
    fl = Pos(0, y, 0) * Rot(-90, 0, 0) * Cylinder(11, 3.5, align=MIN_Z)
    body = Pos(0, y - 3 - 10, 0) * Rot(-90, 0, 0) * Cylinder(5.1, 13, align=MIN_Z)
    n = (fl + body) - Pos(0, y - 20, 0) * Rot(-90, 0, 0) * Cylinder(4.0, 40, align=MIN_Z)
    return col(n, C_BRASS, "Tr8×1.5 flange nut")


@lru_cache
def shelf():
    y_bot = P.BATTERY_SHELF_Y
    sk = Rectangle(130, 120)
    s = hplate(y_bot + SHELF_T, SHELF_T, Pos(*_skxy((0, 0))) * sk)
    for az in list(P.GUIDE_ROD_AZ) + [60]:
        s -= hplate(y_bot + SHELF_T + 1, SHELF_T + 2, Pos(*_skxy(polar(P.GUIDE_ROD_R, az))) * Circle(3.0))
    s -= hplate(y_bot + SHELF_T + 1, SHELF_T + 2, Circle(4.5))              # screw + bearing
    return col(s, C_LASER, "battery shelf")


@lru_cache
def battery():
    y0 = P.BATTERY_SHELF_Y + SHELF_T
    b = Pos(27.5, y0 + 19, 0) * Box(35, 38, 106)
    return col(b, C_BATT, "6S 2200 battery")


def base_plate_y():
    return P.BOTTOM_SQUARE_Y + P.CAGE_STRUT_D / 2      # sits on top of the bottom-square struts


@lru_cache
def guide_rods():
    parts = []
    y0, y1 = base_plate_y() + BASE_T, P.BATTERY_SHELF_Y + SHELF_T
    for az in P.GUIDE_ROD_AZ:
        x, z = polar(P.GUIDE_ROD_R, az)
        parts.append(col(Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(3.0, y1 - y0, align=MIN_Z), C_STEEL, "rod Ø6"))
    x, z = polar(P.GUIDE_ROD_R, 60)
    parts.append(col(Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(3.0, y1 - y0, align=MIN_Z), C_DARK, "carbon post Ø6"))
    return parts


@lru_cache
def lead_screw():
    s = Pos(0, -125, 0) * Rot(-90, 0, 0) * Cylinder(4.0, 125, align=MIN_Z)
    return col(s, C_STEEL, "Tr8×1.5 lead screw (Part 2)")


# ------------------------------------------------------------------ context (not part of P3)
@lru_cache
def cage_struts():
    from part3.analysis.requirements_check import cage_struts as cs
    parts = []
    for name, a, b in cs():
        a, b = Vector(*a), Vector(*b)
        d = b - a
        c = Solid.make_cylinder(P.CAGE_STRUT_D / 2, d.length, Plane(origin=a, z_dir=d))
        parts.append(c)
    return col(Compound(children=parts), C_DARK, "cage struts (context)")


@lru_cache
def shell_lower():
    outer = Sphere(P.SHELL_R_IN + 1.0)
    inner = Sphere(P.SHELL_R_IN)
    s = (outer - inner) & Pos(0, -125, 0) * Box(600, 250, 600)
    return col(s, Color(0.55, 0.75, 0.9), "shell inner face (context)")


@lru_cache
def props():
    parts = []
    for az in P.PROP_AZIMUTHS:
        x, z = polar(P.PROP_HUB_R, az)
        parts.append(Pos(x, P.PROP_PLANE_Y, z) * Rot(-90, 0, 0) * Cylinder(P.PROP_D / 2, 2, align=CEN))
    return col(Compound(children=parts), Color(0.85, 0.3, 0.25), "5in prop discs (context)")


# ------------------------------------------------------------------ base plate with pod windows
def base_plate(pod_shapes_by_state):
    """220 square on the bottom-square struts, windows cut wherever any pod passes through it."""
    import numpy as np
    from scipy.spatial import ConvexHull
    y_bot = base_plate_y()
    slab = Pos(0, y_bot + BASE_T / 2, 0) * Box(400, BASE_T + 2, 400)
    half = P.BOTTOM_SQUARE / 2 + 3
    plate = hplate(y_bot + BASE_T, BASE_T, Rectangle(2 * half, 2 * half))
    windows = []
    for az, shapes in pod_shapes_by_state.items():
        pts = []
        for sh in shapes:
            cut = sh & slab
            if cut is None or not cut.solids():
                continue
            for v in cut.vertices():
                pts.append((v.X, v.Z))
            for e in cut.edges():
                for k in range(9):
                    p = e @ (k / 8)
                    pts.append((p.X, p.Z))
        if len(pts) < 3:
            continue
        pts = np.array(pts)
        hull = pts[ConvexHull(pts).vertices]
        poly = Polygon(*[_skxy(tuple(p)) for p in hull], align=None)
        poly = offset(poly, amount=5.0)
        windows.append(poly)
        plate -= hplate(y_bot + BASE_T + 1, BASE_T + 2, poly)
    for az in list(P.GUIDE_ROD_AZ) + [60]:
        plate -= hplate(y_bot + BASE_T + 1, BASE_T + 2, Pos(*_skxy(polar(P.GUIDE_ROD_R, az))) * Circle(3.0))
    return col(plate, C_LASER, "base plate")


# ------------------------------------------------------------------ assembly
def assembly(lift=0.0, context=True):
    parts = []
    pod_world = {}
    for az in P.WHEEL_AZIMUTHS:
        moving, fixed = pod(lift)
        w = [to_world(m, az, lift) for m in moving + fixed]
        w.append(tower_world(az, lift))
        pod_world[az] = w
        parts += w
    hub = [hub_plate(), nut()] + lm6_housings()
    parts += [Pos(0, lift, 0) * h for h in hub]
    parts += [shelf(), battery(), lead_screw()] + guide_rods()
    ctx = [cage_struts(), props(), shell_lower()] if context else []
    return parts, ctx, pod_world


def export(name, parts):
    OUT.mkdir(parents=True, exist_ok=True)
    c = Compound(children=parts)
    export_gltf(c, str(OUT / f"{name}.glb"), binary=True, linear_deflection=0.08, angular_deflection=0.35)
    return c


if __name__ == "__main__":
    import time
    t0 = time.time()
    report = dict(gear=GI, apex_y=APEX_Y, gear_back_y=GEAR_BACK_Y, motor_face_z=MOTOR_FACE_Z,
                  spring_loaded_len=SPRING_LOADED_L, tower_z0=TOWER_Z0)
    print(json.dumps(report, indent=1, default=float))
    states = {}
    for lift in (0.0, P.LIFT_STROKE):
        parts, ctx, pw = assembly(lift)
        states[lift] = pw
        tag = "rolling" if lift == 0 else "lifted"
        export(f"p3_assembly_{tag}", parts)
        print(tag, "exported", round(time.time() - t0, 1), "s")
    # base plate from both states (+ bump: carriage up by BUMP in the rolling state)
    by_az = {az: states[0.0][az] + states[P.LIFT_STROKE][az] for az in P.WHEEL_AZIMUTHS}
    bp = base_plate(by_az)
    export("p3_base_plate", [bp])
    ctx = [cage_struts(), props(), shell_lower()]
    export("p3_context_cage", [cage_struts()])
    export("p3_context_props", [props()])
    export("p3_context_shell", [shell_lower()])
    export_step(bp, str(OUT / "p3_base_plate.step"))
    print("done", round(time.time() - t0, 1), "s")
