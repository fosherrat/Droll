# DRL-P3 interference check

Exact distances (BRepExtrema). Designed contacts are checked for overlap volume.

## rolling (lift 0.0 mm, bump 0.0 mm)

- Collisions: **0**
- Designed contacts with overlap > 0.5 mm³: **0**
- Pairs closer than 3 mm (not touching): 75
  - omni wheel Nexus 14135@0 ↔ wheel flange@0: 0.05 mm
  - omni wheel Nexus 14135@120 ↔ wheel flange@120: 0.05 mm
  - omni wheel Nexus 14135@240 ↔ wheel flange@240: 0.05 mm
  - wheel bevel gear@0 ↔ pinion bevel gear@0: 0.05 mm
  - wheel bevel gear@120 ↔ pinion bevel gear@120: 0.05 mm
  - wheel bevel gear@240 ↔ pinion bevel gear@240: 0.05 mm
  - omni wheel Nexus 14135@120 ↔ axle Ø5@120: 0.05 mm
  - omni wheel Nexus 14135@240 ↔ axle Ø5@240: 0.05 mm
  - omni wheel Nexus 14135@0 ↔ axle Ø5@0: 0.05 mm
  - spacer@0 ↔ axle Ø5@0: 0.10 mm
  - spacer@120 ↔ axle Ø5@120: 0.10 mm
  - spacer@240 ↔ axle Ø5@240: 0.10 mm

| Pod vs context (mm) | 0° | 120° | 240° |
|---|---|---|---|
| cage strut | 13.3 | 13.6 | 13.6 |
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

