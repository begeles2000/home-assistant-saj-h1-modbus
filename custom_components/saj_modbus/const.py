from typing import Optional
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.const import (
    UnitOfReactivePower,  # Ersetze den Import für die veraltete Konstante
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from typing import Dict, NamedTuple, Any


DOMAIN = "saj_modbus"
DEFAULT_NAME = "SAJ"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_PORT = 502
CONF_SAJ_HUB = "saj_hub"
ATTR_MANUFACTURER = "SAJ Electric"


@dataclass
class SensorGroup:
    unit_of_measurement: Optional[str] = None
    icon: str = ""  # Optional
    device_class: Optional[str] = None  
    state_class: Optional[str] = None  
    force_update: bool = False  # Neues Attribut für die Gruppe
    
@dataclass
class SajModbusSensorEntityDescription(SensorEntityDescription):
    """A class that describes SAJ H1 sensor entities."""


power_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:solar-power",
    force_update=True  # force_update für die gesamte Gruppe aktivieren

)

voltage_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfElectricPotential.VOLT,
    device_class=SensorDeviceClass.VOLTAGE,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:sine-wave",  
)

current_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    device_class=SensorDeviceClass.CURRENT,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:current-dc",  
)

temperature_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:thermometer",  
)

energy_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon="mdi:solar-power",  
)

information_sensors_group = SensorGroup(
    icon="mdi:information-outline"  
)

gfci_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
    device_class=SensorDeviceClass.CURRENT,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:current-dc"
)

iso_resistance_sensors_group = SensorGroup(
    unit_of_measurement="kΩ",  
    icon="mdi:omega"
)

battery_sensors_group = SensorGroup(
    unit_of_measurement='%',  
    device_class=SensorDeviceClass.BATTERY,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:battery"  
)

frequency_sensors_group = SensorGroup(
    unit_of_measurement=UnitOfFrequency.HERTZ,  # Einheit in Hertz
    device_class=SensorDeviceClass.FREQUENCY,  # Klassifizierung als Frequenz
    state_class=SensorStateClass.MEASUREMENT,  # Zustand wird gemessen
    icon="mdi:sine-wave"  # Passendes Icon für Frequenz
)


# Neue Gruppe für Zeit- bzw. Scheduling-Daten
schedule_sensors_group = SensorGroup(
    unit_of_measurement=None,
    icon="mdi:clock-outline",
    device_class=None,
    state_class=None,
)

def create_sensor_descriptions(group: SensorGroup, sensors: list) -> dict:
    descriptions = {}
    for sensor in sensors:
        
        icon = sensor.get("icon", group.icon)
        if icon and not icon.startswith("mdi:"):
            icon = f"mdi:{icon}"
        
        
        enable = sensor.get("enable", True)
        native_unit = sensor.get("unit_of_measurement", group.unit_of_measurement)
        
        descriptions[sensor["key"]] = SajModbusSensorEntityDescription(
            name=sensor["name"],
            key=sensor["key"],
            native_unit_of_measurement=native_unit,
            icon=icon,
            device_class=group.device_class,
            state_class=group.state_class,
            entity_registry_enabled_default=enable,
            force_update=group.force_update
        )
    return descriptions



power_sensors = [
    {"name": "Total Load Power", "key": "TotalLoadPower", "icon": "transmission-tower"},
    {"name": "Grid Load Power", "key": "gridPower", "icon": "power-socket"},
    {"name": "Total Grid Power", "key": "totalgridPower", "icon": "power-socket"},
    {"name": "PV Power", "key": "pvPower", "icon": "solar-power"},
    {"name": "Battery Power", "key": "batteryPower", "icon": "battery-charging-100"},
    {"name": "Inverter Power", "key": "inverterPower", "icon": "power-socket"},
    {"name": "PV1 Power", "key": "pv1Power", "icon": "flash"},
    {"name": "PV2 Power", "key": "pv2Power", "icon": "flash"},
    {"name": "PV3 Power", "key": "pv3Power", "icon": "flash", "enable": False},
    {"name": "PV4 Power", "key": "pv4Power", "icon": "flash", "enable": False},
    
    {"name": "CT Grid Power Watt", "key": "CT_GridPowerWatt", "icon": "flash", "enable": False},
    {"name": "CT Grid Power VA", "key": "CT_GridPowerVA", "icon": "flash-outline", "enable": False},
    {"name": "CT PV Power Watt", "key": "CT_PVPowerWatt", "icon": "flash", "enable": False},
    {"name": "CT PV Power VA", "key": "CT_PVPowerVA", "icon": "flash-outline", "enable": False},
    {"name": "Total Inverter Power VA", "key": "TotalInvPowerVA", "icon": "flash", "enable": False},
    {"name": "Backup Total Load Power Watt", "key": "BackupTotalLoadPowerWatt", "icon": "home-lightning-bolt", "enable": False},
    {"name": "Backup Total Load Power VA", "key": "BackupTotalLoadPowerVA", "icon": "home-lightning-bolt-outline", "enable": False},
    {"name": "R-Phase Grid Power Watt", "key": "RGridPowerWatt", "icon": "flash", "enable": False},
    {"name": "R-Phase Grid Power VA", "key": "RGridPowerVA", "icon": "flash-outline", "enable": False},
    {"name": "S-Phase Grid Power Watt", "key": "SGridPowerWatt", "icon": "flash", "enable": False},
    {"name": "S-Phase Grid Power VA", "key": "SGridPowerVA", "icon": "flash-outline", "enable": False},
    {"name": "T-Phase Grid Power Watt", "key": "TGridPowerWatt", "icon": "flash", "enable": False},
    {"name": "T-Phase Grid Power VA", "key": "TGridPowerVA", "icon": "flash-outline", "enable": False},
    
   
]



voltage_sensors = [
    {"name": "PV1 Voltage", "key": "pv1Voltage", "icon": "sine-wave"},
    {"name": "PV2 Voltage", "key": "pv2Voltage", "icon": "sine-wave"},
    {"name": "PV3 Voltage", "key": "pv3Voltage", "icon": "sine-wave", "enable": False},
    {"name": "PV4 Voltage", "key": "pv4Voltage", "icon": "sine-wave", "enable": False},
    
    {"name": "R-Phase Grid Voltage", "key": "RGridVolt", "icon": "sine-wave", "enable": False},
    {"name": "S-Phase Grid Voltage", "key": "SGridVolt", "icon": "sine-wave", "enable": False},
    {"name": "T-Phase Grid Voltage", "key": "TGridVolt", "icon": "sine-wave", "enable": False},
    
    # Battery voltage sensor for H1
    {"name": "Battery Voltage", "key": "BatVolt", "icon": "battery", "enable": True},

    # Removing H2-specific battery sensors
    {"name": "Battery Voltage High Protection", "key": "BatProtHigh", "icon": "alert", "enable": False},
    {"name": "Battery Voltage Low Warning", "key": "BatProtLow", "icon": "alert", "enable": False},
    {"name": "Battery Charge Voltage", "key": "Bat_Chargevoltage", "icon": "battery-charging", "enable": False},
    {"name": "Battery Discharge Cut-off Voltage", "key": "Bat_DisCutOffVolt", "icon": "battery", "enable": False},
]



frequency_sensors = [
    
    {"name": "R-Phase Grid Frequency", "key": "RGridFreq", "icon": "sine-wave", "enable": False},
    {"name": "S-Phase Grid Frequency", "key": "SGridFreq", "icon": "sine-wave", "enable": False},
    {"name": "T-Phase Grid Frequency", "key": "TGridFreq", "icon": "sine-wave", "enable": False},
    
]
    
current_sensors = [
    {"name": "PV1 Total Current", "key": "pv1TotalCurrent", "icon": "current-dc"},
    {"name": "PV2 Total Current", "key": "pv2TotalCurrent", "icon": "current-dc"},
    {"name": "PV3 Total Current", "key": "pv3TotalCurrent", "icon": "current-dc", "enable": False},
    {"name": "PV4 Total Current", "key": "pv4TotalCurrent", "icon": "current-dc", "enable": False},
   
    {"name": "R-Phase Grid Current", "key": "RGridCurr", "icon": "current-dc", "enable": False},
    {"name": "S-Phase Grid Current", "key": "SGridCurr", "icon": "current-dc", "enable": False},
    {"name": "T-Phase Grid Current", "key": "TGridCurr", "icon": "current-dc", "enable": False},
    {"name": "R-Phase Grid DC Component", "key": "RGridDCI", "icon": "current-dc", "enable": False},
    {"name": "S-Phase Grid DC Component", "key": "SGridDCI", "icon": "current-dc", "enable": False},
    {"name": "T-Phase Grid DC Component", "key": "TGridDCI", "icon": "current-dc", "enable": False},
    
    # Battery current sensors for H1
    {"name": "Battery Current", "key": "BatCurr", "icon": "current-dc", "enable": True},
    {"name": "Battery Control 1 Current", "key": "BatCurr1", "icon": "current-dc", "enable": True},
    {"name": "Battery Control 2 Current", "key": "BatCurr2", "icon": "current-dc", "enable": True},

    # Removing H2-specific battery sensors
    {"name": "Battery Discharge Current Limit", "key": "BatDisCurrLimit", "icon": "battery", "enable": False},
    {"name": "Battery Charge Current Limit", "key": "BatChaCurrLimit", "icon": "battery-charging", "enable": False},
]

battery_sensors = [
    {"name": "Battery Energy Percent", "key": "batEnergyPercent", "icon": "battery-charging-100", "enable": True},
    # Removing H2-specific battery sensors
    {"name": "Battery 1 SOC", "key": "Bat1SOC", "icon": "battery", "enable": False},
    {"name": "Battery 1 SOH", "key": "Bat1SOH", "icon": "battery", "enable": False},
    {"name": "Battery 2 SOC", "key": "Bat2SOC", "icon": "battery", "enable": False},
    {"name": "Battery 2 SOH", "key": "Bat2SOH", "icon": "battery", "enable": False},
    {"name": "Battery 3 SOC", "key": "Bat3SOC", "icon": "battery", "enable": False},
    {"name": "Battery 3 SOH", "key": "Bat3SOH", "icon": "battery", "enable": False},
    {"name": "Battery 4 SOC", "key": "Bat4SOC", "icon": "battery", "enable": False},
    {"name": "Battery 4 SOH", "key": "Bat4SOH", "icon": "battery", "enable": False},
]



gfci_sensors = [
    {"name": "GFCI", "key": "gfci", "icon": "current-dc", "enable": False}

]

temperature_sensors = [
    {"name": "Inverter Temperature", "key": "SinkTemp", "icon": "thermometer"},
    {"name": "Environment Temperature", "key": "AmbTemp", "icon": "thermometer-lines"},
    {"name": "Battery Temperature", "key": "BatTemp", "icon": "battery-thermometer"},
    
    {"name": "Battery 1 Temperature", "key": "Bat1Temperature", "icon": "thermometer", "enable": True},
    {"name": "Battery 2 Temperature", "key": "Bat2Temperature", "icon": "thermometer", "enable": True},
    {"name": "Battery 3 Temperature", "key": "Bat3Temperature", "icon": "thermometer", "enable": True},
    {"name": "Battery 4 Temperature", "key": "Bat4Temperature", "icon": "thermometer", "enable": True},
] 




iso_resistance_sensors = [
    {"name": "PV1+ Isolation Resistance", "key": "iso1", "icon": "omega"},
    {"name": "PV2+ Isolation Resistance", "key": "iso2", "icon": "omega"},
    {"name": "PV3+ Isolation Resistance", "key": "iso3", "icon": "omega", "enable": False},  
    {"name": "PV4+ Isolation Resistance", "key": "iso4", "icon": "omega", "enable": False},  
 
]

information_sensors = [
    {"name": "Device Type", "key": "devtype", "icon": "information-outline", "enable": False},
    {"name": "Sub Type", "key": "subtype", "icon": "information-outline", "enable": False},
    {"name": "Comms Protocol Version", "key": "commver", "icon": "information-outline", "enable": False},
    {"name": "Serial Number", "key": "sn", "icon": "information-outline", "enable": False},
    {"name": "Product Code", "key": "pc", "icon": "information-outline", "enable": False},
    {"name": "Display Software Version", "key": "dv", "icon": "information-outline", "enable": False},
    {"name": "Master Ctrl Software Version", "key": "mcv", "icon": "information-outline", "enable": False},
    {"name": "Slave Ctrl Software Version", "key": "scv", "icon": "information-outline", "enable": False},
    {"name": "Display Board Hardware Version", "key": "disphwversion", "icon": "information-outline", "enable": False},
    {"name": "Control Board Hardware Version", "key": "ctrlhwversion", "icon": "information-outline", "enable": False},
    {"name": "Power Board Hardware Version", "key": "powerhwversion", "icon": "information-outline", "enable": False},
    {"name": "Inverter Status", "key": "mpvstatus", "icon": "information-outline"},
    {"name": "Inverter Working Mode", "key": "mpvmode", "icon": "information-outline"},
    {"name": "Inverter Error Message", "key": "faultmsg", "icon": "message-alert-outline", "enable": True},
    {"name": "Direction PV", "key": "directionPV", "icon": "arrow-all"},
    {"name": "Direction Battery", "key": "directionBattery", "icon": "arrow-all"},
    {"name": "Direction Grid", "key": "directionGrid", "icon": "arrow-all"},
    {"name": "Direction Ouput", "key": "directionOutput", "icon": "arrow-all"},
    {"name": "R-Phase Grid Power Factor", "key": "RGridPowerPF", "icon": "power-plug", "enable": False},
    {"name": "S-Phase Grid Power Factor", "key": "SGridPowerPF", "icon": "power-plug", "enable": False},
    {"name": "T-Phase Grid Power Factor", "key": "TGridPowerPF", "icon": "power-plug", "enable": False},

    # Removing H2-specific battery information sensors
    {"name": "Battery Number", "key": "BatNum", "icon": "numeric", "enable": False},
    {"name": "Battery Capacity", "key": "BatCapcity", "icon": "battery", "enable": False},
    {"name": "Battery User Capacity", "key": "BatUserCap", "icon": "battery", "enable": False},
    {"name": "Battery Online", "key": "BatOnline", "icon": "cloud", "enable": False},
    {"name": "Battery Fault", "key": "Bat1FaultMSG", "icon": "alert", "enable": False},
    {"name": "Battery Warning", "key": "Bat1WarnMSG", "icon": "alert", "enable": False}
]
    


energy_sensors = [
    {"name": "Today PV Energy", "key": "todayenergy", "enable": True, "icon": "solar-power"},
    {"name": "Month PV Energy", "key": "monthenergy", "enable": True, "icon": "solar-power"},
    {"name": "Year PV Energy", "key": "yearenergy", "enable": True, "icon": "solar-power"},
    {"name": "Total PV Energy", "key": "totalenergy", "enable": True, "icon": "solar-power"},
    {"name": "Battery Today Charge", "key": "bat_today_charge", "enable": True, "icon": "battery-charging"},
    {"name": "Battery Month Charge", "key": "bat_month_charge", "enable": True, "icon": "battery-charging"},
    {"name": "Battery Year Charge", "key": "bat_year_charge", "enable": True, "icon": "battery-charging"},
    {"name": "Battery Total Charge", "key": "bat_total_charge", "enable": True, "icon": "battery-charging-100"},
    {"name": "Battery Today Discharge", "key": "bat_today_discharge", "enable": True, "icon": "battery-minus"},
    {"name": "Battery Month Discharge", "key": "bat_month_discharge", "enable": True, "icon": "battery-minus"},
    {"name": "Battery Year Discharge", "key": "bat_year_discharge", "enable": True, "icon": "battery-minus"},
    {"name": "Battery Total Discharge", "key": "bat_total_discharge", "enable": True, "icon": "battery-minus"},
    {"name": "Feed-in Today Energy", "key": "feedin_today_energy", "enable": True, "icon": "transmission-tower"},
    {"name": "Feed-in Month Energy", "key": "feedin_month_energy", "enable": True, "icon": "transmission-tower"},
    {"name": "Feed-in Year Energy", "key": "feedin_year_energy", "enable": True, "icon": "transmission-tower"},
    {"name": "Feed-in Total Energy", "key": "feedin_total_energy", "enable": True, "icon": "transmission-tower"},
    {"name": "Sell Today Energy", "key": "sell_today_energy", "enable": True, "icon": "solar-power"},
    {"name": "Sell Month Energy", "key": "sell_month_energy", "enable": True, "icon": "solar-power"},
    {"name": "Sell Year Energy", "key": "sell_year_energy", "enable": True, "icon": "solar-power"},
    {"name": "Sell Total Energy", "key": "sell_total_energy", "enable": True, "icon": "solar-power"},
]
    

# Neue Sensoren für "First Charge" definieren:
first_charge_sensors = [
    {
        "name": "First Charge Start Time",
        "key": "first_charge_start_time",
        "icon": "clock-outline",
    },
    {
        "name": "First Charge End Time",
        "key": "first_charge_end_time",
        "icon": "clock-outline",
    },
    {
        "name": "First Charge Day Mask",
        "key": "first_charge_day_mask",
        "icon": "calendar",
    },
    {
        "name": "First Charge Power Percent",
        "key": "first_charge_power_percent",
        "icon": "flash",
        "unit_of_measurement": "%"  # Hier Überschreibung der Einheit
    },
}



SENSOR_TYPES = {
    **create_sensor_descriptions(power_sensors_group, power_sensors),
    **create_sensor_descriptions(voltage_sensors_group, voltage_sensors),
    **create_sensor_descriptions(current_sensors_group, current_sensors),
    **create_sensor_descriptions(temperature_sensors_group, temperature_sensors),
    **create_sensor_descriptions(energy_sensors_group, energy_sensors),
    **create_sensor_descriptions(information_sensors_group, information_sensors),
    **create_sensor_descriptions(iso_resistance_sensors_group, iso_resistance_sensors),
    **create_sensor_descriptions(battery_sensors_group, battery_sensors), 
    **create_sensor_descriptions(gfci_sensors_group,gfci_sensors),
    **create_sensor_descriptions(frequency_sensors_group,frequency_sensors),
    **create_sensor_descriptions(schedule_sensors_group, first_charge_sensors),
   
}


DEVICE_STATUSSES = {
    0: "Initialization",
    1: "Waiting",
    2: "Running",
    3: "Offnet mode, used for energy storage",
    4: "Grid on-load mode, used for energy storage",
    5: "Fault",
    6: "Update",
    7: "Test",
    8: "Self-checking",
    9: "Reset",
}

FAULT_MESSAGES = {
    0: {
		0x00000001: "Lost Com. H ↔ M Err",
		0x00000002: "Meter lost Meter",
		0x00000004: "HIMI Eeprom error",
		0x00000008: "HMI RTC Err",
		0x00000010: "BMS Device Error",
		0x00000020: "BMS lost communication warning",
		0x00000040: "Reserved (bit 71)",
		0x00000080: "Reserved (bit 72)",
		0x00000100: "Reserved (bit 73)",
		0x00000200: "Reserved (bit 74)",
		0x00000400: "Reserved (bit 75)",
		0x00000800: "R Phase voltage high fault",
		0x00001000: "R Phase voltage low fault",
		0x00002000: "S Phase voltage high fault",
		0x00004000: "S Phase voltage low fault",
		0x00008000: "T Phase voltage high fault",
		0x00010000: "T Phase voltage low fault",
		0x00020000: "Frequency High Fault",
		0x00040000: "Frequency Low Fault ",
		0x00080000: "Reserved (bit 84)",
		0x00100000: "Reserved (bit 85)",
		0x00200000: "Reserved (bit 86)",
		0x00400000: "Reserved (bit 87)",
		0x00800000: "No Grid Fault",
		0x01000000: "PV Input Mode Fault",
		0x02000000: "Hardware HW PV Curr High Fault",
		0x04000000: "PV Voltage",
		0x08000000: "Hardware HW Bus Volt High Fault",
		0x10000000: "Reserved (bit 93)",
		0x20000000: "Reserved (bit 94)",
		0x40000000: "Reserved (bit 95)",
		0x80000000: "Reserved (bit 96)",
},



    1: {
		0x00000001: "Master Bus Voltage High",
		0x00000002: "Master Bus Voltage Low",
		0x00000004: "Master Grid Phase Error",
		0x00000008: "Master PV Voltage High Error",
		0x00000010: "Master Islanding Error",
		0x00000020: "Reserved (bit 6)",
		0x00000040: "Master PV Input Error",
		0x00000080: "Communication between DSP and PC lost",
		0x00000100: "Master HW Bus Voltage High",
		0x00000200: "Master HW PV Current High",
		0x00000400: "Reserved (bit 11)",
		0x00000800: "Master HW Inv Current High",
		0x00001000: "Reserved (bit 13)",
		0x00002000: "Reserved (bit 14)",
		0x00004000: "Master Grid NE Voltage Error",
		0x00008000: "Master DRM0 Error",
		0x00010000: "Master Fan 1 Error",
		0x00020000: "Master Fan 2 Error",
		0x00040000: "Master Fan 3 Error",
		0x00080000: "Master Fan 4 Error",
		0x00100000: "Master Arc Error",
		0x00200000: "Master SW PV Current High",
		0x00400000: "Master Battery Voltage High",
		0x00800000: "Master Battery Current High",
		0x01000000: "Master Battery Charge Voltage High",
		0x02000000: "Master Battery Overload",
		0x04000000: "Master Battery Soft Connect Timeout",
		0x08000000: "Master Output Overload",
		0x10000000: "Master Battery Open Circuit Error",
		0x20000000: "Master Battery Discharge Voltage Low",
		0x40000000: "Authority expires",
		0x80000000: "Lost Communication D <-> C",
    },

    
    
        
    2: {
		0x80000000: "Bus Voltage Balance Error",
		0x40000000: "ISO Error",
		0x20000000: "Phase 3 DCI Error",
		0x10000000: "Phase 2 DCI Error",
		0x08000000: "Phase 1 DCI Error",
		0x04000000: "GFCI Error",
		0x02000000: "Reserved (bit 58)",
		0x01000000: "Reserved (bit 57)",
		0x00800000: "No Grid Error",
		0x00400000: "Phase 3 DCV Current Error",
		0x00200000: "Phase 2 DCV Current Error",
		0x00100000: "Phase 1 DCV Current Error",
		0x00080000: "Reserved (bit 52)",
		0x00040000: "Grid Frequency Low",
		0x00020000: "Grid Frequency High",
		0x00010000: "Reserved (bit 49)",
		0x00008000: "OffGrid Voltage Low",
		0x00004000: "Voltage of Master host power network is 10 Min High under voltage",
		0x00002000: "Phase 3 Voltage Low",
		0x00001000: "Phase 3 Voltage High",
		0x00000800: "Phase 2 Voltage Low",
		0x00000400: "Phase 2 Voltage High",
		0x00000200: "Phase 1 Voltage Low",
		0x00000100: "Phase 1 Voltage High",
		0x00000080: "Current Sensor Error",
		0x00000040: "DCI Device Error",
		0x00000020: "GFCI Device Error",
		0x00000010: "Communication Error M <-> S",
		0x00000008: "Temperature Low Error",
		0x00000004: "Temperature High Error",
		0x00000002: "EEPROM Error",
		0x00000001: "Relay Error",
    },


}