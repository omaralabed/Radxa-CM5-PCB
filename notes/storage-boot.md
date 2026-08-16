# Storage And Boot

## Decision

Use CM5 eMMC only for normal storage and boot.

## Implications

- Do not add a microSD slot for normal operation.
- Keep board routing simpler by avoiding SDMMC connector routing and ESD parts.
- Plan recovery and provisioning through another path.

## Recovery And Provisioning

Design in all of these:

- USB recovery/update mode exposed on a service connector or external USB-C port
- Network provisioning over LAN
- Debug UART header for boot logs and recovery support
- Dedicated recovery/reset button if required by the CM5 boot flow

## Open Decisions

- Exact USB recovery connector style and placement.
- Exact debug UART connector style and voltage.
- Whether recovery/reset buttons are external, internal, or service-only.
