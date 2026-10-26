[![hacs_badge](https://img.shields.io/badge/HACS-default-orange.svg)](https://github.com/hacs/default)[![GitHub release](https://img.shields.io/github/v/release/stanus74/home-assistant-saj-h2-modbus)](https://github.com/stanus74/home-assistant-saj-h2-modbus/releases)[![GitHub All Releases](https://img.shields.io/github/downloads/stanus74/home-assistant-saj-h2-modbus/total)](https://github.com/stanus74/home-assistant-saj-h2-modbus/releases)  
[![Buy Me a Coffee](https://buymeacoffee.com/assets/img/custom_images/white_img.png)](https://buymeacoffee.com/stanus74)


# SAJ H2 Inverter Modbus - A Home Assistant integration for SAJ H2 Inverters

> ## Fork with SAJ H1 support
>
> This is a fork of [stanus74/home-assistant-saj-h2-modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus)
> that adds support for the single-phase **SAJ H1 series** (tested on an **H1-5K-S2** with the AIO3 WiFi module).
> Everything else (sensors, switches, cards, MQTT) is unchanged, and H2/HS2/HS3 inverters behave exactly as upstream.
>
> **Why:** the H1 answers almost all H2 read blocks, but keeps its application mode (AppMode) in register
> `0x3247`. On the H1, `0x3647` always reads `0` and writing it has no effect, so with the upstream integration
> the mode, charging/discharging and passive switches did nothing on an H1.
>
> **What this fork changes (only when an H1 is detected):**
>
> | | H2 (upstream) | H1 (this fork) |
> |---|---|---|
> | Detection | — | Automatic: device type `0x54` (register `0x8F00`) or serial number starting with `H1` |
> | AppMode read/write | `0x3647` | `0x3247` (0 Self-use, 1 Time-of-use, 2 Backup, 3 Passive) |
> | Passive mode `0x3636` | 0 standby, 1 discharge, 2 charge | same values (the SAJ protocol PDF has 1/2 swapped) |
> | Passive powers `0x3637`-`0x363A` | per-mille of rated power (shown as %) | **watts** (shown as W, max 5000) |
> | Discharge depths, battery/grid power limits (`0x3644`-`0x3646`, `0x364D`-`0x3650`) | writable | writes refused (registers unused on H1) |
> | **Battery Mode** select + **Battery Mode Power** number | — | new, see below |
> | Device model shown | SAJ H2 | SAJ H1 |
>
> The domain (`saj_h2_modbus`) and all entity unique IDs are kept, so existing entities, dashboards and
> automations keep working when replacing the upstream integration with this fork.
>
> ### Battery Mode (H1 only)
>
> `select.saj_battery_mode` sets what the battery does with one entity, writing all registers in a safe order.
> `number.saj_battery_mode_power` (W, kept by Home Assistant) is the power for grid charge/discharge; changing it
> while charging/discharging applies it immediately.
>
> | Option | Writes | Effect (verified on H1-5K-S2) |
> |---|---|---|
> | `self_use` | AppMode 0, `0x3636` 0 | Normal self-consumption |
> | `standby` | `0x3636` 0, AppMode 3 | Battery neither charges nor discharges; house (and EV) run from PV/grid |
> | `grid_charge` | discharge powers 0, charge powers = P, `0x3636` 2, AppMode 3 | Battery charges from the grid at ~P W |
> | `grid_discharge` | charge powers 0, discharge powers = P, `0x3636` 1, AppMode 3 | Battery discharges at P W (surplus exported) |
> | `time_of_use` | AppMode 1, `0x3636` 0 | Follows the charge/discharge time slots configured in the integration |
>
> **Important:** on the H1 the opposite direction's passive powers must be 0. With `0x3638`/`0x363A` set, the inverter
> discharged even with `0x3636 = 2` (charge). The battery mode select takes care of this.
>
> Stopping a grid charge at a target SOC is up to your automation (switch back to `self_use` or `standby`); the
> inverter has no failsafe and stays in the last mode written.
>
> **Known issue:** one AIO3 module locked up (Modbus exception 2 on every register until power-cycled) while two
> Modbus clients were connected.
>
> **Only one Modbus TCP client at a time:** the AIO3 module mixes responses between simultaneous clients and
> rejects the second one. Do not run this integration together with another Modbus client (YAML hub, scripts, ...).
>
> `h1-tools/` contains a read-only register probe and test scripts used to map the H1 registers.
>
> **Install via HACS:** HACS → ⋮ → Custom repositories → add `https://github.com/begeles2000/home-assistant-saj-h1-modbus`
> (category *Integration*), install it and remove/disable the upstream *SAJ H2 Inverter Modbus* to avoid two copies
> of the same domain.

Integration for reading data from SAJ Inverters through Modbus TCP.

It should work for Ampere Solar Inverter (EKD-Solar) too. They use SAJ HS2 Inverter.

## Features 

- Installation through Config Flow UI
- Over 390 registers (power, energy, temperature sensors, battery...)
- Configurable polling interval - changeable at any time, with real-time sensors adjustable at 10-second intervals or **even 1-second intervals** (via MQTT)

- Smart Modbus connection management - especially for AIO3 

- **New Feature:** Configure Charging Time and Power, ability to switch the working mode between **Self-Consumption** / **Time-of-Use Mode** (to charge the battery with grid power) 

## Installation

This integration is available in the HACS default repository. 

1. Open HACS 
2. Find "SAJ H2 Inverter Modbus" and click "Install."
3. Restart Home Assistant.
4. After reboot of Home-Assistant, this integration can be configured through the integration setup UI


## Configuration

1. Navigate to the "Integrations" page in your configuration, then click "Add Integration and 
select "SAJ H2 Modbus."
2. Enter the IP Address and Interval 

3. Optional: Setting the charge values for charging the battery from the grid >[read the instructions](https://github.com/stanus74/home-assistant-saj-h2-modbus/blob/main/working-mode-doc.pdf)
4. Set charging values in Home Assistant, see below

---

## Features

### 🚀 New Fast Coordinator (10s) for Live Data

* **High-frequency polling for key metrics (e.g., PV power, battery):**

  * Introduced a 10s fast coordinator 
    Energy sensors are polled every 10 seconds: 

    "TotalLoadPower", "pvPower", "batteryPower", "totalgridPower",
    "inverterPower", "gridPower",

You can be enabled/disable in Configuration Settings every time

#### Realtime sensors (10s) vs. Ultra Fast (1s) — pick one

The two options are **not** cumulative. Enabling *Ultra Fast* switches the 10s loop
off, which changes where the live data ends up:

| | Realtime sensors (10s) | Ultra Fast (1s) |
|---|---|---|
| Home Assistant entities | every 10 s | **only on the main scan interval (60 s)** |
| MQTT | every 10 s | every 1 s |
| PV1 / PV2 power | updated | **not polled** |
| Other energy sensors | updated | updated over MQTT only |

*Ultra Fast* exists for consumers that read the live values off MQTT, and it keeps
the 1s cycle short by reading only the register block that carries the aggregate
power values. `pv1Power` and `pv2Power` live in a different block that is not part
of that cycle, so the per-string values only refresh on the main scan interval.

If you want fast updates **inside Home Assistant**, use *Realtime sensors (10s)*.
Enabling both does not give you both — Ultra Fast wins and the HA entities get
slower, not faster.


### 🚀 Charging/Discharging Control

> **⚠️ Warning: Write Registers**
>
> This integration exposes input entities that write directly to Modbus registers.  
> These commands change inverter behaviour in real time.
>
> Incorrect values can cause:
> - wrong battery charging/discharging
> - wrong export limit / grid behaviour
> - inverter protection mode activation
>
> Use write functions carefully.  
> The developer is not liable for any issues arising from user-applied register writes.

### ⚡ SAJ Inverter – Passive Mode 

Passive Mode allows you to charge or discharge your battery at a fixed power level – for example, during low electricity rates or for grid support.

Learn more: https://github.com/stanus74/home-assistant-saj-h2-modbus/discussions/105

**How it works:**

1. **Set the power level** (0–1000, where 1000 = 100%):
   - `number.saj_passive_bat_charge_power` – Battery charge power
   - `number.saj_passive_bat_discharge_power` – Battery discharge power

2. **Activate the mode** via Switch:
   - `switch.saj_passive_charge_control` (ON = Charge / OFF = Off)
   - `switch.saj_passive_discharge_control` (ON = Discharge / OFF = Off)

**Important** for Power Settings
https://github.com/stanus74/home-assistant-saj-h2-modbus/issues/141

That's it – the inverter handles the rest automatically.

### 🚀 Export Limit Control

- **SAJ Export Limit (Input)** 
  `number.saj_export_limit_input` : Value in **percent** – e.g. `500` = 50% of inverter max power (e.g. 4000 W for 8 kW inverter)

Perfect for zero export or dynamic grid feed-in limitation. 
**Important**: This applies to PV power surplus that is fed into the public grid.


### Configure Charging and Discharging Time and Power (Time-of-Use Mode)

#### 🚀 Custom Lovelace Card for Charging/Discharging Control

A custom Lovelace card is available to provide a user-friendly interface for controlling settings:

![SAJ H2 Charge Card](https://github.com/stanus74/home-assistant-saj-h2-modbus/blob/main/images/saj_h2_modbus/charge.png "SAJ H2 Charge Card")

Features:
- Easy time selection for charge start and end
- Slider for charge power percentage
- Checkbox selection for charging days 
- Button to enable/disable charging



For detailed installation instructions, see [SAJ H2 Charge Card Installation](https://github.com/stanus74/saj-h2-lovelace-card)





[![Buy Me a Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://buymeacoffee.com/stanus74)
