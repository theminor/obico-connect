import logging
import threading
import time
import aiohttp
import backoff
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .utils import server_request
from .lib.error_stats import error_stats

POST_PIC_INTERVAL_SECONDS = 10.0

_logger = logging.getLogger(__name__)

class JpegPoster:

    def __init__(self, hass, camera_entity_id, plugin):
        self.hass = hass
        self.camera_entity_id = camera_entity_id
        self.plugin = plugin
        self.last_jpg_post_ts = 0

    async def capture_jpeg(self):
        camera = self.hass.states.get(self.camera_entity_id)
        if camera is None:
            raise Exception(f"Camera entity {self.camera_entity_id} not found")

        url = camera.attributes.get("entity_picture")
        if url is None:
            raise Exception(f"Camera entity {self.camera_entity_id} does not have an entity_picture attribute")

        # Prepend the base URL of your Home Assistant instance
        base_url = self.hass.config.external_url or self.hass.config.internal_url
        if not base_url:
            raise Exception("Base URL for Home Assistant is not set")
        full_url = f"{base_url}{url}"

        _logger.debug(f"Capturing JPEG from URL: {full_url}")

        session = async_get_clientsession(self.hass)
        async with session.get(full_url) as response:
            _logger.debug(f"Response status: {response.status}")
            if response.status != 200:
                _logger.error(f"Failed to capture jpeg - HTTP status code: {response.status}")
                raise Exception(f"Failed to capture jpeg - HTTP status code: {response.status}")
            response.raise_for_status()
            return await response.read()

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    @backoff.on_predicate(backoff.expo, max_tries=3)
    async def post_pic_to_server(self):
        try:
            error_stats.attempt('webcam')
            jpeg_data = await self.capture_jpeg()
            data = aiohttp.FormData()
            data.add_field('pic', jpeg_data, filename='image.jpg', content_type='image/jpeg')
            data.add_field('viewing_boost', 'true')  # or remove this line?
        except Exception as e:
            error_stats.add_connection_error('webcam', self.plugin)
            _logger.error(f'Failed to capture jpeg - {e}')
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.plugin.endpoint_prefix}/api/v1/octo/pic/",
                    data=data,
                    headers=self.plugin.auth_headers(),
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    _logger.warning(f'Jpeg posted to server - {resp.status}')
                    resp.raise_for_status()
        except Exception as e:
            _logger.error(f'Failed to post jpeg to server - {e}')

    async def pic_post_loop(self):
        while True:
            try:
                interval_seconds = POST_PIC_INTERVAL_SECONDS
                if self.last_jpg_post_ts > time.time() - interval_seconds:
                    continue

                self.last_jpg_post_ts = time.time()
                await self.post_pic_to_server()
            except Exception as e:
                _logger.error(f"Error in pic_post_loop: {e}")