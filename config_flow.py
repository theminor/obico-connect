import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_AUTH_TOKEN, CONF_ENDPOINT_PREFIX, DEFAULT_NAME
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class ObicoConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.endpoint_prefix = user_input[CONF_ENDPOINT_PREFIX]
            self.auth_token = None
            return await self.async_step_verification_code()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ENDPOINT_PREFIX, default="https://app.obico.io"): str,
                }
            ),
        )

    async def async_step_verification_code(self, user_input=None):
        if user_input is not None:
            verification_code = user_input["verification_code"]
            self.auth_token = await self.verify_code(verification_code)
            if self.auth_token:
                return self.async_create_entry(title=DEFAULT_NAME, data={
                    CONF_AUTH_TOKEN: self.auth_token,
                    CONF_ENDPOINT_PREFIX: self.endpoint_prefix
                })

        return self.async_show_form(
            step_id="verification_code",
            data_schema=vol.Schema(
                {
                    vol.Required("verification_code"): str,
                }
            ),
        )

    async def verify_code(self, code):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.endpoint_prefix}/api/v1/octo/verify/?code={code}") as response:
                    if response.status == 200:
                        data = await response.json()
                        printer = data.get("printer")
                        if printer:
                            return printer.get("auth_token")
            except Exception as e:
                _LOGGER.error(f"Error making GET request: {e}")
        return None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ObicoConnectOptionsFlow(config_entry)

class ObicoConnectOptionsFlow(config_entries.OptionsFlowWithConfigEntry):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ENDPOINT_PREFIX, default=self.config_entry.options.get(CONF_ENDPOINT_PREFIX, "https://app.obico.io")): str,
                }
            ),
        )