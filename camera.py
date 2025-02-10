import logging
from homeassistant.components.camera import Camera
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ObicoConnectCamera(hass.data[DOMAIN])], True)

class ObicoConnectCamera(Camera):
    def __init__(self, config):
        super().__init__()
        self._name = config["name"]

    @property
    def name(self):
        return self._name

    async def async_camera_image(self):
        return b""