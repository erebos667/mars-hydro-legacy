from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([MarsSensor(c, "brightness", "%", None, "light"), MarsSensor(c, "temperature", "°F", SensorDeviceClass.TEMPERATURE, "fan"), MarsSensor(c, "temperature_c", "°C", SensorDeviceClass.TEMPERATURE, "fan"), MarsSensor(c, "humidity", "%", SensorDeviceClass.HUMIDITY, "fan"), MarsSensor(c, "speed", "RPM", None, "fan")])

class MarsSensor(SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, kind, unit, device_class, source):
        self.coordinator, self.kind, self.source = coordinator, kind, source
        self._attr_name = kind.replace("_", " ").title()
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_unique_id = f"marshydro_{kind}"
    @property
    def _device(self): return self.coordinator.data.get(self.source) if self.coordinator.data else None
    @property
    def available(self): return self.coordinator.last_update_success and self._device is not None
    @property
    def device_info(self):
        if not self._device: return None
        return {"identifiers": {(DOMAIN, str(self._device.get("id")))}, "name": self._device.get("deviceName", "Mars Hydro"), "manufacturer": "Mars Hydro", "model": "Legacy"}
    @property
    def native_value(self):
        d = self._device
        if not d: return None
        if self.kind == "brightness": return d.get("deviceLightRate")
        if self.kind == "temperature": return d.get("temperature")
        if self.kind == "temperature_c":
            try: return round((float(d.get("temperature")) - 32) * 5 / 9, 1)
            except (TypeError, ValueError): return None
        if self.kind == "humidity": return d.get("humidity")
        return d.get("speed")
