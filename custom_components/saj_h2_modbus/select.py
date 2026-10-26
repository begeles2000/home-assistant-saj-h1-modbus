"""SAJ Modbus select entities (H1 battery mode)."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import models
from .entity import SajBaseEntity
from .hub import SAJModbusHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SAJ select entities."""
    hub: SAJModbusHub = entry.runtime_data
    # The battery mode relies on H1 register semantics (AppMode 0x3247, passive
    # powers in watts), so it is only offered on H1 inverters.
    if not hub.is_h1:
        return
    async_add_entities([SajBatteryModeSelect(hub, hub.device_info)])


class SajBatteryModeSelect(CoordinatorEntity, SelectEntity, SajBaseEntity):
    """Single control for what the battery does: self-use, hold, grid charge..."""

    _attr_has_entity_name = True
    _attr_translation_key = "battery_mode"
    _attr_icon = "mdi:home-battery"
    _attr_options = list(models.BATTERY_MODES)

    def __init__(self, hub: SAJModbusHub, device_info: dict) -> None:
        super().__init__(hub)
        SajBaseEntity.__init__(self, hub, device_info)
        self._attr_unique_id = f"{hub.name}_battery_mode"

    @property
    def current_option(self) -> str | None:
        return models.battery_mode_from_data(self._hub.inverter_data)

    @property
    def extra_state_attributes(self) -> dict:
        data = self._hub.inverter_data
        return {
            "app_mode": data.get("AppMode"),
            "passive_charge_enable": data.get("passive_charge_enable"),
            "power_w": self._hub.battery_mode_power,
        }

    async def async_select_option(self, option: str) -> None:
        if option not in models.BATTERY_MODES:
            _LOGGER.error("Invalid battery mode: %s", option)
            return
        await self._hub.set_battery_mode(option)
