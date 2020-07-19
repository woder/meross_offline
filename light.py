"""Platform for light integration."""
import logging
import colorsys

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_RGB_COLOR, ATTR_COLOR_TEMP, ATTR_BRIGHTNESS, 
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, SUPPORT_COLOR, PLATFORM_SCHEMA, Light)
from homeassistant.components.climate import (
    SUPPORT_TARGET_HUMIDITY, ClimateDevice)
    
from homeassistant.util import color as colorutil

#Meross libs
from . import config
from meross_iot.supported_devices.light_bulbs import GenericBulb
from meross_iot.supported_devices.humidifiers import GenericHumidifier
from meross_iot.supported_devices.light_bulbs import to_rgb
from .utils import mangle
from .devices.light import MLight
from .devices.humidifier import MHumidifierLight

_LOGGER = logging.getLogger("Meross_Light")

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
})


def setup_platform(hass, configha, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    
    cfg = config.load(hass.config.path("meross_config.json"))
    p = dict()
    p["domain"] = cfg["server"]
    p["port"] = cfg["port"]
    p["ca_cert"] = cfg["ca_cert"]
    
    all_devices = sorted(config.list_devices(cfg))
    devices = []
    devices.extend(all_devices)
    
    lights = []
    for dev in devices:
        print(dev)
        device = cfg["devices"][dev]
        key = mangle(dev)
        p["uuid"] = device["hardware"]["uuid"]
        p["devName"] = device["friendly_name"]
        p["devType"] = device["hardware"]["type"]
        p["hdwareVersion"] = device["hardware"]["version"]
        p["fmwareVersion"] = device["firmware"]["version"]
        if "msl" in p["devType"]:
            MLight(GenericBulb("token", key, None, **p), hass, add_entities)
        elif p["devType"] == "msxh0":
            df = MHumidifierLight(GenericHumidifier("token", key, None, **p), hass, add_entities)

