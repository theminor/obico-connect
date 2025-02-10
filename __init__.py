import logging
import requests
import voluptuous as vol
import asyncio
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from .const import DOMAIN, DEFAULT_NAME, CONF_AUTH_TOKEN, CONF_ENDPOINT_PREFIX

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_AUTH_TOKEN): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_ENDPOINT_PREFIX, default="https://app.obico.io"): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=60): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    conf = config.get(DOMAIN)

    if conf is None:
        return True

    name = conf[CONF_NAME]
    auth_token = conf[CONF_AUTH_TOKEN]
    endpoint_prefix = conf[CONF_ENDPOINT_PREFIX]
    scan_interval = conf[CONF_SCAN_INTERVAL]

    hass.data[DOMAIN] = {
        "name": name,
        "auth_token": auth_token,
        "endpoint_prefix": endpoint_prefix,
        "scan_interval": scan_interval,
    }

    load_platform(hass, "sensor", DOMAIN, {}, config)
    load_platform(hass, "camera", DOMAIN, {}, config)

    return True

async def async_setup_entry(hass, entry):
    """Set up Obico Connect from a config entry."""
    _LOGGER.info("Setting up Obico Connect")
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    _LOGGER.info("Unloading Obico Connect")
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True

async def post_printer_status(hass, auth_token, endpoint_prefix):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {auth_token}'}
                async with session.post(f"{endpoint_prefix}/api/v1/octo/printer_status/", headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Failed to post printer status: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error posting printer status: {e}")

        await asyncio.sleep(60)  # Send heartbeat every 60 seconds

# Start the heartbeat task
hass.loop.create_task(post_printer_status(hass, auth_token, endpoint_prefix))