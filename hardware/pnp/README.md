# Pick and Place Assembly Plan

OpenPnP job files for Granit v0.3 prototype assembly.

## Usage

```bash
cd hardware
make pnp        # generate board.xml + ensure parts exist
make feeders    # assign parts to feeder slots
make feeder-map # generate interactive HTML feeder map
```

## Feeder Allocation

Defined in [`feeders.csv`](feeders.csv) — the single source of truth for
which part goes in which feeder slot. Apply with `make feeders`.

View the interactive feeder map with `make feeder-map`.

## Hand-Place Components

| Ref | Part | Reason |
| --- | ---- | ------ |
| CM1 | Raspberry Pi CM4 | Board-to-board connector |
| J1 | USB-C receptacle | Mid-mount, alignment |
| J2 | Slide switch | Odd form factor |
| J3 | UART connector | Vertical |
| J4 | SATA 22-pin | Through-hole pins |
| SW1 | Tactile button | Side-mount |
| C26 | 100µF/25V electrolytic | Tall |

## Assembly Sequence

1. **Stencil** — apply solder paste (tape-hinge, align under microscope)
2. **Machine place** — run OpenPnP job (90 placements)
3. **Inspect** — check QFN-48 (U3) alignment
4. **Reflow** — hot plate (peak ~245°C)
5. **Inspect** — check for bridges
6. **Hand-solder** — CM1, J1–J4, SW1, C26
7. **Clean** — IPA wash
