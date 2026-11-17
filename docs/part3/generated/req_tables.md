### Geometry (computed)

| Item | Value |
|---|---|
| Contact point | r 103.1, y -221.1 |
| Wheel centre | r 90.9, y -194.9 |
| Bottom square plane | y -160.8 |
| Lower side face height | 115.9 |
| Prop tip to shell inner | 4.3 |

### Lift sweep (worst of 3 wheels; wheel envelope Ø58 × 25)

| Lift | Wheel→strut | Nearest strut | Wheel→prop disc | Wheel→shell | Hub→shelf |
|---|---|---|---|---|---|
| 0.0 | 16.3 | bottom-square (wheel @0°) | 58.3 | contact | 28.0 |
| 10.0 | 12.0 | bottom-square (wheel @0°) | 50.7 | 5.8 | 18.0 |
| 15.0 | 9.8 | bottom-square (wheel @120°) | 45.7 | 10.1 | 13.0 |
| 20.0 | 7.3 | bottom-square (wheel @120°) | 40.7 | 14.5 | 8.0 |
| 22.5 | 6.1 | bottom-square (wheel @120°) | 38.2 | 16.6 | 5.5 |
| 25.0 | 5.0 | bottom-square (wheel @120°) | 35.7 | 18.8 | 3.0 |
| 30.0 | 3.1 | bottom-square (wheel @120°) | 30.7 | 23.0 | -2.0 |
| 35.0 | 1.5 | bottom-square (wheel @120°) | 25.7 | 27.3 | -7.0 |
| 40.0 | -0.5 | bottom-square (wheel @0°) | 20.7 | 31.5 | -12.0 |

Wheel envelope touches a strut at **39.0 mm** lift; hub meets battery shelf at **28 mm**.

### Room for a motor pointing inward (25 mm class)

| Bevel side | Max body length | Limited by | Other limits |
|---|---|---|---|
| equator side | **52 mm** | prop disc | hub plate 66, lead-screw nut 191 |
| pole side | **86 mm** | hub plate | lead-screw nut 94, other motors 118 |

### Drive (pendulum-limited, frame tilt 30°, hanging 2.93 kg, COM −50 mm)

| Case | Accel m/s² | Shell torque N·m | Wheel force N | Wheel torque peak N·m | Wheel rpm | Normal load N | Traction margin | Peak W |
|---|---|---|---|---|---|---|---|---|
| v=0.5 m/s | 0.78 | 0.82 | 2.46 | 0.107 | 199 | 10.6 | 2.1× | 2.2 |
| v=1.0 m/s | 0.78 | 0.82 | 2.46 | 0.107 | 345 | 10.6 | 2.1× | 3.9 |

COM height sensitivity (v = 1.0 m/s):

| COM below centre | Accel m/s² | Wheel torque peak N·m | Max slope at 30° tilt |
|---|---|---|---|
| d=30mm | 0.44 | 0.061 | 2.7° |
| d=50mm | 0.78 | 0.107 | 4.5° |
| d=80mm | 1.35 | 0.187 | 7.3° |
| d=120mm | 2.30 | 0.318 | 11.0° |

### Derived motor requirements (per wheel, at the wheel axle)

| Requirement | Value |
|---|---|
| Loaded speed | 345 rpm |
| No-load speed (buy) | ≥ 459 rpm |
| Continuous torque | 0.071 N·m |
| Peak torque incl. losses | 0.107 N·m |
| Stall torque (buy) | ≥ 0.32 N·m |
| Peak mechanical power | 3.9 W |
| Tread for ±1.5° shell yaw | 2.70 mm |
| Encoder: tread per count | ≤ 0.54 mm (≥ 337 counts / wheel rev) |
