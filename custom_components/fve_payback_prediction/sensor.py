import logging
import random
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fve_payback_prediction"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the FVE sensor."""
    coordinator = hass.data.get(DOMAIN)
    if coordinator is None:
        _LOGGER.error("Coordinator is not set up.")
        return

    async_add_entities([FveDailySavingsSensor(coordinator)], True)

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
        await self.coordinator.async_request_refresh()
        data = self.coordinator.data
        solar_energy = data["solar_energy"]
        price_per_kwh = data["price_per_kwh"]
        self._state = round(solar_energy * price_per_kwh, 2)
