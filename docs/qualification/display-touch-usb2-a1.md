# Display Touch USB 2 Qualification A1

## Purpose

The locked JUNEBOX monitor is powered from 12 V and receives HDMI video. Its
touch link must enumerate as USB 2 HID through a standard USB 3 A-to-B cable,
because the carrier intentionally routes only VBUS, D-, D+, and ground at
`J802`; SuperSpeed contacts are not allocated.

## Controlled setup

- Display: JUNEBOX / DTM MALL Amazon ASIN `B0GK5X95D9`.
- Carrier host connector: Wurth `692122030100`, USB 3 Type-A receptacle.
- Monitor cable: released 1000 +/-25 mm USB 3 A-to-B harness candidate.
- Touch power: `IO_5V0` through `F802`, 1.10 A hold polyfuse.
- Monitor power: separate `DISPLAY_12V`, 12 V / 2.5 A fused branch.

## Required tests

1. Photograph and record the exact monitor touch receptacle and power connector.
2. Confirm continuity for USB 2 pins in the selected A-to-B cable.
3. Enumerate the touch controller with the USB SuperSpeed pairs intentionally
   absent. Record VID, PID, USB speed, HID descriptors, and kernel messages.
4. Verify ten-point touch, edge accuracy, press/drag, suspend/resume, warm reboot,
   cold boot, and 100 USB reconnect cycles.
5. Measure `IO_5V0` startup droop, steady current, reconnect peak, and ripple at
   the monitor end of the 1000 mm cable.
6. Run HDMI at 1920 x 1080 / 60 Hz while touch, Wi-Fi, cellular, and audio are
   active. No touch loss, video corruption, or audio interference is allowed.
7. Exercise full lid travel and the 300 mm / 45 degree panel-service position;
   cables must not tension connectors or violate their moving bend radius.

## Acceptance

Release the cable and monitor interface only after USB 2 HID operation passes
without SuperSpeed lanes, the monitor-end voltage remains inside the monitor
requirement, and the dressed harness passes movement and strain-relief tests.
If USB 2-only enumeration fails, stop release and revise the touch architecture;
do not quietly route generic SuperSpeed pairs without a new CM5 interface audit.
