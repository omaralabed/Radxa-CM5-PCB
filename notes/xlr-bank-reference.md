# XLR Bank Reference

## Source Folder

Reference source:

`/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`

Use this folder for XLR connector size, spacing, and mechanical reference only.
Do not use it as the Radxa electrical audio reference. For the capacitor/active
balanced XLR electrical reference, use
`/Users/viewvision/Desktop/ProComm enclosure and PCB boards` and
`notes/procomm-capacitor-xlr-audio-reference.md`.

## Source Files Checked

- `ProComm_Combo.kicad_pcb`
- `ProComm_Combo.kicad_sch`
- `Factory_Files/ProComm_Combo_factory_20260630_102652_assembly_current/README_FACTORY.md`
- `Factory_Files/ProComm_Combo_factory_20260630_102652_assembly_current/assembly/ProComm_Combo_CPL_Position_KiCad_raw.csv`
- `Factory_Files/ProComm_Combo_factory_20260630_102652_assembly_current/assembly/ProComm_Combo_BOM_PCBWay.csv`

## Connector Parts

Legacy XLR board connector basis:

- Outputs: Neutrik `NC3MAV`, male 3-pin vertical PCB XLR
- Inputs: Neutrik `NC3FAV`, female 3-pin vertical PCB XLR
- `P` / hot audio connects to XLR pin 2
- `N` / cold audio connects to XLR pin 3
- XLR pin 1 / shell pads were intentionally floating in the old board

For the Radxa CM5 product, pin 1 / shell/chassis treatment must be reviewed
again for the new balanced audio, EMC, and enclosure grounding design.

## Legacy Board Geometry

Legacy XLR board outline:

- Width: 95 mm
- Height: 230 mm
- Board outline came from Edge.Cuts in `ProComm_Combo.kicad_pcb`

Legacy XLR placement:

- Output connector footprint origins: x = 22 mm
- Input connector footprint origins: x = 73 mm
- Footprint-origin column spacing: 51 mm
- Rows: y = 17, 45, 73, 101, 129, 157, 185, 213 mm
- Row pitch: 28 mm
- Row count: 8

Legacy XLR footprint circular reference:

- `NC3MAV` output circular center is footprint origin + (3.81 mm, 0)
- `NC3FAV` input circular center is footprint origin + (-3.81 mm, 0)
- Output circular center x: 25.81 mm on the old board
- Input circular center x: 69.19 mm on the old board
- True circular-center spacing between output and input columns: 43.38 mm
- Courtyard/reference circle diameter: 22.8 mm
- Fab/reference circle diameter: 21.8 mm

Legacy XLR circular envelope:

- Left edge of output courtyard circle: x = 14.41 mm
- Right edge of input courtyard circle: x = 80.59 mm
- Circular XLR bank width, excluding labels and screw/latch access: 66.18 mm
- Top edge of first-row courtyard circle: y = 5.60 mm
- Bottom edge of last-row courtyard circle: y = 224.40 mm
- Circular XLR bank height: 218.80 mm

## Radxa Panel Starting Point

Use the legacy XLR geometry as the first Radxa top-panel placement basis:

- Keep two vertical XLR columns.
- Keep 8 rows.
- Keep CH1 at the top and CH8 at the bottom.
- Use `NC3MAV` size/pitch for the output column.
- Use `NC3FAV` size/pitch for the input column.
- Start from 28 mm row pitch and 43.38 mm circular-center column spacing.
- Leave 15.0 mm / 0.59 in from the finished left panel edge to the outer left
  edge of the XLR bank so the connector bank clears the frame boundary.

If the 15.0 mm clearance is measured to the left edge of the XLR circular
envelope, the first output circular center is approximately:

- 15.0 mm + 11.4 mm = 26.4 mm from the finished left panel edge

Then the input circular center is approximately:

- 26.4 mm + 43.38 mm = 69.78 mm from the finished left panel edge

The old 28 mm row pitch is mechanically compact. Because the Radxa unit needs
individual labels under each connector, check label readability before freezing
the row pitch. The iM2300 panel has enough front-to-back room to increase pitch
slightly if the labels need more space.

## Release Checks

- Verify the final Neutrik mechanical drawings and panel cutouts.
- Import official or verified STEP models for `NC3MAV` and `NC3FAV`.
- Confirm latch/release-tab orientation against the operator photo reference.
- Confirm whether XLRs are panel-mounted, PCB-mounted, or panel-supported with
  short harnesses to the carrier.
- Confirm pin 1 and shell/chassis bonding with the final audio-ground and EMC
  plan.
