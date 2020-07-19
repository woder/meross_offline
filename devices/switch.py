"""Platform for light integration."""
import logging
import colorsys

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import SwitchDevice
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_RGB_COLOR, ATTR_COLOR_TEMP, ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, SUPPORT_COLOR, PLATFORM_SCHEMA, Light)

from homeassistant.util import color as colorutil

# Meross libs
from meross_iot.supported_devices.power_plugs import GenericPlug

_LOGGER = logging.getLogger("Meross_Switch")


class MSwitch():
    """Representation of a Meross Switch"""

    def __init__(self, dev, hass, add_entities):
        """Initialize a Meross Switch"""
        add_entities([MerossSwitch(dev)])


class MerossSwitch(SwitchDevice):
    """Representation of an Awesome Light."""

    def __init__(self, switch):
        """Initialize an AwesomeLight."""
        self._switch = switch
        self._name = switch._name
        self._state = None
        self._channel_id = 0
        self._switch.get_status()
        _LOGGER.warning("HI! ")
        _LOGGER.warning(self._switch._channels)

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def today_energy_kwh(self):
        """Return the today total energy usage in kWh."""
        return None

    @property
    def available(self) -> bool:
        # A device is available if it's online
        return True

    @property
    def should_poll(self) -> bool:
        # In general, we don't want HomeAssistant to poll this device.
        # Instead, we will notify HA when an event is received.
        return False

    @property
    def is_on(self) -> bool:
        # Note that the following method is not fetching info from the device over the network.
        # Instead, it is reading the device status from the state-dictionary that is handled by the library.
        return self._switch.get_channel_status(self._channel_id)

    def turn_off(self, **kwargs) -> None:
        self._switch.turn_off_channel(self._channel_id)

    def turn_on(self, **kwargs) -> None:
        self._switch.turn_on_channel(self._channel_id)

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.info(self._switch.get_status())
