"""Part 3 · step 2 · purchased-part models.

Local frames (both parts):
  omni wheel  : centre of the wheel at the origin, wheel axis = +Z,
                wheel mid-plane at z = 0.
  gearmotor   : centre of the gearbox front face at the origin, shaft points +Z,
                body runs toward -Z.

Run:  python3 part3/cad/vendor_parts.py
Writes part3/cad/out/{nexus14135_omni58,pololu4843_25d}.{step,glb}
"""
import sys
from functools import lru_cache
from pathlib import Path

from build123d import (Align, Axis, Box, Color, Compound, Cylinder, Location, Pos, Rot,
                       export_gltf, export_step, import_step)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "part3" / "cad" / "out"
VENDOR = ROOT / "part3" / "vendor"

# ------------------------------------------------------------------ colours
C_PLATE = Color(0.16, 0.17, 0.19)
C_ROLLER = Color(0.55, 0.57, 0.60)
C_PIN = Color(0.80, 0.80, 0.78)
C_HUB = Color(0.25, 0.26, 0.28)
C_ALU = Color(0.78, 0.79, 0.80)
C_CAN = Color(0.42, 0.43, 0.45)
C_ENC = Color(0.10, 0.10, 0.11)
C_STEEL = Color(0.70, 0.71, 0.73)
C_BRASS = Color(0.80, 0.62, 0.26)
C_PINS = Color(0.85, 0.72, 0.30)

# ------------------------------------------------------------------ omni wheel
NEXUS_STEP = VENDOR / "nexus-14135-omni58.step"
NEXUS_AXIS_MID_Y = 11.5        # wheel body spans y −2.5 … 25.5 in the vendor file
NEXUS_DROP_VOLUMES = (2499.6,)  # long servo/LEGO hub adapter: we make our own flange

# measured from the vendor STEP (see docs/part3/02-vendor-models.md)
WHEEL = dict(
    d_rolling_min=58.9, d_rolling_max=60.05,   # rolling radius varies with roller phase
    width=28.0,                                 # rollers, axial (drawing says 26)
    hub_bore=12.0, bolt_n=6, bolt_d=2.5, bolt_pcd=48.0,
)


@lru_cache
def omni_wheel() -> Compound:
    """Nexus 14135, cleaned, centred, axis +Z, coloured by role."""
    raw = import_step(str(NEXUS_STEP))
    parts = []
    for so in raw.solids():
        v = round(so.volume, 1)
        if any(abs(v - d) < 1 for d in NEXUS_DROP_VOLUMES):
            continue
        if abs(v - 1698.3) < 1:
            so.color, so.label = C_ROLLER, "roller"
        elif abs(v - 234.3) < 1:
            so.color, so.label = C_PIN, "roller pin"
        elif v > 4000:
            so.color, so.label = C_PLATE, "side plate"
        else:
            so.color, so.label = C_HUB, "hub"
        parts.append(so)
    c = Compound(children=parts, label="omni wheel Nexus 14135")
    # vendor axis is +Y; move mid-plane to 0, then turn Y→Z
    c = c.moved(Location((0, -NEXUS_AXIS_MID_Y, 0)))
    c = Rot(90, 0, 0) * c
    return c


# ------------------------------------------------------------------ gearmotor
MOTOR = dict(
    gearbox_d=25.0, gearbox_l=19.0,      # 20.4:1
    can_d=24.4, can_l=30.8,
    enc_d=25.0, enc_l=14.7,
    shaft_d=4.0, shaft_l=12.5, shaft_flat=3.5,
    boss_d=7.0, boss_l=2.5,
    m3_offset=8.5, m3_depth=6.0,
)


def gearmotor() -> Compound:
    """Pololu #4843 envelope model from the vendor dimension drawing."""
    m = MOTOR
    z0 = 0.0
    gb = Pos(0, 0, z0 - m["gearbox_l"]) * Cylinder(m["gearbox_d"] / 2, m["gearbox_l"],
                                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sy in (1, -1):    # 2×M3 tapped holes (drawn as Ø2.5 tap drill)
        gb -= Pos(0, sy * m["m3_offset"], -m["m3_depth"]) * Cylinder(1.25, m["m3_depth"],
                                                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    gb.color, gb.label = C_ALU, "gearbox"
    can = Pos(0, 0, -m["gearbox_l"] - m["can_l"]) * Cylinder(
        m["can_d"] / 2, m["can_l"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    can.color, can.label = C_CAN, "motor"
    z_enc = -m["gearbox_l"] - m["can_l"] - m["enc_l"]
    enc = Pos(0, 0, z_enc) * Cylinder(m["enc_d"] / 2, m["enc_l"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    enc.color, enc.label = C_ENC, "encoder"
    # 1×6 header, leaving radially at +Y near the motor/encoder joint
    hdr = Pos(0, m["enc_d"] / 2 + 1.5, z_enc + m["enc_l"] - 3.5) * Box(15.2, 5.0, 2.5)
    hdr.color, hdr.label = C_PINS, "encoder header"
    boss = Cylinder(m["boss_d"] / 2, m["boss_l"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    boss.color, boss.label = C_BRASS, "bushing"
    shaft = Cylinder(m["shaft_d"] / 2, m["shaft_l"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    flat = Pos(m["shaft_flat"] - m["shaft_d"] / 2 + 2, 0, m["shaft_l"] / 2 + 0.6) * Box(4, 6, m["shaft_l"] - 1)
    shaft -= flat
    shaft.color, shaft.label = C_STEEL, "D-shaft"
    return Compound(children=[gb, can, enc, hdr, boss, shaft], label="gearmotor Pololu 4843")


def export_all():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, shape in (("nexus14135_omni58", omni_wheel()), ("pololu4843_25d", gearmotor())):
        export_step(shape, str(OUT / f"{name}.step"))
        export_gltf(shape, str(OUT / f"{name}.glb"), binary=True,
                    linear_deflection=0.05, angular_deflection=0.3)
        bb = shape.bounding_box()
        print(f"{name}: size {bb.size.X:.1f} × {bb.size.Y:.1f} × {bb.size.Z:.1f} mm, "
              f"z {bb.min.Z:.1f} … {bb.max.Z:.1f}")


if __name__ == "__main__":
    export_all()
