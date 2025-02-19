import requests
import logging

_logger = logging.getLogger('homeassistant.components.obico')

def server_request(method, uri, plugin, timeout=30, raise_exception=False, skip_debug_logging=False, **kwargs):
    url = plugin.canonical_endpoint_prefix() + uri
    headers = plugin.auth_headers()
    try:
        resp = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        _logger.error(f"Request to {url} failed: {e}")
        if raise_exception:
            raise
        return None