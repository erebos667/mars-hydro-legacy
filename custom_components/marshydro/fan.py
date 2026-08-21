from homeassistant.components.fan import FanEntity, FanEntityFeature
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarsHydroFan(data["api"], data["coordinator"])])

class MarsHydroFan(FanEntity):
    _attr_has_entity_name = True
    _attr_name = "Fan"
    _attr_supported_features = FanEntityFeature.SET_SPEED

    def __init__(self, api, coordinator):
        self.api = api
        self.coordinator = coordinator
        self._attr_unique_id = "marshydro_fan"

    @property
    def _device(self):
        return self.coordinator.data.get("fan") if self.coordinator.data else None

    @property
    def available(self):
        return self.coordinator.last_update_success and self._device is not None

    @property
    def percentage(self):
        return max(25, min(100, int(float(self._device.get("deviceLightRate", 25)))))

    @property
    def is_on(self):
        return not bool(self._device.get("isClose"))

    @property
    def device_info(self):
        if not self._device: return None
        return {"identifiers": {(DOMAIN, str(self._device.get("id")))}, "name": self._device.get("deviceName", "Mars Hydro Fan"), "manufacturer": "Mars Hydro", "model": "Legacy"}

    async def async_set_percentage(self, percentage):
        await self.api.set_fanspeed(max(25, min(100, int(percentage))), self._device["id"])
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.api.toggle_switch(True, self._device["id"])
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self.api.toggle_switch(False, self._device["id"])
        await self.coordinator.async_request_refresh()
