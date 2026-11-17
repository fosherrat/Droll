"""Droll shared design parameters — single source of truth.

Units: mm, kg, N, s, degrees (unless a name says otherwise).
Frame: origin at the shell (sphere) centre, +y up, x/z horizontal.
Azimuth is measured from +x toward +z. Props sit at azimuth 0/90/180/270.

Each value carries a status tag in the comment:
  [fixed]    agreed in DRL-SPEC rev 0.3, change only by spec revision
  [proposed] proposed by a part sheet, still needs team sign-off
  [assumed]  planning assumption, replace with measured/datasheet value
  [open]     conflicting sources, decision needed (see docs/part3/00-requirements.md)
"""
from math import sqrt

# ---------------------------------------------------------------- shell
SHELL_R_OUT = 250.0          # [fixed] Ø500 outer
SHELL_WALL = 6.0             # [fixed] lattice PETG
SHELL_R_IN = SHELL_R_OUT - SHELL_WALL   # 244, wheel running surface
SHELL_KEEPOUT_R = 230.0      # [fixed] nothing on the shell inside r 230 (hinge pads)
SHELL_MASS = 0.77            # [assumed] hemisphere + petals + hinges

# ---------------------------------------------------------------- cage
CAGE_CORNER_R = 223.7        # [fixed] all cage corners on this sphere
CAGE_STRUT_D = 6.0           # [fixed] carbon tube
CAGE_EDGE = 160.0            # [fixed] standard strut length
BOTTOM_SQUARE = 230.0        # [proposed] was 160 → 220 (25° contact) → 230 (lifted pod cleared 3.8 mm, see P3 D8)
BOTTOM_SQUARE_Y = -sqrt(CAGE_CORNER_R**2 - 2 * (BOTTOM_SQUARE / 2) ** 2)  # ≈ -153.6
EQUATOR_SQUARE_HALF = CAGE_EDGE / 2                 # side-square half width (80)
SIDE_FACE_X = CAGE_EDGE / 2 * (1 + sqrt(2))         # ≈ 193.1, side squares' plane
LOWER_SIDE_TOP_Y = -CAGE_EDGE / 2                   # -80, top edge of lower side faces

# ---------------------------------------------------------------- props (option A, level)
PROP_D = 127.0               # [fixed] 5"
PROP_AZIMUTHS = (0, 90, 180, 270)
PROP_HUB_R = 152.0           # [proposed] with 22 cm square
PROP_PLANE_Y = -105.0        # [proposed]
PROP_CLEAR_MIN = 10.0        # [assumed] keep solid parts this far from a prop disc

# ---------------------------------------------------------------- wheel module (Part 3)
WHEEL_COUNT = 3
WHEEL_AZIMUTHS = (0, 120, 240)          # [proposed]
CONTACT_ANGLE = 25.0                    # [proposed] from the bottom pole
WHEEL_DIRECTION = "azimuth"             # [fixed] ballbot: push sideways
WHEEL_D = 58.0                          # [fixed] Nexus 14135 (step 1)
WHEEL_W = 26.0                          # [fixed] Nexus 14135 drawing
POD_SPRING_TRAVEL_STATIC = 2.7          # [proposed] off the stop when loaded
POD_BUMP_TRAVEL = 10.0                  # [proposed]

# hub plate / lift
HUB_Y_DOWN = -104.0                     # [fixed] D2: Part 3 value; Part 2 must move its screw up
LIFT_STROKE = 22.5                      # [fixed] D1: Tr8x1.5 x 15 turns
LIFT_STROKE_MIN, LIFT_STROKE_MAX = 15.0, 25.0   # [proposed] acceptable window
BATTERY_SHELF_Y = -76.0                 # [proposed] fixed shelf above the hub
GUIDE_ROD_D = 6.0
GUIDE_ROD_R = 45.0
GUIDE_ROD_AZ = (180, 300)

# chosen purchased parts (step 1) — see docs/part3/01-part-selection.md
MOTOR = "Pololu #4843 20.4:1 25Dx65L HP 12V, 48 CPR"
MOTOR_D = 25.0                          # gearbox / can diameter
MOTOR_BODY_L = 64.5                     # gearbox 19 + motor 30.8 + encoder 14.7
MOTOR_SHAFT_D, MOTOR_SHAFT_L = 4.0, 12.5   # D-shaft
MOTOR_NOLOAD_RPM, MOTOR_STALL_NM, MOTOR_STALL_A = 500, 0.73, 5.0
ENCODER_COUNTS_PER_OUT_REV = 48 * 20.4  # ≈ 979

# lead screw (owned by Part 2, mirrored here)
SCREW = "Tr8x1.5"                       # [fixed] D1, single start, self-locking
SCREW_TURNS_PER_STROKE = 15.0           # [fixed] D1

# ---------------------------------------------------------------- mass / dynamics
ROBOT_MASS = 3.7                        # [assumed] rev 0.3 estimate
HANGING_MASS = ROBOT_MASS - SHELL_MASS  # everything the wheels carry
COM_BELOW_CENTRE = 50.0                 # [assumed] hanging COM below sphere centre
PART3_MASS_BUDGET = 380.0               # g, spec budget
PART3_MASS_V1_EST = 761.0               # g, wheel sheet v1 BOM
PART3_MASS_TARGET = None                # [fixed] D6: not a driver this round; track only

# operating targets
V_MAX = 1.0                             # [fixed] D5 m/s top rolling speed (planning case)
V_NOMINAL = 0.5                         # [fixed] D5 m/s typical indoor speed
YAW_RATE = 90.0                         # [assumed] °/s spin while rolling
ALIGN_TOL = 1.5                         # [fixed] ° shell-to-frame alignment for step 2
FRAME_TILT_MAX = 30.0                   # [assumed] ° allowed pendulum tilt
MU_ROLLER = 0.5                         # [assumed] roller on PETG
LOSS_FACTOR = 1.5                       # [assumed] rollers + lattice bumps
SUPPLY_V = 12.0                         # [proposed] buck from 6S for wheel motors
