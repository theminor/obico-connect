DOMAIN = "obico_connect" # Home Assistant component domain
DEFAULT_NAME = "Obico Connect" # Default name for the Home Assistant integration
CONF_AUTH_TOKEN = "auth_token"
CONF_ENDPOINT_PREFIX = "endpoint_prefix"
POST_STATUS_INTERVAL_SECONDS = 50
MAX_GCODE_DOWNLOAD_SECONDS = 30 * 60 # 30 minutes
POST_PIC_INTERVAL_SECONDS = 15.0 # How frquently to post a picture fromt eh webcam to the Obico server