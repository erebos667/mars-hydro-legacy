from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarsSwitch(data["api"], data["coordinator"], "light"), MarsSwitch(data["api"], data["coordinator"], "fan")])

class MarsSwitch(SwitchEntity):
    _attr_has_entity_name = True
    def __init__(self, api, coordinator, kind):
        self.api, self.coordinator, self.kind = api, coordinator, kind
        self._attr_name = f"{kind.capitalize()} Power"
        self._attr_unique_id = f"marshydro_{kind}_power"
    @property
    def _device(self): return self.coordinator.data.get(self.kind) if self.coordinator.data else None
    @property
    def available(self): return self.coordinator.last_update_success and self._device is not None
    @property
    def is_on(self): return not bool(self._device.get("isClose"))
    @property
    def device_info(self):
        if not self._device: return None
        return {"identifiers": {(DOMAIN, str(self._device.get("id")))}, "name": self._device.get("deviceName", "Mars Hydro"), "manufacturer": "Mars Hydro", "model": "Legacy"}
    async def async_turn_on(self, **kwargs):
        await self.api.toggle_switch(False, self._device["id"])
        await self.coordinator.async_request_refresh()
    async def async_turn_off(self, **kwargs):
        await self.api.toggle_switch(True, self._device["id"])
        await self.coordinator.async_request_refresh()
