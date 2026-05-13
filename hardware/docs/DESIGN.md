# Hardware Design Notes

Detailed design decisions and PCB routing guidelines for the Granit carrier board.

## SATA Power Switching

12V and 5V to the SATA connector are switched by P-channel MOSFETs
(Q2, Q3 — FDS4435BZ). GPIO17 (`SATA_PWR_EN`) drives N-channel level shifters
(Q5, Q6 — 2N7002) which pull the P-FET gates low to turn them on.

```
Supply (+12V or +5VP)
  │
  JP5/JP6 pad 1 ─── [bridged default] ─── JP5/JP6 pad 2 (common)
                                              │
  JP5/JP6 pad 3 ─── GND                  R12/R13 (100K)
                                              │
                                         ┌────┴──── Q2/Q3 gate
                                         │
                                    2N7002 drain
                                         │
  SATA_PWR_EN (GPIO17) ── R14 (10K) ── 2N7002 gate
                                         │
                                    2N7002 source
                                         │
                                        GND
```

Two 3-pad solder jumpers (JP5 `SATA_12V_PWR`, JP6 `SATA_5V_PWR`) select the boot default:
- **Pads 1-2 bridged (default):** 100K pull-up to source → FETs OFF → HDD powered on by software
- **Pads 2-3 bridged:** 100K pull-down to GND → FETs ON → HDD powered at boot

GPIO17 high → N-FET on → P-FET gate low → SATA power on.
GPIO17 low or high-Z (boot default) → N-FET off → pull-up holds P-FET off.

R14 (10K) protects GPIO17 against N-FET gate-to-drain failure.

## Power Routing & Netclasses

PCB is fabricated with JLCPCB standard 4-layer stackup (1oz / 35µm copper on all layers).
Track widths are sized per IPC-2221 for outer-layer traces with 20°C temperature rise.

| Netclass | Track Width | Via (pad/drill) | Capacity (1oz, 20°C rise) | Worst-case Load | Nets |
|---|---|---|---|---|---|
| Power 12V | 3.0mm | 1.6mm / 0.8mm | ~3.5A | ~2.5A | `+12V*`, `fused`, `unfused` |
| Power 5V | 2.5mm | 1.6mm / 0.8mm | ~3.2A | ~2.8A | `+5VP`, `VBUS`, `switch` |
| Power 3V3 | 1.0mm | 0.8mm / 0.4mm | ~1.5A | ~0.6A | `+3V3` |

### Routing Guidelines

- Netclass widths are the default for main runs. Neck down to pad width over the last 1–2mm at component pads.
- Use copper pours for 12V and 5V in the PSU area where space allows.
- Use 2–3 parallel vias where power traces change layers.
- Place GND return vias near every power via.
- Keep 12V and 5V routing on top/bottom layers — do not break the inner GND planes.
- Do not route power traces under or parallel to PCIe/SATA/Ethernet differential pairs.

### Layer Strategy

- **Top layer:** PSU components and local routing, signal components
- **Inner 1 (In1.Cu):** GND plane — keep unbroken
- **Inner 2 (In2.Cu):** GND plane — keep unbroken
- **Bottom layer:** Power distribution (5V, 12V, 3.3V to rest of board), signal routing

### Signal Integrity

- **PCIe:** 100Ω differential impedance, matched length, minimize vias and stubs
- **SATA:** 100Ω differential impedance, matched length
- **Ethernet:** 100Ω differential impedance to RJ45 with magnetics
- **USB:** 90Ω differential impedance
- Power traces crossing differential pairs must cross perpendicular (90°)

### AC Coupling Capacitors

6× 100nF 0805 in series on high-speed differential pairs, all placed near the ASM1061:

- **SATA TX** (STXP_A, STXN_A): required by SATA spec (ASM1061 datasheet CTX = 75–200nF)
- **SATA RX** (SRXP_A, SRXN_A): defensive — external interface, can't guarantee drive-side caps
- **PCIe RX** (PCIE_RX_P, PCIE_RX_N): required by CM4 datasheet ("external AC coupling capacitor required")
- **PCIe TX, CLK**: not needed — CM4 has internal AC coupling
- **Ethernet**: not needed — MagJack provides galvanic isolation
- **USB**: not needed — DC-coupled by spec

### ESD Protection

- **USB-C** (J7): USBLC6-2SC6 on D+/D− — user-facing external connector, required
- **SATA** (J9): no ESD protection — internal connector inside metal enclosure, not user-accessible, AC coupling caps provide DC fault isolation
- **Ethernet** (J3): RJ45 MagJack has integrated common-mode chokes and 2kV isolation

## Power Budget

| Rail | Source | Capacity | Worst-case Load |
|---|---|---|---|
| 12V | External PSU | 3A+ recommended | ~2.5A (HDD spin-up + buck converter) |
| 5V | AP64501SP-13 | 3.5A | ~2.8A (CM4 + HDD + USB) |
| 3.3V | NCP1117 LDO | 1A | ~0.6A (ASM1061 + RTC + misc) |

Realistic steady state: ~1.5A (CM4) + 0.5A (HDD) = 2.0A on 5V rail.
HDD spin-up and CM4 peak don't occur simultaneously — SATA power is software-controlled.

### 5V Rail Voltage (5.16V)

The feedback divider (R2=12K, R4=2.2K) sets the buck converter output to 5.16V, intentionally above 5.0V:

- **SATA power FET drop**: FDS4435BZ Rds(on) ~9mΩ → ~18mV loss at 2A
- **Trace/connector resistance**: additional ~30–50mV drop to CM4 pins
- **CM4 undervoltage threshold**: the CM4 triggers low-voltage warnings below ~4.9V

Running at 5.16V ensures the CM4 sees >5.0V after all drops, avoiding undervoltage throttling.

## Ethernet MagJack Pin Mapping

The HR911130A (Hanrun) GbE MagJack follows the standard TIA-568B MDI (Medium Dependent
Interface) pinout. The RJ45 jack pins 1–8 map to Ethernet pairs through internal isolation
transformers, with the transformer outputs on PCB-side pins P1–P10.

### TIA-568B MDI Pair Assignment

In Gigabit Ethernet (1000BASE-T), all 4 pairs are bidirectional. The pair numbering follows
TIA-568B:

| RJ45 Jack Pins | MDI Pair | Function (legacy 10/100) |
|---|---|---|
| 1, 2 | Pair 0 | TX |
| 3, 6 | Pair 1 | RX |
| 4, 5 | Pair 2 | BI (GbE only) |
| 7, 8 | Pair 3 | BI (GbE only) |

Note: Pair 1 (pins 3 and 6) is intentionally split across pins 4 and 5 on the RJ45 jack.
This is a TIA-568 design choice for backwards compatibility with 2-pair telephone wiring.

### HR911130A PCB-Side Pin Mapping

| PCB Pin | Signal | CM4 Net | Notes |
|---|---|---|---|
| P1 | Center tap (primary) | +3.3V via bias resistor | Transformer center tap bias |
| P2 | MDI Pair 0+ | ETH_P0_P | |
| P3 | MDI Pair 0− | ETH_P0_N | |
| P4 | MDI Pair 1+ | ETH_P1_P | Physically far from P7 — normal per TIA-568 |
| P5 | MDI Pair 2+ | ETH_P2_P | |
| P6 | MDI Pair 2− | ETH_P2_N | |
| P7 | MDI Pair 1− | ETH_P1_N | Physically far from P4 — normal per TIA-568 |
| P8 | MDI Pair 3+ | ETH_P3_P | |
| P9 | MDI Pair 3− | ETH_P3_N | |
| P10 | Center tap (secondary) | GND via RC network | Bob Smith termination |
| 11 | LED Green anode | +3.3V via resistor | Link/Activity |
| 12 | LED Green cathode | nLED1 | |
| 13 | LED Yellow cathode | nLED2 | |
| 14 | LED Yellow anode | +3.3V via resistor | Speed |
| S1, S2 | Shield | GND | Chassis ground |

### Routing Notes

- P4 and P7 (Pair 1) are physically separated on the PCB pads because the MagJack's
  internal transformers mirror the RJ45 jack pin arrangement where pins 3 and 6 are split.
  Route them as a matched-length differential pair despite the physical separation at the
  MagJack end.
- All 4 Ethernet pairs require 100Ω differential impedance and length matching.
- The MagJack provides galvanic isolation (2kV) — no external AC coupling or ESD protection
  needed on the Ethernet lines.

## GLOBAL_EN Wake/Shutdown Latch

Controls CM4 power state via the GLOBAL_EN pin (pin 99). Supports cold boot, software
shutdown with latch, RTC alarm wake, and button wake.

### Background

GLOBAL_EN has a CM4-internal pull-up — the module boots when GLOBAL_EN is HIGH or floating,
and powers off completely when GLOBAL_EN is held LOW. After shutdown, CM4 GPIOs go Hi-Z,
so a hardware latch is required to hold GLOBAL_EN LOW and prevent immediate reboot.

### Failed Approach (v0.3)

The v0.3 design used an OR gate (U4, 74AHCT1G32) driving GLOBAL_EN HIGH on wake events,
with Q1 (2N7002) gated by RTC ~INT. R19 (10K pull-up on Q1 gate) held Q1 ON at power-on,
pulling U4 input LOW and preventing boot. The logic was fundamentally inverted.

Workaround: R19 removed. RTC wake non-functional.

### Redesigned Circuit (proposed for v0.4)

Uses a 74LVC1G74 D flip-flop as an SR latch via asynchronous ~PRE (set) and ~CLR (reset).

```
                          ┌───────────────────┐
        RTC ~INT ─────────┤ ~PRE           Q  ├──────── GLOBAL_EN (CM4 pin 99)
                          │                   │
        BUTTON ───────────┤        74LVC1G74  │
                          │                   │
        GPIO6 ────────────┤ ~CLR              │
                          │                   │
                     GND ─┤ CLK            D  ├── GND
                          │                   │
                    +3V3 ─┤ VCC          GND  ├── GND
                          └───────────────────┘

        ~PRE pin external components:
            R1 (100K) ── ~PRE to GND        power-on: forces Q=HIGH via RC delay
            C1 (100nF) ─ ~PRE to GND        holds ~PRE LOW during 3V3 ramp (~10ms)

        ~CLR pin external components:
            R2 (100K) ── ~CLR to +3V3       prevents accidental shutdown at boot

        Existing pull-ups (kept):
            R19 (10K) ── RTC ~INT to +3V3   releases ~PRE HIGH when no alarm
            R6  (10K) ── BUTTON to +3V3     releases ~PRE HIGH when not pressed
```

CLK and D are tied to GND — no clocked operation, only async ~PRE/~CLR control Q.

### Operation

| State | ~PRE | ~CLR | Q (GLOBAL_EN) | Result |
|-------|------|------|----------------|--------|
| Cold power-on | LOW (C1 holds during ramp) | HIGH (R2) | HIGH | Boots |
| Running | HIGH (R19+R6 overpower R1) | HIGH | HIGH (latched) | Stays on |
| Shutdown | HIGH | LOW (GPIO6) | LOW | Off |
| Sleeping | HIGH | HIGH (GPIO6 Hi-Z, R2) | LOW (latched) | Stays off |
| RTC wake | LOW (~INT asserts) | HIGH | HIGH | Boots |
| Button wake | LOW (pressed) | HIGH | HIGH | Boots |

### Conflict: ~PRE=LOW and ~CLR=LOW Simultaneously

Per TI SN74LVC1G74 datasheet: both asserted → Q=HIGH (nonstable state). Wake wins over
shutdown. When one releases, output follows whichever remains asserted. This is safe — the
device cannot be held off while a wake event is active.

### Power-On Timing

R1 (100K) + C1 (100nF) gives τ = 10ms. During 3V3 ramp-up, C1 holds ~PRE below VIL,
forcing Q=HIGH. Once 3V3 stabilizes, R19 (10K) and R6 (10K) overpower R1 (100K) and
bring ~PRE HIGH. The latch then holds Q=HIGH until ~CLR is asserted.

### RTC ~INT Lock-Out

DS3231 ~INT is level-triggered — stays LOW until the alarm flag is cleared via I2C. While
~INT is LOW, ~PRE is asserted and the latch cannot be reset (shutdown is blocked). This is
acceptable because GLOBAL_EN must be HIGH during boot anyway. The boot script must clear
the alarm early:

```bash
i2cset -y 1 0x68 0x0F 0x00  # Clear DS3231 status register (alarm flags)
```

### GPIO6 Float Protection

GPIO6 defaults to Hi-Z (input) at boot. R2 (100K to +3V3) keeps ~CLR HIGH, preventing
accidental shutdown. GPIO6 has no boot-time alternate function that would drive it LOW.

### Debouncing

Not required. ~PRE is level-sensitive — button bounce repeatedly forces Q=HIGH, which is
idempotent. CM4 PMIC power-up (~100ms) is far slower than bounce (~1–10ms).

### Parts Change from v0.3

| Remove | Add |
|--------|-----|
| U4 (74AHCT1G32) | 74LVC1G74DP,125 (Nexperia, TSSOP-8, IPN: U-012) |
| Q1 (2N7002) | R1: 100K to GND on ~PRE |
| R16 (GLOBAL_EN pull-up) | R2: 100K to +3V3 on ~CLR |
| R18 (Q1 drain pull-up) | C1: 100nF on ~PRE to GND |

R19 (RTC_INT pull-up) and R6 (BUTTON pull-up) are kept.

### Software Configuration

```ini
# CM4 EEPROM (rpi-eeprom-config)
POWER_OFF_ON_HALT=1       # PMIC fully powers off on shutdown
WAKE_ON_GPIO=0            # Only wake via GLOBAL_EN toggle

# config.txt
dtoverlay=gpio-poweroff,gpiopin=6,active_low=1
```

### Open Validation

- [ ] Verify GPIO6 does not glitch LOW during boot (scope on prototype)
- [ ] Measure actual power-on RC timing with chosen component values
