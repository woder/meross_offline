"""Platform for light integration."""
import logging
import colorsys
import time

from homeassistant.components.light import (
    ATTR_RGB_COLOR, ATTR_COLOR_TEMP, ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, SUPPORT_COLOR, PLATFORM_SCHEMA, Light)
from homeassistant.components.climate import (
    SUPPORT_TARGET_HUMIDITY, ClimateDevice)

from homeassistant.components.climate.const import (
    ATTR_PRESET_MODE,
    CURRENT_HVAC_DRY,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_DRY,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    PRESET_NONE,
)

from homeassistant.helpers.event import async_track_state_change

# Meross libs
from meross_iot.supported_devices.humidifiers import GenericHumidifier

_LOGGER = logging.getLogger("Meross_Humidifier")
AUTO = "Auto"
OFF = "Off"
INTER = "Intermittent"


class MHumidifier():
    """Representation of a Meross Humidifier"""

    def __init__(self, dev, hass, add_entities):
        """Initialize a Meross Humidifier"""
        entities = []
        entities.append(MerossHumidifier(hass, dev))
        add_entities(entities)


class MHumidifierLight():
    """Representation of a Meross Humidifier"""

    def __init__(self, dev, hass, add_entities):
        """Initialize a Meross Humidifier"""
        entities = []
        entities.append(HumidifierLight(dev))
        add_entities(entities)


class MerossHumidifier(ClimateDevice):
    """Representation of an Awesome Light."""

    def __init__(self, hass, dev):
        """Initialize an AwesomeLight."""
        self._dev = dev
        self._name = dev._name
        self._set_point = 40
        self._mode = "Off"
        self._dev.get_status()
        self._hvac_list = [HVAC_MODE_DRY, HVAC_MODE_OFF]
        self._hvac_mode = HVAC_MODE_OFF
        self._unit = hass.config.units.temperature_unit
        async_track_state_change(hass, "sensor.humidity", self.humidity_change, from_state=None, to_state=None)

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    def set_humidity(self, humidity):
        """Set new target humidity."""
        self._set_point = humidity

    async def async_set_humidity(self, humidity):
        """Set new target humidity."""
        self._set_point = humidity

    def humidity_change(self, eid, old_state, new_state):
        if self._hvac_mode == HVAC_MODE_OFF or self._mode == OFF:
            return

        if float(new_state.state) < self._set_point:
            self._dev.turn_on()
        else:
            self._dev.turn_off()

    def set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        self.handle_preset_mode(preset_mode)

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        self.handle_preset_mode(preset_mode)

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        self.handle_hvac_mode(hvac_mode)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        self.handle_hvac_mode(hvac_mode)

    def handle_hvac_mode(self, hvac_mode):
        """Control the hvac mode"""
        self._hvac_mode = hvac_mode
        if self._hvac_mode == HVAC_MODE_OFF:
            self._dev.turn_off()
        elif self._hvac_mode == HVAC_MODE_DRY:
            if self._mode == OFF:
                self._mode = AUTO

            self._dev.turn_on()
        else:
            self._dev.turn_off()

    def handle_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        self._mode = preset_mode
        if self._mode == AUTO:
            self._hvac_mode = HVAC_MODE_DRY
            self._dev.turn_on()
        elif self._mode == INTER:
            self._hvac_mode = HVAC_MODE_DRY
            self._dev.turn_intermittent()
        else:
            self._hvac_mode = HVAC_MODE_OFF
            self._dev.turn_off()

    @property
    def hvac_mode(self):
        """Return current operation."""
        return self._hvac_mode

    @property
    def hvac_action(self):
        """Return the current running hvac operation if supported.

        Need to be one of CURRENT_HVAC_*.
        """
        if self._hvac_mode == HVAC_MODE_OFF:
            return CURRENT_HVAC_OFF
        if not self.is_on:
            return CURRENT_HVAC_IDLE
        if self._hvac_mode == HVAC_MODE_DRY:
            return CURRENT_HVAC_DRY
        return CURRENT_HVAC_DRY

    @property
    def hvac_modes(self):
        """List of available operation modes."""
        return self._hvac_list

    @property
    def preset_modes(self):
        return [AUTO, INTER, OFF]

    @property
    def preset_mode(self):
        return self._mode

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def target_humidity(self):
        """Return the current target humidity"""
        return self._set_point

    @property
    def is_on(self) -> bool:
        # Note that the following method is not fetching info from the device over the network.
        # Instead, it is reading the device status from the state-dictionary that is handled by the library.
        return self._dev.get_status().get('mode') != 0

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.info(self._dev.get_status())

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_TARGET_HUMIDITY | SUPPORT_PRESET_MODE


class HumidifierLight(Light):
    """Representation of an Awesome Light."""

    def __init__(self, dev):
        """Initialize an AwesomeLight."""
        self._dev = dev
        self._name = dev._name
        self._state = None
        self._dev.get_status()

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self._dev.disable_dnd()

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        self._dev.disable_dnd()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._dev.enable_dnd()

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        self._dev.enable_dnd()

    @property
    def is_on(self) -> bool:
        # Note that the following method is not fetching info from the device over the network.
        # Instead, it is reading the device status from the state-dictionary that is handled by the library.
        dnd = self._dev.get_status().get('DNDMode')
        if dnd is not None:
            return dnd.get('mode') != 1
        return True

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.info(self._dev.get_status())

    @property
    def supported_features(self):
        """Flag supported features."""
        return 0
