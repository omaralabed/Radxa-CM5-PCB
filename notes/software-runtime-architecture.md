# Software Runtime Architecture

## Goal

Protect ProComm SIP/audio operation from Wi-Fi AP, cellular modem, router,
display, logging, and background load.

## CPU Partition

The Radxa CM5/RK3588-class module has a heterogeneous CPU. Treat the OS image as
two logical runtime domains:

- Audio/SIP domain: 8x8 TDM audio engine, SIP signaling, RTP/media processing,
  audio watchdog, and any low-latency mixer/monitoring process.
- Network/system domain: Wi-Fi AP, cellular modem, WAN/LAN routing, firewall,
  DHCP/DNS, web UI, logs, update service, and maintenance tasks.

Implementation targets:

- Pin audio/SIP processes to reserved CPU cores.
- Keep network IRQs away from the audio/SIP cores where practical.
- Give audio DMA/I2S IRQ handling higher priority.
- Use real-time scheduling for the audio process where safe.
- Use a fixed performance governor or real-time tuned profile during active
  operation.
- Keep buffers large enough to survive load spikes unless a lower-latency mode
  is explicitly required.

## GPU, VPU, And NPU Offload

Selected accelerator role: use the GPU and NPU where they reduce CPU pressure,
but do not depend on them for hard real-time audio timing.

Selected GPU uses:

- HDMI touchscreen UI rendering.
- Waveform/meters/spectrum display rendering.
- General graphics.

Selected NPU uses:

- Future local AI/noise/classification features on the NPU if needed.
- Noise detection/classification.
- Smart monitoring.

Possible VPU/video uses, if video features are added later:

- Video preview, decode, encode, or streaming assist through the video pipeline.

Possible GPU compute experiments:

- OpenCL/Vulkan compute experiments only after the core audio path is stable.

Do not use GPU offload for:

- I2S/TDM timing.
- ALSA DMA reliability.
- Primary SIP/RTP real-time scheduling.
- Router/firewall packet forwarding.
- Wi-Fi AP or cellular modem control.

The GPU is valuable because it can keep UI and video work off the CPU, which
helps protect the audio/SIP cores. The audio clocking, DMA path, ALSA driver,
and process scheduling still remain CPU/kernel responsibilities.

## Stress-Test Rule

Run the production image under worst-case load before release:

- 8-channel capture and 8-channel playback active.
- SIP call active.
- Wi-Fi AP serving clients.
- WAN/LAN routing loaded.
- Cellular modem online.
- HDMI touchscreen active.
- eMMC logging active.

Pass condition: no audible mute, no lost TDM sync, no unrecovered ALSA xruns, no
channel-map corruption, and no converter reset/mute glitches.
