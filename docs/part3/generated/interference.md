# DRL-P3 interference check

Exact distances (BRepExtrema). Designed contacts are checked for overlap volume.

## rolling (lift 0.0 mm, bump 0.0 mm)

- Collisions: **16**
  - ❌ carriage@0 ↔ wheel flange@0 (overlap 0.0 mm³)
  - ❌ carriage@0 ↔ spacer@0 (overlap 0.0 mm³)
  - ❌ LM4UU@0 ↔ spring@0 (overlap 0.1 mm³)
  - ❌ LM4UU@0 ↔ spring@0 (overlap 0.1 mm³)
  - ❌ carriage@120 ↔ wheel flange@120 (overlap 0.0 mm³)
  - ❌ carriage@120 ↔ spacer@120 (overlap 0.0 mm³)
  - ❌ LM4UU@120 ↔ spring@120 (overlap 0.1 mm³)
  - ❌ LM4UU@120 ↔ spring@120 (overlap 0.1 mm³)
  - ❌ carriage@240 ↔ wheel flange@240 (overlap 0.0 mm³)
  - ❌ carriage@240 ↔ spacer@240 (overlap 0.0 mm³)
  - ❌ LM4UU@240 ↔ spring@240 (overlap 0.1 mm³)
  - ❌ LM4UU@240 ↔ spring@240 (overlap 0.1 mm³)
  - ❌ hub plate ↔ LM6UU (overlap 0.0 mm³)
  - ❌ hub plate ↔ LM6UU (overlap 0.0 mm³)
  - ❌ 6S 2200 battery ↔ rod Ø6 (overlap 0.0 mm³)
  - ❌ 6S 2200 battery ↔ carbon post Ø6 (overlap 0.0 mm³)
- Designed contacts with overlap > 0.5 mm³: **3**
  - ⚠️ omni wheel Nexus 14135@0 ↔ wheel flange@0: 28.5 mm³
  - ⚠️ omni wheel Nexus 14135@120 ↔ wheel flange@120: 28.5 mm³
  - ⚠️ omni wheel Nexus 14135@240 ↔ wheel flange@240: 28.5 mm³
- Pairs closer than 3 mm (not touching): 74
  - wheel bevel gear@0 ↔ pinion bevel gear@0: 0.05 mm
  - wheel bevel gear@120 ↔ pinion bevel gear@120: 0.05 mm
  - wheel bevel gear@240 ↔ pinion bevel gear@240: 0.05 mm
  - omni wheel Nexus 14135@120 ↔ axle Ø5@120: 0.05 mm
  - omni wheel Nexus 14135@240 ↔ axle Ø5@240: 0.05 mm
  - omni wheel Nexus 14135@0 ↔ axle Ø5@0: 0.05 mm
  - spacer@0 ↔ axle Ø5@0: 0.10 mm
  - spacer@120 ↔ axle Ø5@120: 0.10 mm
  - spacer@240 ↔ axle Ø5@240: 0.10 mm
  - spring@240 ↔ tower@240: 0.40 mm
  - spring@120 ↔ tower@120: 0.40 mm
  - spring@120 ↔ tower@120: 0.40 mm

| Pod vs context (mm) | 0° | 120° | 240° |
|---|---|---|---|
| cage strut | 5.8 | 10.2 | 10.2 |
| prop disc | 26.4 | 21.7 | 21.7 |
| shell | 0.2 | 0.2 | 0.2 |

| Clearance | mm |
|---|---|
| pod 0° ↔ pod 120° | 10.4 |
| pod 0° ↔ pod 240° | 10.4 |
| pod 120° ↔ pod 240° | 10.4 |
| pod 0° ↔ centre rods / screw | 11.6 |
| pod 120° ↔ centre rods / screw | 11.6 |
| pod 240° ↔ centre rods / screw | 11.6 |

## bump +10 (lift 0.0 mm, bump 10.0 mm)

- Collisions: **30**
  - ❌ omni wheel Nexus 14135@0 ↔ rod Ø4@0 (overlap 3.8 mm³)
  - ❌ omni wheel Nexus 14135@0 ↔ stop collar@0 (overlap 3.0 mm³)
  - ❌ omni wheel Nexus 14135@0 ↔ rod Ø4@0 (overlap 3.8 mm³)
  - ❌ omni wheel Nexus 14135@0 ↔ stop collar@0 (overlap 34.3 mm³)
  - ❌ carriage@0 ↔ wheel flange@0 (overlap 0.0 mm³)
  - ❌ carriage@0 ↔ spacer@0 (overlap 0.0 mm³)
  - ❌ carriage@0 ↔ bump pad@0 (overlap 0.0 mm³)
  - ❌ LM4UU@0 ↔ spring@0 (overlap 0.2 mm³)
  - ❌ LM4UU@0 ↔ spring@0 (overlap 0.2 mm³)
  - ❌ omni wheel Nexus 14135@120 ↔ stop collar@120 (overlap 3.0 mm³)
  - ❌ omni wheel Nexus 14135@120 ↔ rod Ø4@120 (overlap 3.8 mm³)
  - ❌ omni wheel Nexus 14135@120 ↔ stop collar@120 (overlap 34.3 mm³)
  - ❌ carriage@120 ↔ wheel flange@120 (overlap 0.0 mm³)
  - ❌ carriage@120 ↔ spacer@120 (overlap 0.0 mm³)
  - ❌ carriage@120 ↔ bump pad@120 (overlap 0.0 mm³)
  - ❌ LM4UU@120 ↔ spring@120 (overlap 0.2 mm³)
  - ❌ LM4UU@120 ↔ spring@120 (overlap 0.2 mm³)
  - ❌ omni wheel Nexus 14135@240 ↔ rod Ø4@240 (overlap 3.8 mm³)
  - ❌ omni wheel Nexus 14135@240 ↔ stop collar@240 (overlap 34.3 mm³)
  - ❌ omni wheel Nexus 14135@240 ↔ rod Ø4@240 (overlap 3.8 mm³)
  - ❌ omni wheel Nexus 14135@240 ↔ stop collar@240 (overlap 34.3 mm³)
  - ❌ carriage@240 ↔ wheel flange@240 (overlap 0.0 mm³)
  - ❌ carriage@240 ↔ spacer@240 (overlap 0.0 mm³)
  - ❌ carriage@240 ↔ bump pad@240 (overlap 0.0 mm³)
  - ❌ LM4UU@240 ↔ spring@240 (overlap 0.2 mm³)
  - ❌ LM4UU@240 ↔ spring@240 (overlap 0.2 mm³)
  - ❌ hub plate ↔ LM6UU (overlap 0.0 mm³)
  - ❌ hub plate ↔ LM6UU (overlap 0.0 mm³)
  - ❌ 6S 2200 battery ↔ rod Ø6 (overlap 0.0 mm³)
  - ❌ 6S 2200 battery ↔ carbon post Ø6 (overlap 0.0 mm³)
- Designed contacts with overlap > 0.5 mm³: **3**
  - ⚠️ omni wheel Nexus 14135@0 ↔ wheel flange@0: 28.5 mm³
  - ⚠️ omni wheel Nexus 14135@120 ↔ wheel flange@120: 28.5 mm³
  - ⚠️ omni wheel Nexus 14135@240 ↔ wheel flange@240: 28.5 mm³
- Pairs closer than 3 mm (not touching): 66
  - wheel bevel gear@0 ↔ pinion bevel gear@0: 0.05 mm
  - wheel bevel gear@120 ↔ pinion bevel gear@120: 0.05 mm
  - wheel bevel gear@240 ↔ pinion bevel gear@240: 0.05 mm
  - omni wheel Nexus 14135@120 ↔ axle Ø5@120: 0.05 mm
  - omni wheel Nexus 14135@240 ↔ axle Ø5@240: 0.05 mm
  - omni wheel Nexus 14135@0 ↔ axle Ø5@0: 0.05 mm
  - spacer@0 ↔ axle Ø5@0: 0.10 mm
  - spacer@240 ↔ axle Ø5@240: 0.10 mm
  - spacer@120 ↔ axle Ø5@120: 0.10 mm
  - spring@240 ↔ tower@240: 0.40 mm
  - spring@240 ↔ tower@240: 0.40 mm
  - spring@120 ↔ tower@120: 0.40 mm

| Pod vs context (mm) | 0° | 120° | 240° |
|---|---|---|---|
| cage strut | 5.8 | 13.3 | 13.3 |
| prop disc | 26.4 | 21.7 | 21.7 |
| shell | 10.2 | 10.2 | 10.2 |

| Clearance | mm |
|---|---|
| pod 0° ↔ pod 120° | 3.1 |
| pod 0° ↔ pod 240° | 3.1 |
| pod 120° ↔ pod 240° | 3.1 |
| pod 0° ↔ centre rods / screw | 5.8 |
| pod 120° ↔ centre rods / screw | 5.8 |
| pod 240° ↔ centre rods / screw | 5.8 |

## lifted (lift 22.5 mm, bump 0.0 mm)

- Collisions: **22**
  - ❌ carriage@0 ↔ wheel flange@0 (overlap 0.0 mm³)
  - ❌ carriage@0 ↔ spacer@0 (overlap 0.0 mm³)
  - ❌ LM4UU@0 ↔ stop collar@0 (overlap 0.0 mm³)
  - ❌ LM4UU@0 ↔ spring@0 (overlap 0.1 mm³)
  - ❌ LM4UU@0 ↔ stop collar@0 (overlap 0.0 mm³)
  - ❌ LM4UU@0 ↔ spring@0 (overlap 0.1 mm³)
  - ❌ carriage@120 ↔ wheel flange@120 (overlap 0.0 mm³)
  - ❌ carriage@120 ↔ spacer@120 (overlap 0.0 mm³)
  - ❌ LM4UU@120 ↔ stop collar@120 (overlap 0.0 mm³)
  - ❌ LM4UU@120 ↔ spring@120 (overlap 0.1 mm³)
  - ❌ LM4UU@120 ↔ stop collar@120 (overlap 0.0 mm³)
  - ❌ LM4UU@120 ↔ spring@120 (overlap 0.1 mm³)
  - ❌ carriage@240 ↔ wheel flange@240 (overlap 0.0 mm³)
  - ❌ carriage@240 ↔ spacer@240 (overlap 0.0 mm³)
  - ❌ LM4UU@240 ↔ stop collar@240 (overlap 0.0 mm³)
  - ❌ LM4UU@240 ↔ spring@240 (overlap 0.1 mm³)
  - ❌ LM4UU@240 ↔ stop collar@240 (overlap 0.0 mm³)
  - ❌ LM4UU@240 ↔ spring@240 (overlap 0.1 mm³)
  - ❌ hub plate ↔ LM6UU (overlap 0.0 mm³)
  - ❌ hub plate ↔ LM6UU (overlap 0.0 mm³)
  - ❌ 6S 2200 battery ↔ rod Ø6 (overlap 0.0 mm³)
  - ❌ 6S 2200 battery ↔ carbon post Ø6 (overlap 0.0 mm³)
- Designed contacts with overlap > 0.5 mm³: **3**
  - ⚠️ omni wheel Nexus 14135@0 ↔ wheel flange@0: 28.5 mm³
  - ⚠️ omni wheel Nexus 14135@120 ↔ wheel flange@120: 28.5 mm³
  - ⚠️ omni wheel Nexus 14135@240 ↔ wheel flange@240: 28.5 mm³
- Pairs closer than 3 mm (not touching): 65
  - wheel bevel gear@0 ↔ pinion bevel gear@0: 0.05 mm
  - wheel bevel gear@120 ↔ pinion bevel gear@120: 0.05 mm
  - wheel bevel gear@240 ↔ pinion bevel gear@240: 0.05 mm
  - omni wheel Nexus 14135@240 ↔ axle Ø5@240: 0.05 mm
  - omni wheel Nexus 14135@0 ↔ axle Ø5@0: 0.05 mm
  - omni wheel Nexus 14135@120 ↔ axle Ø5@120: 0.05 mm
  - spacer@240 ↔ axle Ø5@240: 0.10 mm
  - spacer@120 ↔ axle Ø5@120: 0.10 mm
  - spacer@0 ↔ axle Ø5@0: 0.10 mm
  - spring@240 ↔ tower@240: 0.40 mm
  - spring@0 ↔ tower@0: 0.40 mm
  - spring@0 ↔ tower@0: 0.40 mm

| Pod vs context (mm) | 0° | 120° | 240° |
|---|---|---|---|
| cage strut | 0.0 | 4.9 | 4.9 |
| prop disc | 17.6 | 14.1 | 14.1 |
| shell | 17.4 | 17.4 | 17.4 |

| Clearance | mm |
|---|---|
| pod 0° ↔ pod 120° | 12.4 |
| pod 0° ↔ pod 240° | 12.4 |
| pod 120° ↔ pod 240° | 12.4 |
| pod 0° ↔ centre rods / screw | 5.3 |
| pod 120° ↔ centre rods / screw | 5.3 |
| pod 240° ↔ centre rods / screw | 5.3 |

Shell distance is 0 in the rolling states by design (wheel contact).
