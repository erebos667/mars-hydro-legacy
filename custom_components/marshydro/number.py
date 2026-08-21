from homeassistant.components.number import NumberEntity, NumberMode

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarsHydroFanSpeed(data["api"], data["coordinator"])])


class MarsHydroFanSpeed(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Fan Speed"
    _attr_icon = "mdi:fan-speed-3"
    _attr_native_min_value = 25
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, api, coordinator):
        self.api = api
        self.coordinator = coordinator
        self._attr_unique_id = "marshydro_fan_speed"

    @property
    def _device(self):
        return self.coordinator.data.get("fan") if self.coordinator.data else None

    @property
    def available(self):
        return self.coordinator.last_update_success and self._device is not None

    @property
    def native_value(self):
        if not self._device:
            return None
        try:
            return max(25, min(100, int(float(self._device.get("deviceLightRate", 25)))))
        except (TypeError, ValueError):
            return 25

    @property
    def device_info(self):
        if not self._device:
            return None
        return {
            "identifiers": {(DOMAIN, str(self._device.get("id")))},
            "name": self._device.get("deviceName", "Mars Hydro Fan"),
            "manufacturer": "Mars Hydro",
            "model": "Legacy",
        }

    async def async_set_native_value(self, value):
        speed = max(25, min(100, int(value)))
        await self.api.set_fanspeed(speed, self._device["id"])
        await self.coordinator.async_request_refresh()
