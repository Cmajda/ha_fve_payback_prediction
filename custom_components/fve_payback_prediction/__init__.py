"""The fve_payback_prediction component."""
import logging
import voluptuous as vol
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fve_payback_prediction"
CONF_SOLAR_ENERGY_SENSOR = "solar_energy_sensor_today"
CONF_PRICE_PER_KWH_SENSOR = "price_per_kwh_sensor"

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOLAR_ENERGY_SENSOR): cv.string,
        vol.Required(CONF_PRICE_PER_KWH_SENSOR): cv.string,
    }
)

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up the fve_payback_prediction component from a config entry."""
    _LOGGER.debug("Setting up fve_payback_prediction component.")
    
    # Extract configuration data
    platform_config = entry.data
    _LOGGER.debug(f"Platform config: {platform_config}")

    # Get sensor names from configuration
    solar_energy_sensor = platform_config.get(CONF_SOLAR_ENERGY_SENSOR)
    price_per_kwh_sensor = platform_config.get(CONF_PRICE_PER_KWH_SENSOR)

    if not solar_energy_sensor or not price_per_kwh_sensor:
        _LOGGER.error("Senzory 'solar_energy_sensor' a 'price_per_kwh_sensor' musí být definovány v configuration.yaml")
        return False

    _LOGGER.debug(f"Solar energy sensor: {solar_energy_sensor}")
    _LOGGER.debug(f"Price per kWh sensor: {price_per_kwh_sensor}")

    # Initialize the coordinator
    coordinator = FvePaybackCoordinator(hass, solar_energy_sensor, price_per_kwh_sensor)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in hass data
    hass.data[DOMAIN] = coordinator
    _LOGGER.debug("Coordinator set up and stored in hass data.")

    # Set up the platform
    await hass.config_entries.async_forward_entry_setup(entry, 'sensor')
    _LOGGER.debug("Sensor platform setup complete.")
    return True

class FvePaybackCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, solar_energy_sensor, price_per_kwh_sensor):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )
        self.solar_energy_sensor = solar_energy_sensor
        self.price_per_kwh_sensor = price_per_kwh_sensor
        self.solar_energy = 0.0
        self.price_per_kwh = 0.0

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            solar_energy_state = self.hass.states.get(self.solar_energy_sensor)
            price_per_kwh_state = self.hass.states.get(self.price_per_kwh_sensor)

            _LOGGER.debug(f"Fetching data: {self.solar_energy_sensor} state: {solar_energy_state}")
            _LOGGER.debug(f"Fetching data: {self.price_per_kwh_sensor} state: {price_per_kwh_state}")

            if solar_energy_state is None:
                _LOGGER.error(f"Senzor '{self.solar_energy_sensor}' chybí.")
                self.solar_energy = 0.0
            else:
                solar_energy = solar_energy_state.state
                if solar_energy in ['unknown', 'unavailable']:
                    _LOGGER.warning(f"Neplatná hodnota solar_energy='{solar_energy}', nastavena na 0")
                    self.solar_energy = 0.0
                else:
                    self.solar_energy = float(solar_energy)

            if price_per_kwh_state is None:
                _LOGGER.error(f"Senzor '{self.price_per_kwh_sensor}' chybí.")
                self.price_per_kwh = 0.0
            else:
                price_per_kwh = price_per_kwh_state.state
                if price_per_kwh in ['unknown', 'unavailable']:
                    _LOGGER.warning(f"Neplatná hodnota price_per_kwh='{price_per_kwh}', nastavena na 0")
                    self.price_per_kwh = 0.0
                else:
                    self.price_per_kwh = float(price_per_kwh)

            _LOGGER.debug(f"Data updated: solar_energy={self.solar_energy}, price_per_kwh={self.price_per_kwh}")
            return {
                "solar_energy": self.solar_energy,
                "price_per_kwh": self.price_per_kwh
            }
        except Exception as e:
            _LOGGER.error(f"Error in _async_update_data: {e}")
            raise UpdateFailed(f"Error communicating with API: {e}")
