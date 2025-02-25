import aiohttp
import logging

_logger = logging.getLogger('homeassistant.components.obico')

async def server_request(method, uri, plugin, timeout=30, raise_exception=False, skip_debug_logging=False, **kwargs):
    url = plugin.endpoint_prefix + uri
    headers = plugin.auth_headers()
    # Merge headers if provided in kwargs
    if 'headers' in kwargs:
        headers.update(kwargs.pop('headers'))
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, timeout=timeout, **kwargs) as resp:
                resp.raise_for_status()
                return await resp.json()
    except aiohttp.ClientError as e:
        _logger.error(f"Request to {url} failed: {e}")
        if raise_exception:
            raise
        return None