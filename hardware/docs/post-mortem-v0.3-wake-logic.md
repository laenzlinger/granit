# Post-Mortem: v0.3 Wake/Shutdown Latch Failure

## Summary

The v0.3 wake/shutdown circuit did not work. The CM4 could not be woken by RTC alarm or
button press, and could not be cleanly latched off after shutdown. The logic was
fundamentally inverted.

## Intended Behaviour

1. CM4 boots on power-on
2. Software triggers shutdown → hardware holds GLOBAL_EN LOW → CM4 stays off
3. RTC alarm or button press → drives GLOBAL_EN HIGH → CM4 wakes
4. Cycle repeats

## What Was Built (v0.3)

```
RTC ~INT ──── Q1 gate (2N7002) ──── Q1 drain ──── U6 input (74AHCT1G32 OR gate)
                                                        │
                                              U6 output ──── GLOBAL_EN
```

- U6 (74AHCT1G32): OR gate driving GLOBAL_EN HIGH on wake events
- Q1 (2N7002): N-FET gated by RTC ~INT, pulling one OR gate input LOW/HIGH
- R19 (10K): pull-up on Q1 gate to +3V3

## What Went Wrong

**The logic was inverted.** R19 holds Q1 gate HIGH at power-on, turning Q1 ON, which pulls
the U6 input LOW. With both OR gate inputs LOW, GLOBAL_EN stays LOW → CM4 cannot boot.

The design assumed Q1 ON = wake, but Q1 ON actually = "pull input low" = no wake signal.

Additionally, there was no latch mechanism. After shutdown, CM4 GPIOs go Hi-Z. Without a
latch, GLOBAL_EN floats back HIGH (CM4 internal pull-up) and the CM4 immediately reboots.
The OR gate is combinational — it cannot hold state.

## Root Cause

1. **Logic inversion**: confused active-low (~INT asserts LOW on alarm) with the gate
   drive needed to produce a HIGH on GLOBAL_EN
2. **No state retention**: an OR gate is combinational, not sequential. A latch/flip-flop
   is required to hold the off state after shutdown.

## Workaround Applied

Removed R19. Without the pull-up, Q1 gate floats low, Q1 stays OFF, and GLOBAL_EN floats
HIGH via CM4 internal pull-up. The board boots and runs normally, but:

- RTC wake: non-functional
- Button wake: non-functional
- Clean shutdown latch: non-functional (CM4 reboots immediately after halt)

## Lessons Learned

1. **Simulate the logic before fabrication.** A truth table on paper would have caught the
   inversion. The circuit was designed intuitively rather than systematically.
2. **Combinational logic cannot hold state.** Shutdown requires a latch — the output must
   remain LOW after the control signal (GPIO) goes Hi-Z.
3. **Active-low signals need careful tracking.** DS3231 ~INT is active-low, GLOBAL_EN is
   active-high. Every inversion in the chain must be accounted for.

## Fix (v0.4)

Replace the OR gate + N-FET with a **74LVC1G74 D flip-flop** used as an SR latch:

- ~PRE (set) ← RTC ~INT + button (active-low → forces Q HIGH → boot)
- ~CLR (reset) ← GPIO6 (active-low → forces Q LOW → off)
- Q → GLOBAL_EN

The flip-flop holds state after the control signals release. No logic inversion issues
because ~PRE and ~CLR directly map to the active-low wake sources.

See DESIGN.md "Redesigned Circuit (proposed for v0.4)" for full schematic and analysis.

## Components Affected

| Remove (v0.3) | Add (v0.4) |
|----------------|------------|
| U6 (74AHCT1G32) | 74LVC1G74DP,125 (TSSOP-8) |
| Q1 (2N7002) | R1: 100K ~PRE to GND |
| R16 (GLOBAL_EN pull-up) | R2: 100K ~CLR to +3V3 |
| R18 (Q1 drain pull-up) | C1: 100nF ~PRE to GND |

R19 and R6 (existing pull-ups on ~INT and button) are kept.
