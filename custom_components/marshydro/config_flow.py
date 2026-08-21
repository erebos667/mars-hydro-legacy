import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from .api import MarsHydroAPI
from .const import DOMAIN

class MarsHydroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input:
            try:
                api = MarsHydroAPI(user_input["email"], user_input["password"])
                await api.login()
                await self.async_set_unique_id(user_input["email"].lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Mars Hydro Legacy", data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )
