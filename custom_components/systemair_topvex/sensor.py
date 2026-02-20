"""Sensor entities for Systemair Topvex."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TopvexCoordinator, TopvexData
from .entity import TopvexEntity


@dataclass(frozen=True)
class TopvexSensorDescription(SensorEntityDescription):
    """Describe a Topvex sensor."""
    value_fn: Callable[[TopvexData], float | str | None] = lambda d: None


SENSORS: tuple[TopvexSensorDescription, ...] = (
    TopvexSensorDescription(
        key="outdoor_temp",
        name="Utetemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda d: d.outdoor_temp,
    ),
    TopvexSensorDescription(
        key="intake_temp",
        name="Inntakstemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda d: d.intake_temp,
    ),
    TopvexSensorDescription(
        key="supply_temp",
        name="Tillufttemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda d: d.supply_temp,
    ),
    TopvexSensorDescription(
        key="exhaust_temp",
        name="Avkasttemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda d: d.exhaust_temp,
    ),
    TopvexSensorDescription(
        key="extract_temp",
        name="Avtrekkstemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda d: d.extract_temp,
    ),
    TopvexSensorDescription(
        key="after_recovery_temp",
        name="Temperatur etter veksler",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda d: d.after_recovery_temp,
    ),
    TopvexSensorDescription(
        key="saf_flow",
        name="Tilluft luftmengde",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m³/h",
        suggested_display_precision=0,
        value_fn=lambda d: d.saf_flow,
    ),
    TopvexSensorDescription(
        key="eaf_flow",
        name="Avtrekk luftmengde",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m³/h",
        suggested_display_precision=0,
        value_fn=lambda d: d.eaf_flow,
    ),
    TopvexSensorDescription(
        key="saf_output",
        name="Tilluftvifte utgang",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        value_fn=lambda d: d.saf_output,
    ),
    TopvexSensorDescription(
        key="eaf_output",
        name="Avtrekksvifte utgang",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        value_fn=lambda d: d.eaf_output,
    ),
    TopvexSensorDescription(
        key="recovery_efficiency",
        name="Gjenvinningsgrad",
        icon="mdi:recycle",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        value_fn=lambda d: d.recovery_efficiency,
    ),
    TopvexSensorDescription(
        key="frost_protection",
        name="Frostsikring",
        icon="mdi:snowflake-alert",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        value_fn=lambda d: d.frost_protection,
    ),
    TopvexSensorDescription(
        key="bypass",
        name="Bypass",
        icon="mdi:valve",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        value_fn=lambda d: d.seq_b,
    ),
    TopvexSensorDescription(
        key="exch_pressure",
        name="Vekslertrykk",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PA,
        suggested_display_precision=0,
        value_fn=lambda d: d.exch_pressure,
    ),
    TopvexSensorDescription(
        key="filter_pressure_saf",
        name="Filtertrykk tilluft",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PA,
        suggested_display_precision=0,
        value_fn=lambda d: d.filter_pressure_saf,
    ),
    TopvexSensorDescription(
        key="filter_pressure_eaf",
        name="Filtertrykk avtrekk",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PA,
        suggested_display_precision=0,
        value_fn=lambda d: d.filter_pressure_eaf,
    ),
    TopvexSensorDescription(
        key="co2",
        name="CO2",
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="ppm",
        suggested_display_precision=0,
        value_fn=lambda d: d.co2,
    ),
    TopvexSensorDescription(
        key="humidity_room",
        name="Luftfuktighet",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        value_fn=lambda d: d.humidity_room,
    ),
    TopvexSensorDescription(
        key="unit_mode",
        name="Driftsmodus",
        icon="mdi:information-outline",
        value_fn=lambda d: d.unit_mode_name,
    ),
    TopvexSensorDescription(
        key="boost_remaining",
        name="Komfyravtrekk gjenstående",
        icon="mdi:timer-outline",
        native_unit_of_measurement="s",
        value_fn=lambda d: d.boost_remaining if d.boost_active else 0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Topvex sensors."""
    coordinator: TopvexCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TopvexSensor(coordinator, desc) for desc in SENSORS
    )


class TopvexSensor(TopvexEntity, SensorEntity):
    """Topvex sensor entity."""

    entity_description: TopvexSensorDescription

    def __init__(
        self, coordinator: TopvexCoordinator, description: TopvexSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key, description.name)
        self.entity_description = description

    @property
    def native_value(self):
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
