import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector
from .const import DOMAIN, CONF_AUTH_TOKEN, CONF_ENDPOINT_PREFIX, DEFAULT_NAME
import aiohttp
import logging
import homeassistant.helpers.entity_registry as async_get_entity_registry

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class ObicoConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.endpoint_prefix = user_input[CONF_ENDPOINT_PREFIX]
            self.device_type = user_input["device_type"]
            self.auth_token = None
            return await self.async_step_verification_and_camera()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENDPOINT_PREFIX, default="https://app.obico.io", description="Enter the URL to the Obico Server (including port, if applicable)"): str,
                    vol.Required("device_type", description="Select the type of Printer you will connect from Home Assistant"): vol.In(["Bambu Lab", "Moonraker"]),
                }
            ),
        )

    async def async_step_verification_and_camera(self, user_input=None):
        if user_input is not None:
            verification_code = user_input["verification_code"]
            self.auth_token = await self.verify_code(verification_code)
            if self.auth_token:
                camera_entity_id = user_input["camera_entity_id"]
                update_interval = user_input.get("update_interval", 5)
                printer_device_id = user_input["printer_device_id"]
                return self.async_create_entry(title=DEFAULT_NAME, data={
                    CONF_AUTH_TOKEN: self.auth_token,
                    CONF_ENDPOINT_PREFIX: self.endpoint_prefix,
                    "camera_entity_id": camera_entity_id,
                    "update_interval": update_interval,
                    "printer_device_id": printer_device_id,
                    "device_type": self.device_type
                })

        registry = async_get_entity_registry.async_get(self.hass)
        camera_entities = [entity.entity_id for entity in registry.entities.values() if entity.domain == "camera"]
        integration_type = "bambu_lab" if self.device_type == "Bambu Lab" else "moonraker"

        return self.async_show_form(
            step_id="verification_and_camera",
            data_schema=vol.Schema(
                {
                    vol.Required("verification_code", description="Enter the verification code provided by the Obico Server"): str,
                    vol.Required("printer_device_id", description="Select the printer device to monitor"): selector({"device": {"integration": integration_type}}),
                    vol.Required("camera_entity_id", description="Select the camera entity to use"): vol.In(camera_entities),
                    vol.Optional("update_interval", default=5, description="Enter the update interval (in seconds)"): vol.All(vol.Coerce(int), vol.Range(min=1, max=300)),
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

        if user_input is not None:
            endpoint_prefix = user_input.get(CONF_ENDPOINT_PREFIX, "").rstrip("/")
            return self.async_create_entry(title="", data={CONF_ENDPOINT_PREFIX: endpoint_prefix})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
            {
                vol.Optional(CONF_ENDPOINT_PREFIX, default=self.config_entry.options.get(CONF_ENDPOINT_PREFIX, "https://app.obico.io")): str,
            }
            ),
        )