"""Platform for sensor integration."""
from __future__ import annotations
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=1)  # Set to 1 minute
_LOGGER = logging.getLogger(__name__)

DOMAIN = "fve_payback_prediction"
CONF_SOLAR_ENERGY_SENSOR_TODAY = "solar_energy_sensor_today"
CONF_PRICE_PER_KWH_SENSOR = "price_per_kwh_sensor"

CONF_HUMAN_NAME = "Daily Savings"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SOLAR_ENERGY_SENSOR_TODAY): cv.string,
        vol.Required(CONF_PRICE_PER_KWH_SENSOR): cv.string,
    }
)

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities, discovery_info: DiscoveryInfoType = None):
    """Set up the fve_payback_prediction sensor platform."""
    solar_energy_sensor_today = config.get(CONF_SOLAR_ENERGY_SENSOR_TODAY)
    price_per_kwh_sensor = config.get(CONF_PRICE_PER_KWH_SENSOR)
    
    add_entities([FveDailySavingsSensor(hass, solar_energy_sensor_today, price_per_kwh_sensor)])

class FveDailySavingsSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, solar_energy_sensor_today: str, price_per_kwh_sensor: str):
        """Initialize the sensor."""
        self.hass = hass
        self.solar_energy_sensor_today = solar_energy_sensor_today
        self.price_per_kwh_sensor = price_per_kwh_sensor
        self._state = None
        self._name = CONF_HUMAN_NAME
        self._unique_id = DOMAIN + "_daily_savings"
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._unique_id
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:currency-usd"

    @property
    def should_poll(self):
        """Return True if the sensor should be polled."""
        return True
        
    @Throttle(MIN_TIME_BETWEEN_SCANS)
    def update(self):
        """Update the sensor state."""
        # Fetch the latest state from the sensors
        solar_energy_state = self.hass.states.get(self.solar_energy_sensor_today)
        price_per_kwh_state = self.hass.states.get(self.price_per_kwh_sensor)

        _LOGGER.debug(f"Fetching sensor values: {self.solar_energy_sensor_today} = {solar_energy_state}, {self.price_per_kwh_sensor} = {price_per_kwh_state}")

        # Convert None to 0 and handle potential conversion errors
        try:
            solar_energy = float(solar_energy_state.state) if solar_energy_state and solar_energy_state.state not in ['unknown', 'unavailable'] else 0.0
            price_per_kwh = float(price_per_kwh_state.state) if price_per_kwh_state and price_per_kwh_state.state not in ['unknown', 'unavailable'] else 0.0
            self._state = solar_energy * price_per_kwh
            _LOGGER.debug(f"Calculated state: {self._state} (solar_energy: {solar_energy}, price_per_kwh: {price_per_kwh})")
        except ValueError as e:
            _LOGGER.error(f"Error converting sensor values to float: {e}")
            self._state = 0.0

        if solar_energy_state is None or price_per_kwh_state is None:
            _LOGGER.warning(f"One or both sensors are unavailable: {self.solar_energy_sensor_today} = {solar_energy_state}, {self.price_per_kwh_sensor} = {price_per_kwh_state}. Set to default value 0.0")
