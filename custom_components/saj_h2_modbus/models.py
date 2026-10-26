"""Inverter model profiles.

The integration targets the H2/HS2/HS3 register map. The single-phase H1 series
(e.g. H1-5K-S2) answers almost all of the same read blocks, but differs in a few
control registers. Everything model-specific lives here so the rest of the code
only asks the hub which profile applies.
"""

from __future__ import annotations

from typing import Any

# Device type reported in register 0x8F00 by the H1 series (SAJ protocol 2020).
DEVTYPE_H1 = 0x54

# On the H1 the application mode lives in 0x3247. 0x3647 exists but always
# reads 0 and writing it has no effect.
H1_APP_MODE_ADDRESS = 0x3247

# Passive mode on the H1 (verified on an H1-5K-S2):
# - 0x3636 uses the same values as the H2: 0 = standby, 1 = discharge,
#   2 = charge (the SAJ protocol PDF has 1 and 2 swapped).
# - 0x3637-0x363A are plain watts, not per-mille of rated power.
# - The opposite direction's powers must be 0: with 0x3638/0x363A set, the
#   inverter discharged even with 0x3636 = 2.
PASSIVE_STANDBY = 0
PASSIVE_DISCHARGE = 1
PASSIVE_CHARGE = 2
H1_PASSIVE_POWER_KEYS = (
    "passive_grid_charge_power",
    "passive_grid_discharge_power",
    "passive_bat_charge_power",
    "passive_bat_discharge_power",
)
H1_PASSIVE_POWER_MAX_W = 5000

# Application modes (0x3247 on the H1)
APP_MODE_SELF_USE = 0
APP_MODE_TIME_OF_USE = 1
APP_MODE_PASSIVE = 3

# Battery mode select (H1 only): option -> (AppMode, 0x3636, power direction)
BATTERY_MODE_SELF_USE = "self_use"
BATTERY_MODE_STANDBY = "standby"
BATTERY_MODE_GRID_CHARGE = "grid_charge"
BATTERY_MODE_GRID_DISCHARGE = "grid_discharge"
BATTERY_MODE_TIME_OF_USE = "time_of_use"
BATTERY_MODES = (
    BATTERY_MODE_SELF_USE,
    BATTERY_MODE_STANDBY,
    BATTERY_MODE_GRID_CHARGE,
    BATTERY_MODE_GRID_DISCHARGE,
    BATTERY_MODE_TIME_OF_USE,
)
DEFAULT_BATTERY_MODE_POWER_W = 1000


def battery_mode_from_data(data: dict[str, Any]) -> str | None:
    """Derive the battery mode select option from cached inverter data."""
    try:
        app_mode = int(data.get("AppMode"))
        passive = int(data.get("passive_charge_enable", 0))
    except (TypeError, ValueError):
        return None
    if app_mode == APP_MODE_SELF_USE:
        return BATTERY_MODE_SELF_USE
    if app_mode == APP_MODE_TIME_OF_USE:
        return BATTERY_MODE_TIME_OF_USE
    if app_mode == APP_MODE_PASSIVE:
        return {
            PASSIVE_STANDBY: BATTERY_MODE_STANDBY,
            PASSIVE_CHARGE: BATTERY_MODE_GRID_CHARGE,
            PASSIVE_DISCHARGE: BATTERY_MODE_GRID_DISCHARGE,
        }.get(passive)
    return None  # e.g. backup mode


# Simple settings whose H2 registers fall into an unused range on the H1
# (0x3644-0x3646 and 0x364D-0x3650 always read 0). Writes are refused so the
# entities stay in place for H2 users without touching unknown H1 registers.
H1_UNSUPPORTED_SETTINGS = frozenset(
    {
        "battery_on_grid_discharge_depth",
        "battery_off_grid_discharge_depth",
        "battery_capacity_charge_upper_limit",
        "battery_charge_power_limit",
        "battery_discharge_power_limit",
        "grid_max_charge_power",
        "grid_max_discharge_power",
    }
)


def is_h1(data: dict[str, Any]) -> bool:
    """Return True if the cached inverter data identifies an H1 series device."""
    if data.get("devtype") == DEVTYPE_H1:
        return True
    return str(data.get("sn") or "").upper().startswith("H1")
