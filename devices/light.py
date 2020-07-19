"""Platform for light integration."""
import logging
import colorsys

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_RGB_COLOR, ATTR_COLOR_TEMP, ATTR_BRIGHTNESS, 
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, SUPPORT_COLOR, PLATFORM_SCHEMA, Light)
    
from homeassistant.util import color as colorutil

#Meross libs
from meross_iot.supported_devices.light_bulbs import GenericBulb
from meross_iot.supported_devices.light_bulbs import to_rgb

_LOGGER = logging.getLogger("Meross_Light")

def rgb_to_color(color):
    blue = color & 255
    green = (color >> 8) & 255
    red = (color >> 16) & 255
    return (red, green, blue)

class MLight():
    """Representation of a Meross Light"""

    def __init__(self, dev, hass, add_entities):
        """Initialize a Meross Light"""
        _LOGGER.warning("HI1!")
        add_entities([MerossLight(dev)])

class MerossLight(Light):
    """Representation of an Awesome Light."""

    def __init__(self, light):
        """Initialize an AwesomeLight."""
        self._light = light
        self._name = light._name
        self._state = None
        self._brightness = None
        self._rgb = None
        self._light.get_status()
        _LOGGER.warning("HI!")

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    def turn_on(self, **kwargs):
        """Turn on or control the light."""
        self._light.turn_on()
        rgb = self._light.get_light_color().get('rgb')
        _LOGGER.warning(rgb)
        color = rgb_to_color(rgb)
        brightness = self._light.get_light_color().get('luminance')
        _LOGGER.warning(kwargs)

        if 'hs_color' in kwargs:
            h, s = kwargs['hs_color']
            r, g, b = colorsys.hsv_to_rgb(h/360, s/100, 255)
            color = (int(r), int(g), int(b))
            _LOGGER.warning(color)
            
        if 'brightness' in kwargs:
            brightness = kwargs['brightness'] / 255 * 100

        _LOGGER.warning(color)
        self._light.set_light_color(rgb=color, luminance=brightness, capacity=5)

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.turn_off()
    
    @property
    def brightness(self):
        # Meross bulbs support luminance between 0 and 100;
        # while the HA wants values from 0 to 255. Therefore, we need to scale the values.
        status = self._light.get_status()
        return status.get('luminance') / 100 * 255

    @property
    def hs_color(self):
        color = self._light.get_status().get('rgb')
        blue = color & 255
        green = (color >> 8) & 255
        red = (color >> 16) & 255
        h, s, v = colorsys.rgb_to_hsv(red, green, blue)
        return [h*360, s*100]
        
    @property
    def is_on(self) -> bool:
        # Note that the following method is not fetching info from the device over the network.
        # Instead, it is reading the device status from the state-dictionary that is handled by the library.
        return self._light.get_status().get('onoff')

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.info(self._light.get_status())
        
    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR
