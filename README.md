# Systemair Topvex - Home Assistant Integration

Custom Home Assistant integration for **Systemair Topvex TC/C03 EL CAV** ventilation units via Modbus TCP.

Provides full monitoring and control of the ventilation unit including temperatures, fan speeds, operating modes, kitchen boost, bypass/frost protection, and alarm management.

## Installation (HACS)

1. Add this repository as a custom repository in HACS
2. Search for "Systemair Topvex" and install
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration → Systemair Topvex**
5. Enter the IP address of your Topvex unit

## Manual Installation

Copy `custom_components/systemair_topvex/` to your Home Assistant `config/custom_components/` directory.

For the Lovelace card, copy `www/systemair-topvex-card.js` to `config/www/` and add it as a resource:

```yaml
resources:
  - url: /local/systemair-topvex-card.js
    type: module
```

## Entities

### Sensors (~20)
- 6 temperature sensors (outdoor, intake, supply, exhaust, extract, after recovery)
- 2 airflow sensors (SAF/EAF in m³/h)
- 2 fan output sensors (SAF/EAF %)
- Recovery efficiency, frost protection, bypass (%)
- Exchanger and filter pressures (Pa)
- CO2 (ppm), humidity (%)
- Operating mode, kitchen boost remaining

### Climate
- Main ventilation control with HVAC modes (Off/Fan Only)
- Presets: Auto, Low, Normal, High
- Supply temperature setpoint

### Fans (2)
- Supply air fan (SAF) with speed control and presets
- Extract air fan (EAF) with speed control and presets

### Select (3)
- AHU mode selector
- SAF fan mode selector
- EAF fan mode selector

### Number (4)
- Supply temperature setpoint (10-30°C)
- SAF manual output (25-100%)
- EAF manual output (25-100%)
- Bypass manual output (0-100%)

### Switch (1)
- Bypass manual mode (auto/manual)

### Buttons (6)
- Kitchen boost 10/20/30 min
- Cancel kitchen boost
- Acknowledge alarms
- Reset filter alarm

### Binary Sensors
- All 140 alarm registers as binary sensors (common ones enabled by default)

## Services

### `systemair_topvex.kitchen_boost`
Start kitchen boost mode (SAF=1400 m³/h, EAF=400 m³/h).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| minutes | int | 10 | Duration (1-60 minutes) |

### `systemair_topvex.cancel_kitchen_boost`
Cancel active kitchen boost and restore previous settings.

## Lovelace Card

Add the custom card to your dashboard:

```yaml
type: custom:systemair-topvex-card
entity_prefix: sensor.topvex_tc_c03_el_cav
```

## Device

- **Model**: Systemair Topvex TC/C03 EL CAV
- **Controller**: Access (EXOline/Regin), software v4.6-1-00
- **Protocol**: Modbus TCP, port 502
- **Heat exchanger**: Counterflow (motstrøms)

## Requirements

- Home Assistant 2024.1.0+
- `pymodbus` 3.6.0+ (installed automatically)
- Network access to the Topvex unit on Modbus TCP port 502
