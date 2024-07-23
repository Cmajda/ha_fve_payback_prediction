import datetime
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, CURRENCY_CZK
from homeassistant.helpers.template import Template
from homeassistant.util.dt import parse_datetime

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the FVE sensors."""
    async_add_entities([
        FveDailySavingsSensor(hass),
        FveMonthlySavingsSensor(hass),
        FveYearlySavingsSensor(hass),
        FveEstimatedPaybackSensor(hass),
        FveAverageDailyProductionSensor(hass),
        FveRealEstimatedPaybackSensor(hass),
        FveEstimatedPaybackTextSensor(hass),
        FveRealEstimatedPaybackTextSensor(hass),
    ])

class FveDailySavingsSensor(SensorEntity):
    """Sensor for daily savings."""

    @property
    def name(self):
        return "FVE denní úspora"

    @property
    def unique_id(self):
        return "fve_denni_uspora"

    @property
    def state(self):
        solar_energy = float(self.hass.states.get('sensor.solaxg410kw_today_s_solar_energy').state)
        price_per_kwh = float(self.hass.states.get('input_number.fve_cena_za_kwh').state)
        return round(solar_energy * price_per_kwh, 2)

    @property
    def unit_of_measurement(self):
        return CURRENCY_CZK

class FveMonthlySavingsSensor(SensorEntity):
    """Sensor for monthly savings."""

    @property
    def name(self):
        return "FVE měsíční úspora"

    @property
    def unique_id(self):
        return "fve_mesicni_uspora"

    @property
    def state(self):
        today = datetime.datetime.now().day
        total_solar_energy = float(self.hass.states.get('sensor.solaxg410kw_total_solar_energy').state)
        daily_avg = total_solar_energy / today
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        next_month = month + 1 if month < 12 else 1
        next_month_year = year if next_month > 1 else year + 1
        days_in_month = (datetime.datetime(next_month_year, next_month, 1) - timedelta(days=1)).day
        estimated_monthly_energy = daily_avg * days_in_month
        price_per_kwh = float(self.hass.states.get('input_number.fve_cena_za_kwh').state)
        return round(estimated_monthly_energy * price_per_kwh, 2)

    @property
    def unit_of_measurement(self):
        return CURRENCY_CZK

class FveYearlySavingsSensor(SensorEntity):
    """Sensor for yearly savings."""

    @property
    def name(self):
        return "FVE roční úspora"

    @property
    def unique_id(self):
        return "fve_rocni_uspora"

    @property
    def state(self):
        total_solar_energy = float(self.hass.states.get('sensor.solaxg410kw_total_solar_energy').state)
        start_date_str = self.hass.states.get('input_datetime.fve_zacatek_vyroby').state
        if start_date_str not in ['unknown', 'unavailable', 'None'] and start_date_str:
            start_date = parse_datetime(start_date_str)
            days_since_start = (datetime.datetime.now().date() - start_date.date()).days
            if days_since_start > 0:
                daily_avg = total_solar_energy / days_since_start
                estimated_yearly_energy = daily_avg * 365
                price_per_kwh = float(self.hass.states.get('input_number.fve_cena_za_kwh').state)
                return round(estimated_yearly_energy * price_per_kwh, 2)
        return 0

    @property
    def unit_of_measurement(self):
        return CURRENCY_CZK

# Další senzory budou definovány podobným způsobem...

# Příklad dalšího senzoru:
class FveEstimatedPaybackSensor(SensorEntity):
    """Sensor for estimated payback."""

    @property
    def name(self):
        return "FVE odhadovaná návratnost"

    @property
    def unique_id(self):
        return "fve_odhadovana_navratnost"

    @property
    def state(self):
        cena_za_kw = float(self.hass.states.get('input_number.fve_cena_za_kwh').state)
        pocatecni_investice = float(self.hass.states.get('input_number.fve_pocatecni_investice').state)
        odhadovana_denni_vyroba_fve = float(self.hass.states.get('input_number.fve_odhadovana_denni_vyroba').state)
        if odhadovana_denni_vyroba_fve > 0:
            return round(pocatecni_investice / cena_za_kw / odhadovana_denni_vyroba_fve, 2)
        return 0

    @property
    def unit_of_measurement(self):
        return "Dnů"

# Pokračujte v implementaci dalších senzorů...
