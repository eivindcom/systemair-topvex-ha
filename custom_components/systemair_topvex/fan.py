"""Fan entities for Systemair Topvex (SAF and EAF)."""
from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TopvexCoordinator
from .entity import TopvexEntity

SAFE_PRESETS = ["Auto", "Lav", "Normal", "Høy"]
PRESET_TO_AHU = {"Auto": 2, "Lav": 3, "Normal": 4, "Høy": 5}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex fans."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TopvexFan(coordinator, "saf", "Tilluftvifte"),
        TopvexFan(coordinator, "eaf", "Avtrekksvifte"),
    ])


class TopvexFan(TopvexEntity, FanEntity):
    """Supply or extract air fan (read-only speed, mode via presets)."""

    _attr_supported_features = FanEntityFeature.PRESET_MODE
    _attr_speed_count = 100
    _attr_preset_modes = SAFE_PRESETS

    def __init__(
        self, coordinator: TopvexCoordinator, fan_id: str, name: str
    ) -> None:
        super().__init__(coordinator, f"fan_{fan_id}", name)
        self._fan_id = fan_id
        self._attr_icon = "mdi:fan"

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        output = self._get_output()
        return output is not None and output > 0

    @property
    def percentage(self) -> int | None:
        """Return current fan output % (read-only)."""
        output = self._get_output()
        if output is None:
            return None
        return int(round(output))

    @property
    def preset_mode(self) -> str | None:
        """Return current AHU mode as preset."""
        if self.coordinator.data is None:
            return None
        ahu = self.coordinator.data.ahu_mode
        ahu_to_preset = {2: "Auto", 3: "Lav", 4: "Normal", 5: "Høy"}
        return ahu_to_preset.get(ahu)

    @property
    def extra_state_attributes(self) -> dict:
        if self.coordinator.data is None:
            return {}
        d = self.coordinator.data
        if self._fan_id == "saf":
            return {
                "flow": d.saf_flow,
                "mode_raw": d.saf_mode,
                "flow_low": d.saf_flow_low,
                "flow_normal": d.saf_flow_normal,
                "flow_high": d.saf_flow_high,
            }
        return {
            "flow": d.eaf_flow,
            "mode_raw": d.eaf_mode,
            "flow_low": d.eaf_flow_low,
            "flow_normal": d.eaf_flow_normal,
            "flow_high": d.eaf_flow_high,
        }

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set AHU mode (safe presets only)."""
        ahu_mode = PRESET_TO_AHU.get(preset_mode)
        if ahu_mode is not None:
            await self.coordinator.async_set_ahu_mode(ahu_mode)

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs) -> None:
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        else:
            await self.coordinator.async_set_ahu_mode(2)  # Auto

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_ahu_mode(0)

    def _get_output(self) -> float | None:
        if self.coordinator.data is None:
            return None
        if self._fan_id == "saf":
            return self.coordinator.data.saf_output
        return self.coordinator.data.eaf_output
