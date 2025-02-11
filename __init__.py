import logging
import requests
import voluptuous as vol
import asyncio
import aiohttp
from datetime import timedelta
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
    _LOGGER.error("async_setup called")
    _LOGGER.error(f"Config: {config}")

    conf = config.get(DOMAIN)
    if conf is None:
        _LOGGER.error("No configuration found for DOMAIN")
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

    _LOGGER.error(f"Configuration loaded: {hass.data[DOMAIN]}")

    load_platform(hass, "sensor", DOMAIN, {}, config)
    load_platform(hass, "camera", DOMAIN, {}, config)

    async def post_printer_status(now):
        _LOGGER.error("post_printer_status called")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {auth_token}'}
                payload = {
                    # Add more detailed status information here
                    "status": "online",
                    "temperature": 200,  # Example temperature value
                    "job": {
                        "file": "example.gcode",
                        "progress": 50  # Example progress value
                    }
                }
                async with session.post(f"{endpoint_prefix}/api/v1/octo/printer_status/", headers=headers, json=payload) as response:
                    response_text = await response.text()
                    _LOGGER.error(f"Response status: {response.status}")
                    _LOGGER.error(f"Response text: {response_text}")
                    if response.status != 200:
                        _LOGGER.error(f"Failed to post printer status: {response.status} - {response_text}")
                    else:
                        _LOGGER.error(f"Successfully posted printer status: {response.status} - {response_text}")
        except Exception as e:
            _LOGGER.error(f"Error posting printer status: {e}")

    async def initial_registration():
        _LOGGER.error("initial_registration called")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {auth_token}'}
                payload = {
                    "name": name,
                    "status": "online"
                }
                async with session.post(f"{endpoint_prefix}/api/v1/octo/register/", headers=headers, json=payload) as response:
                    response_text = await response.text()
                    _LOGGER.error(f"Response status: {response.status}")
                    _LOGGER.error(f"Response text: {response_text}")
                    if response.status != 200:
                        _LOGGER.error(f"Failed to register printer: {response.status} - {response_text}")
                    else:
                        _LOGGER.error(f"Successfully registered printer: {response.status} - {response_text}")
        except Exception as e:
            _LOGGER.error(f"Error registering printer: {e}")

    # Perform initial registration
    _LOGGER.error("Scheduling initial_registration task")
    hass.loop.create_task(initial_registration())

    # Schedule the periodic status update
    _LOGGER.error("Scheduling post_printer_status task")
    async_track_time_interval(hass, post_printer_status, timedelta(seconds=scan_interval))

    return True

async def async_setup_entry(hass, entry):
    """Set up Obico Connect from a config entry."""
    _LOGGER.error("Setting up Obico Connect")
    _LOGGER.error(f"Entry data: {entry.data}")

    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    auth_token = entry.data[CONF_AUTH_TOKEN]
    endpoint_prefix = entry.data[CONF_ENDPOINT_PREFIX]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 60)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "name": name,
        "auth_token": auth_token,
        "endpoint_prefix": endpoint_prefix,
        "scan_interval": scan_interval,
    }

    _LOGGER.error(f"Configuration loaded from entry: {hass.data[DOMAIN][entry.entry_id]}")

    async def post_printer_status(now):
        _LOGGER.error("post_printer_status called")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {auth_token}'}
                payload = {
                    # Add more detailed status information here
                    "status": "online",
                    "temperature": 200,  # Example temperature value
                    "job": {
                        "file": "example.gcode",
                        "progress": 50  # Example progress value
                    }
                }
                async with session.post(f"{endpoint_prefix}/api/v1/octo/printer_status/", headers=headers, json=payload) as response:
                    response_text = await response.text()
                    _LOGGER.error(f"Response status: {response.status}")
                    _LOGGER.error(f"Response text: {response_text}")
                    if response.status != 200:
                        _LOGGER.error(f"Failed to post printer status: {response.status} - {response_text}")
                    else:
                        _LOGGER.error(f"Successfully posted printer status: {response.status} - {response_text}")
        except Exception as e:
            _LOGGER.error(f"Error posting printer status: {e}")

    async def initial_registration():
        _LOGGER.error("initial_registration called")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {auth_token}'}
                payload = {
                    "name": name,
                    "status": "online"
                }
                async with session.post(f"{endpoint_prefix}/api/v1/octo/register/", headers=headers, json=payload) as response:
                    response_text = await response.text()
                    _LOGGER.error(f"Response status: {response.status}")
                    _LOGGER.error(f"Response text: {response_text}")
                    if response.status != 200:
                        _LOGGER.error(f"Failed to register printer: {response.status} - {response_text}")
                    else:
                        _LOGGER.error(f"Successfully registered printer: {response.status} - {response_text}")
        except Exception as e:
            _LOGGER.error(f"Error registering printer: {e}")

    # Perform initial registration
    _LOGGER.error("Scheduling initial_registration task")
    hass.loop.create_task(initial_registration())

    # Schedule the periodic status update
    _LOGGER.error("Scheduling post_printer_status task")
    async_track_time_interval(hass, post_printer_status, timedelta(seconds=scan_interval))

    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    _LOGGER.error("Unloading Obico Connect")
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True