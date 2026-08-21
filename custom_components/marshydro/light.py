from homeassistant.components.light import LightEntity, ColorMode
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    d = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarsHydroLight(d["api"], d["coordinator"])])

class MarsHydroLight(LightEntity):
    _attr_has_entity_name = True
    _attr_name = "Light"
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, api, coordinator):
        self.api, self.coordinator = api, coordinator
        self._attr_unique_id = "marshydro_light"

    @property
    def _data(self): return self.coordinator.data.get("light") if self.coordinator.data else None
    @property
    def available(self): return self.coordinator.last_update_success and bool(self._data)
    @property
    def is_on(self): return not self._data.get("isClose")
    @property
    def brightness(self): return round(float(self._data.get("deviceLightRate", 0)) * 255 / 100)
    @property
    def device_info(self):
        if not self._data: return None
        return {"identifiers": {(DOMAIN, str(self._data.get("id")))}, "name": self._data.get("deviceName", "Mars Hydro Light"), "manufacturer": "Mars Hydro", "model": "Legacy"}

    async def async_turn_on(self, **kwargs):
        await self.api.toggle_switch(False, self._data["id"])
        if "brightness" in kwargs:
            await self.api.set_brightness(round(kwargs["brightness"] * 100 / 255), self._data["id"])
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.api.toggle_switch(True, self._data["id"])
        await self.coordinator.async_request_refresh()

    async def async_set_brightness(self, brightness):
        await self.api.set_brightness(round(brightness * 100 / 255), self._data["id"])
        await self.coordinator.async_request_refresh()
