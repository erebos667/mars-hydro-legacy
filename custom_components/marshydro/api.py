import aiohttp
import asyncio
import json
import logging
import time

_LOGGER = logging.getLogger(__name__)

class MarsHydroAPI:
    BASE = "https://api.lgledsolutions.com/api/android"

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.device_id = None
        self._lock = asyncio.Lock()
        self.last_login_time = 0
        self.login_interval = 300

    def _system_data(self):
        return json.dumps({
            "reqId": int(time.time() * 1000), "appVersion": "1.2.0",
            "osType": "android", "osVersion": "14", "deviceType": "SM-S928C",
            "deviceId": self.device_id, "netType": "wifi", "wifiName": "123",
            "timestamp": int(time.time()), "token": self.token,
            "timezone": "Europe/Berlin", "language": "German"
        })

    async def _post(self, path, payload):
        headers = {"systemData": self._system_data(), "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.BASE}{path}", headers=headers, json=payload) as response:
                response.raise_for_status()
                return await response.json(content_type=None)

    async def login(self):
        async with self._lock:
            now = time.time()
            if self.token and now - self.last_login_time < self.login_interval:
                return
            data = await self._post("/ulogin/mailLogin/v1", {
                "email": self.email, "password": self.password, "loginMethod": "1"
            })
            token = data.get("data", {}).get("token")
            if not token:
                raise RuntimeError(data.get("msg", "Mars Hydro login failed"))
            self.token = token
            self.last_login_time = now

    async def _call(self, path, payload, retry=True):
        if not self.token:
            await self.login()
        data = await self._post(path, payload)
        if data.get("code") == "102" and retry:
            self.token = None
            await self.login()
            return await self._call(path, payload, False)
        return data

    async def _process_device_list(self, product_type):
        data = await self._call("/udm/getDeviceList/v1", {
            "currentPage": 0, "type": None, "productType": product_type
        })
        if data.get("code") != "000":
            raise RuntimeError(data.get("msg", "Mars Hydro API error"))
        return data.get("data", {}).get("list", [])

    async def get_devices(self):
        lights = await self._process_device_list("LIGHT")
        fans = await self._process_device_list("WIND")
        return (lights[0] if lights else None), (fans[0] if fans else None)

    async def toggle_switch(self, is_close, device_id):
        return await self._call("/udm/lampSwitch/v1", {
            "isClose": is_close, "deviceId": device_id, "groupId": None
        })

    async def set_brightness(self, brightness, device_id=None):
        device_id = device_id or self.device_id
        if not device_id:
            light, _ = await self.get_devices()
            if not light:
                raise RuntimeError("No Mars Hydro light found")
            device_id = light.get("id")
            self.device_id = device_id
        return await self._call("/udm/adjustLight/v1", {
            "light": int(brightness), "deviceId": device_id, "groupId": None
        })

    async def set_fanspeed(self, speed, device_id):
        return await self._call("/udm/adjustLight/v1", {
            "light": int(speed), "deviceId": device_id, "groupId": None
        })
