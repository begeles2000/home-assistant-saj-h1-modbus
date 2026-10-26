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

# Values written to 0x3636 for the passive switches.
# H2: 1 = discharge, 2 = charge.
# H1: follows the SAJ protocol PDF (1 = charge, 2 = discharge). Verified on an
# H1-5K-S2: writing 2 discharged the battery and exported to the grid.
PASSIVE_MODE_TARGETS_H2 = {"passive_charge": 2, "passive_discharge": 1}
PASSIVE_MODE_TARGETS_H1 = {"passive_charge": 1, "passive_discharge": 2}

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
