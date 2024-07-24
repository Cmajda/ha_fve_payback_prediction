"""Sensor platform for fve_payback_prediction."""
import logging
import random
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fve_payback_prediction"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the FVE sensor from a config entry."""
    _LOGGER.debug("Setting up FVE sensor from config entry.")

    coordinator = hass.data.get(DOMAIN)
    if coordinator is None:
        _LOGGER.error("Coordinator not found. Make sure the fve_payback_prediction component is set up correctly.")
        return

    async_add_entities([FveDailySavingsSensor(coordinator)], True)
    _LOGGER.debug("FVE sensor entity added.")

class FveDailySavingsSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._state = None
        self._unique_id = f"{DOMAIN}_denni_uspora_{random.randint(1000, 9999)}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return "Denní úspora"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "Kč"

    @property
    def icon(self):
        return "mdi:currency-usd"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            await self.coordinator.async_request_refresh()
            data = self.coordinator.data
            solar_energy = data["solar_energy"]
            price_per_kwh = data["price_per_kwh"]
            self._state = round(solar_energy * price_per_kwh, 2)
            _LOGGER.debug(f"Sensor updated: state={self._state}, solar_energy={solar_energy}, price_per_kwh={price_per_kwh}")
        except Exception as e:
            _LOGGER.error(f"Error in async_update: {e}")
            self._state = None
