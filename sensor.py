import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ObicoConnectSensor(hass.data[DOMAIN])], True)

class ObicoConnectSensor(Entity):
    def __init__(self, config):
        self._name = config["name"]
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        self._state = "obico_connect_sensor_state"