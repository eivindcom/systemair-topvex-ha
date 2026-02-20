"""Constants for Systemair Topvex integration."""

DOMAIN = "systemair_topvex"
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 10
MAX_REGISTERS_PER_REQUEST = 47

PLATFORMS = [
    "sensor",
    "binary_sensor",
    "climate",
    "fan",
    "select",
    "number",
    "switch",
    "button",
]


# --- Input Registers (FC 0x04, read-only) ---

class IR:
    """Input Register addresses."""
    # Temperatures (scale /10, signed 16-bit)
    OUTDOOR_TEMP = 290
    INTAKE_TEMP = 291
    SUPPLY_TEMP = 292
    EXHAUST_TEMP = 293
    EXTRACT_TEMP = 294

    # Flow (scale 1 but values are 10x display, divide by 10)
    SAF_FLOW = 301
    EAF_FLOW = 302

    # Pressure (scale /10)
    EXCH_PRESSURE_SAF = 303
    EXCH_PRESSURE_EAF = 304

    # Filter pressure (must read individually)
    FILTER_PRESSURE_SAF = 323
    FILTER_PRESSURE_EAF = 324

    # After recovery temperature (must read individually)
    AFTER_RECOVERY_TEMP = 325

    # Sequence outputs (scale /10)
    SEQ_A = 341
    SEQ_B = 342  # Bypass / frostsikring

    # Fan outputs (scale /10)
    SAF_OUTPUT = 353
    EAF_OUTPUT = 354

    # Frost protection AO5 (scale /10)
    FROST_PROTECTION = 374

    # Recovery efficiency (scale /10)
    RECOVERY_EFFICIENCY = 395

    # Unit mode (scale 1)
    UNIT_MODE = 396

    # Environment (scale /10)
    CO2 = 309
    HUMIDITY_ROOM = 310
    HUMIDITY_DUCT = 311
    HUMIDITY_OUTDOOR = 312


# --- Holding Registers (FC 0x03 read / 0x06 write) ---

class HR:
    """Holding Register addresses."""
    # AHU mode control
    AHU_MODE = 565
    MANUAL_SUBMODE = 566

    # SAF (supply air fan)
    SAF_MODE = 567
    SAF_MANUAL_SETPOINT = 568  # scale /10, write *10
    SAF_MANUAL_OUTPUT = 569    # scale /10, write *10

    # EAF (extract air fan)
    EAF_MODE = 570
    EAF_MANUAL_SETPOINT = 571  # scale /10, write *10
    EAF_MANUAL_OUTPUT = 572    # scale /10, write *10

    # Temperature settings
    VENT_CONTROL = 585
    FAN_TYPE = 586
    SUPPLY_SETPOINT = 588      # scale /10, write *10
    EXTRACT_SETPOINT = 589     # scale /10, write *10
    SUPPLY_SETPOINT_MAX = 590
    SUPPLY_SETPOINT_MIN = 591

    # Fan flow setpoints (scale 1, values 10x display)
    SAF_FLOW_LOW = 618
    SAF_FLOW_NORMAL = 619
    SAF_FLOW_HIGH = 620
    EAF_FLOW_LOW = 621
    EAF_FLOW_NORMAL = 622
    EAF_FLOW_HIGH = 623

    # Fan output setpoints (scale /10)
    SAF_OUTPUT_LOW = 624
    SAF_OUTPUT_NORMAL = 625
    SAF_OUTPUT_HIGH = 626
    EAF_OUTPUT_LOW = 627
    EAF_OUTPUT_NORMAL = 628
    EAF_OUTPUT_HIGH = 629

    # Bypass (SEQ-B) control
    BYPASS_MODE = 719     # 0=Auto, 1=Manual
    BYPASS_OUTPUT = 720   # scale /10, write *10


# --- Coils (FC 0x05) ---

class Coil:
    """Coil addresses."""
    ACKNOWLEDGE_ALARMS = 0
    RESET_FILTER_ALARM = 1


# --- Lookup tables ---

UNIT_MODES = {
    0: "Stoppet", 1: "Oppstart", 2: "Lav hastighet", 3: "Normal hastighet",
    4: "Høy hastighet", 5: "Støttevarme", 6: "Støttekjøling",
    7: "CO2", 8: "Frikjøling", 9: "Nedkjøling", 10: "Brann",
    11: "Røyk", 12: "Resirkulering", 13: "Avising",
}

AHU_MODES = {
    0: "Av", 1: "Manuell", 2: "Auto", 3: "Lav", 4: "Normal", 5: "Høy",
}

AHU_MODE_TO_VALUE = {v: k for k, v in AHU_MODES.items()}

FAN_MODES = {
    0: "Av", 1: "Manuell utgang", 2: "Auto", 3: "Manuelt settpunkt",
    4: "Lav", 5: "Normal", 6: "Høy",
}

FAN_MODE_TO_VALUE = {v: k for k, v in FAN_MODES.items()}

VENT_CONTROL_TYPES = {
    0: "Tilluft", 1: "Tilluft m/utekompensering", 2: "Rom kaskade",
    3: "Avtrekk kaskade", 4: "Rom(sommer)/tilluft", 5: "Avtrekk(sommer)/tilluft",
    6: "Rom kaskade m/utekompensering", 7: "Avtrekk kaskade m/utekompensering",
    8: "Avtrekk-avhengig tilluft",
}

FAN_TYPES = {
    0: "Trykk", 1: "Flow", 2: "Manuell", 3: "Ekstern",
    4: "SAF trykk + EAF slave", 5: "SAF trykk + EAF flow slave",
    6: "EAF trykk + SAF slave", 7: "EAF trykk + SAF flow slave",
}

ALARM_STATUSES = {
    1: "OK", 2: "Blokkert", 3: "Kvittert", 5: "Returnert", 7: "Aktiv alarm",
}

ALARM_NAMES = {
    0: "Feil tilluftvifte 1", 1: "Feil tilluftvifte 2", 2: "Feil tilluftvifte 3",
    3: "Feil tilluftvifte 4", 4: "Feil tilluftvifte 5",
    5: "Feil avtrekksvifte 1", 6: "Feil avtrekksvifte 2", 7: "Feil avtrekksvifte 3",
    8: "Feil avtrekksvifte 4", 9: "Feil avtrekksvifte 5",
    10: "Alarm tilluftvifte 1", 11: "Alarm tilluftvifte 2", 12: "Alarm tilluftvifte 3",
    13: "Alarm tilluftvifte 4", 14: "Alarm tilluftvifte 5",
    15: "Alarm avtrekksvifte 1", 16: "Alarm avtrekksvifte 2", 17: "Alarm avtrekksvifte 3",
    18: "Alarm avtrekksvifte 4", 19: "Alarm avtrekksvifte 5",
    20: "Advarsel tilluftvifte 1", 21: "Advarsel tilluftvifte 2", 22: "Advarsel tilluftvifte 3",
    23: "Advarsel tilluftvifte 4", 24: "Advarsel tilluftvifte 5",
    25: "Advarsel avtrekksvifte 1", 26: "Advarsel avtrekksvifte 2", 27: "Advarsel avtrekksvifte 3",
    28: "Advarsel avtrekksvifte 4", 29: "Advarsel avtrekksvifte 5",
    50: "Feil pumpesek. I", 51: "Feil pumpesek. J",
    52: "Filteralarm tilluft", 53: "Filteralarm avtrekk",
    54: "Lav luftmengde", 55: "Frostbeskyttelse", 56: "Avising veksler",
    57: "Brannalarm", 58: "Røykalarm", 59: "Ekstern stopp",
    60: "Ekstern alarm", 61: "Servicestopp", 62: "Elektrisk overoppheting",
    63: "Frostrisiko", 64: "Lav virkningsgrad veksler", 65: "Avisingsalarm",
    66: "Rotasjonsvakt veksler",
    67: "Ekstra alarm 1", 68: "Ekstra alarm 2", 69: "Ekstra alarm 3",
    70: "Ekstra alarm 4", 71: "Ekstra alarm 5", 72: "Ekstra alarm 6",
    73: "Ekstra alarm 7", 74: "Ekstra alarm 8", 75: "Ekstra alarm 9",
    76: "Ekstra alarm 10", 77: "Internbatteri feil",
    78: "Serviceintervall", 79: "Restart blokkert",
    80: "Avvik tillufttemp", 81: "Avvik tilluftvifte", 82: "Avvik avtrekksvifte",
    83: "Avvik fuktighetsstyring", 84: "Avvik ekstra regulator",
    85: "Høy tillufttemp", 86: "Lav tillufttemp",
    87: "Maks grense tillufttemp", 88: "Min grense tillufttemp",
    89: "Høy romtemp", 90: "Lav romtemp",
    91: "Høy avtrekkstemp", 92: "Lav avtrekkstemp",
    93: "Høy utelufttemp", 94: "Lav utelufttemp",
    95: "Frostbeskyttelse 1", 96: "Frostbeskyttelse 2", 97: "Frostbeskyttelse 3",
    112: "Manuell drift aggregat", 113: "Manuell drift tilluft",
    114: "Manuell drift tilluftvifte", 115: "Manuell drift avtrekksvifte",
    116: "Manuell drift varmer", 117: "Manuell drift veksler",
    118: "Manuell drift kjøler", 119: "Manuell drift spjeld",
    120: "Manuell drift pumpe varmer", 121: "Manuell drift pumpe veksler",
    122: "Manuell drift pumpe kjøler", 123: "Manuell drift resirkulering",
    124: "Manuell drift uteluftspjeld", 125: "Manuell drift avkastspjeld",
    126: "Manuell drift brannspjeld",
    127: "Manuell styring sekvens-A", 128: "Manuell styring sekvens-B",
    129: "Manuell styring sekvens-C", 130: "Manuell styring sekvens-D",
    131: "Manuell styring sekvens-E", 132: "Manuell styring sekvens-F",
    133: "Manuell styring sekvens-G", 134: "Manuell styring sekvens-H",
    135: "Manuell styring sekvens-I", 136: "Manuell styring sekvens-J",
    137: "Utgang i manuell drift", 138: "Inngang i manuell drift",
    139: "Manuell drift ekstra regulator",
}

# Kitchen boost defaults
BOOST_SAF_FLOW = 1400  # m³/h
BOOST_EAF_FLOW = 400   # m³/h
BOOST_DEFAULT_MINUTES = 10
