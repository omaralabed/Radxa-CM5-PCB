# H03 Lid-Display Cable Bundle

## Purpose

`H03` connects the underside-facing CM5-CARRIER display interfaces to the
15.6-inch touchscreen in the iM2300 lid. The three cables remain separately
replaceable:

- `H03A`: HDMI video
- `H03B`: USB touch data
- `H03C`: 12 V monitor power

## Prototype Length

Use a finished length of 1000 +/- 25 mm for each first-article cable.

- Measure H03A and H03B connector mating face to connector mating face.
- Measure H03C from the rear face of the fully assembled P803 Micro-Fit
  housing to the monitor-plug strain-relief reference.
- Do not release 1000 mm as the final production length until the actual
  monitor, connector orientations, carrier placement, notch, clamps, lid, and
  removable top panel have passed the motion test below.

## H03A HDMI

- Carrier end: HDMI Type-A male into `J801`, Molex `208658-1001` receptacle.
- Monitor end: HDMI Type-A male, subject to orientation check on the received
  monitor sample.
- Use a shielded, certified High Speed HDMI cable rated for repeated flexing.
- Select low-profile or right-angle overmolds only after the installed sample
  confirms the required exit direction and bend clearance.
- Add positive cable retention near both connectors. Do not rely on HDMI
  connector friction as strain relief.

## H03B USB Touch

- Carrier end: USB Type-A male into `J802`, Wurth `692122030100` receptacle.
- Starting monitor end: USB Type-B male. Confirm whether the received monitor
  uses USB 2.0 Type-B, USB 3.x Type-B, USB-C, or another touch connector before
  production release.
- A USB 3.x A-to-B cable is acceptable even though the carrier currently uses
  only the USB 2.0 D+/D- pair for HID touch.
- Use a shielded high-flex cable and positive retention near both connectors.

## H03C 12 V Power

Carrier connector `J803` is Molex Micro-Fit 3.0 `43045-0412`, mounted on the
PCB underside and facing down.

| J803 / P803 cavity | Assignment | Conductor |
| ---: | --- | --- |
| 1 | `DISPLAY_12V` | 18 AWG red |
| 2 | `DISPLAY_12V` | 18 AWG red |
| 3 | `GND` | 18 AWG black |
| 4 | `GND` | 18 AWG black |

Use Molex housing `43025-0400` and four tin-plated 18 AWG female contacts
`43030-0038`. Join the two positive and two return conductors only in a
qualified monitor-end termination or sealed splice. The monitor-end power
plug remains sample-gated because its exact barrel/locking geometry is not in
the controlled monitor documentation.

The branch is 12 V / 2.5 A and is protected by the upstream 3 A time-lag fuse.
There is no dedicated display eFuse by project requirement.

## Routing And Retention

- Route all three cables through the centered open hinge-edge notch with an
  abrasion liner. Do not pull connector overmolds through an enclosed hole.
- Provide a gentle retained loop for normal lid travel and a separate
  releasable loop for top-panel service.
- Use cushioned clamps and broad hook-and-loop retention. Do not crush HDMI or
  USB cable geometry with narrow cable ties.
- Follow the cable manufacturer's moving bend radius; use at least 10 times
  cable outside diameter where no stricter value is available.
- Keep stored and released cable outside all fan swept volumes, fan intakes,
  PSU airflow, heatsinks, RF coax corridors, board keepouts, and sharp edges.
- Clamp within 75 mm of each carrier connector and at the lid-side transition
  so no PCB or monitor connector carries bundle weight or service force.

## First-Article Acceptance

1. Open and close the lid through its complete travel while all three cables
   are connected. Nothing may pinch, scrape, tighten, or enter a fan opening.
2. With the lid open, release the panel-service clamps. Raise the connected top
   panel at least 300 mm above its support frame and tilt it at least 45
   degrees in the intended service direction.
3. At the entire service envelope, verify visible slack at all six cable ends,
   compliant bend radii, intact edge protection, and no load on connectors.
4. Return the panel to operating position and secure all loops. Verify the case
   closes and latches without compressing a cable.
5. Operate 1080p60 HDMI video, USB HID touch, and maximum display brightness
   during motion. Reject any video blanking, USB disconnect, touch dropout, or
   power interruption.
6. Complete 500 lid open/close cycles, then repeat signal, insulation, visual,
   retention, and H03C polarity tests.
7. Record the dressed lengths. Production may shorten a cable only if the
   complete test still passes with manufacturing and installation tolerance.

## Release Blockers

- Receive the locked JUNEBOX / DTM MALL display and verify its connector,
  mounting, and installed-stack details against the documented
  396.24 x 203.20 x 20.32 mm nominal body envelope.
- Confirm USB touch connector type and orientation.
- Confirm monitor 12 V input plug size, polarity, retention, and current.
- Select exact high-flex HDMI and USB cable manufacturer part numbers.
- Release clamp locations and the protected notch geometry in the mechanical
  assembly drawing.

## Manufacturer Sources

- Molex `43045-0412` PCB header:
  https://www.molex.com/en-us/products/part-detail/0430450412
- Molex `43025-0400` cable housing:
  https://www.molex.com/en-us/products/part-detail/0430250400
- Molex `43030-0038` 18 AWG female contact:
  https://www.molex.com/en-us/products/part-detail/0430300038
- Molex `208658-1001` HDMI receptacle:
  https://www.molex.com/en-us/products/part-detail/2086581001
- Wurth `692122030100` USB receptacle:
  https://www.we-online.com/components/products/datasheet/692122030100.pdf
