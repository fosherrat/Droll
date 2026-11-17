"""Straight bevel (mitre) gear, printable.

Tredgold approximation: the tooth at the back cone is the involute tooth of a
virtual spur gear with N_v = N / cos(delta) teeth, wrapped onto the real pitch
circle. Sections are scaled linearly toward the cone apex (straight bevel).

Local frame: gear axis = +Z. The back face (largest pitch circle) is at z = 0,
the teeth point toward +Z and the cone apex is at z = info["apex_z"].
A hub extends to −Z behind the back face.
"""
from math import acos, atan, cos, degrees, pi, radians, sin, tan

from build123d import Align, Cylinder, Face, Polyline, Pos, Solid, Wire, loft


def _inv(a):
    return tan(a) - a


def involute_tooth(m, zv, pa_deg=20.0, clearance=0.25, backlash=0.15, n=10):
    """One tooth of a spur gear with zv teeth, as (angle, r) polar pairs measured
    from the tooth centreline. Ordered root-left → tip → root-right."""
    pa = radians(pa_deg)
    rp = m * zv / 2
    rb = rp * cos(pa)
    ra = rp + m
    rf = rp - (1 + clearance) * m
    t_half = (pi * m / 2 - backlash / 2) / (2 * rp)      # half-thickness angle at pitch
    half_pitch = pi / zv

    def flank_angle(r):
        a = 0.0 if r <= rb else acos(rb / r)
        return t_half + _inv(pa) - _inv(a)

    r0 = max(rb, rf)
    radii = [r0 + (ra - r0) * i / n for i in range(n + 1)]
    left = [(-flank_angle(r), r) for r in radii]            # base → tip
    right = [(flank_angle(r), r) for r in radii[::-1]]      # tip → base
    pts = [(-half_pitch, rf), (left[0][0], rf)] + left + right + [(right[-1][0], rf)]   # next tooth starts at +half_pitch
    return pts, dict(rp=rp, ra=ra, rf=rf)


def bevel_gear(m=1.0, z=20, z_mate=20, face=5.0, bore=4.0, hub_d=12.0, hub_l=6.0,
               pa_deg=20.0, backlash=0.15, steps=3):
    delta = atan(z / z_mate)                 # pitch cone angle
    rp = m * z / 2                           # pitch radius at the back cone
    R = rp / sin(delta)                      # cone distance
    zv = z / cos(delta)
    tooth, v = involute_tooth(m, zv, pa_deg, backlash=backlash)
    pitch_ang = 2 * pi / z

    apex = R * cos(delta)
    back = []                                   # 3D points on the back cone (heel)
    for k in range(z):
        for ang, r in tooth:
            sx = r - v["rp"]                    # radial offset from the virtual pitch circle
            rr = rp + sx * cos(delta)           # back-cone development
            dz = sx * sin(delta)                # outward along the back cone also moves toward the apex
            a = k * pitch_ang + ang * v["rp"] / rp     # development keeps arc length: φ = φ_v / cos δ
            back.append((rr * sin(a), rr * cos(a), dz))

    def section(zpos):
        """Exact planar slice: every flank line passes through the apex."""
        pts = []
        for x, y, zz in back:
            t = (apex - zpos) / (apex - zz)
            pts.append((x * t, y * t, zpos))
        return Face(Wire(Polyline(*pts, close=True).edges()))

    z_start = min(p[2] for p in back) - 0.5     # a bit behind the heel; trimmed by the back cone below
    z_toe = face * cos(delta)
    secs = [section(z_start + (z_toe - z_start) * i / steps) for i in range(steps + 1)]
    teeth = loft(secs, ruled=True)
    # trim the heel with the back cone: keep z >= (r - rp) * tan(delta)
    bc_apex = -rp * tan(delta)
    H = 40.0
    back_cone = Pos(0, 0, bc_apex) * Solid.make_cone(0.001, H / tan(delta), H)
    teeth = teeth & back_cone
    # root cone: through the heel root point and the apex, so mate tips clear it
    r_root = rp - 1.25 * m * cos(delta) - 0.05
    z_root = -1.25 * m * sin(delta)
    r_toe = r_root * (apex - z_toe) / (apex - z_root)
    body = Pos(0, 0, z_root) * Solid.make_cone(r_root, r_toe, z_toe - z_root)
    body = body & back_cone
    hub = Pos(0, 0, -hub_l) * Cylinder(hub_d / 2, hub_l + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    gear = teeth.fuse(body).fuse(hub).clean()
    gear -= Pos(0, 0, -hub_l - 1) * Cylinder(bore / 2, hub_l + face + 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    info = dict(m=m, z=z, pitch_d=2 * rp, cone_distance=R, delta_deg=degrees(delta),
                apex_z=R * cos(delta), outer_d=2 * (rp + m * cos(delta)), face=face, hub_l=hub_l,
                bore=bore)
    return gear, info


if __name__ == "__main__":
    import time
    t = time.time()
    g, info = bevel_gear()
    print(info)
    print("valid", g.is_valid, "volume", round(g.volume, 1), "time", round(time.time() - t, 1))
