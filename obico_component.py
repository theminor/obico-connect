import logging
import json
import requests
import websocket
import threading
import time
import bson  # Import bson for binary serialization
import inspect  # Import inspect for inspecting function arguments
import asyncio  # Import asyncio for non-blocking sleep
from .const import POST_STATUS_INTERVAL_SECONDS  # Import the constant
from .jpeg_poster import JpegPoster  # Import JpegPoster

_LOGGER = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, url, token=None, on_ws_msg=None, on_ws_close=None, on_ws_open=None, subprotocols=None, waitsecs=120):
        self._mutex = threading.RLock()

        def on_error(ws, error):
            _LOGGER.warning('Server WS ERROR: {}'.format(error))
            threading.Thread(target=self.close).start()

        def on_message(ws, msg):
            if on_ws_msg:
                on_ws_msg(ws, msg)

        def on_close(ws, close_status_code, close_msg):
            _LOGGER.warning('WS Closed - {} - {}'.format(close_status_code, close_msg))
            if on_ws_close:
                on_ws_close(ws, close_status_code=close_status_code)

        def on_open(ws):
            _LOGGER.debug('WS Opened')
            threading.Thread(target=on_ws_open, args=(ws,)).start() if on_ws_open else None

        _LOGGER.debug('Connecting to websocket: {}'.format(url))
        header = ["authorization: bearer " + token] if token else None
        self.ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            header=header,
            subprotocols=subprotocols
        )

        run_forever_kwargs = {'reconnect': 0} if 'reconnect' in inspect.getfullargspec(websocket.WebSocketApp.run_forever).args else {}
        wst = threading.Thread(target=self.ws.run_forever, kwargs=run_forever_kwargs)
        wst.daemon = True
        wst.start()

        asyncio.create_task(self.wait_for_connection(waitsecs))

    async def wait_for_connection(self, waitsecs):
        for i in range(waitsecs * 10):
            if self.connected():
                return
            await asyncio.sleep(0.1)
        self.ws.close()
        raise WebSocketConnectionException('Not connected to websocket server after {}s'.format(waitsecs))

    def send(self, data, as_binary=False):
        with self._mutex:
            if self.connected():
                if as_binary:
                    self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
                else:
                    self.ws.send(data)
            else:
                _LOGGER.warning("Attempted to send data, but WebSocket is not connected.")

    def connected(self):
        return self.ws.sock and self.ws.sock.connected

    def close(self):
        self.ws.close()

class WebSocketConnectionException(Exception):
    pass

class ObicoComponent:
    def __init__(self, hass, config_entry):
        self.hass = hass
        self.auth_token = config_entry.data["auth_token"]
        self.endpoint_prefix = config_entry.data["endpoint_prefix"]
        self.camera_entity_id = config_entry.data["camera_entity_id"]
        self.ws_client = None
        self.jpeg_poster = JpegPoster(hass, self.camera_entity_id, self)
        self.config_entry = config_entry
        self.schedule_periodic_status_update()

    def is_configured(self):
        return self.auth_token is not None and self.endpoint_prefix is not None

    def setup(self):
        _LOGGER.debug("Setting up ObicoComponent")
        if self.is_configured():
            self.establish_ws_connection()
            self.schedule_periodic_status_update()
            asyncio.create_task(self.jpeg_poster.pic_post_loop())

    def establish_ws_connection(self):
        ws_url = f"{self.endpoint_prefix.replace('http', 'ws')}/ws/dev/"
        _LOGGER.debug(f"Establishing WebSocket connection to {ws_url}")
        self.ws_client = WebSocketClient(
            url=ws_url,
            token=self.auth_token,
            on_ws_msg=self.process_server_msg,
            on_ws_close=self.on_server_ws_close,
            on_ws_open=self.on_server_ws_open,
        )

    def process_server_msg(self, ws, raw_data):
        msg = json.loads(raw_data)
        _LOGGER.debug("Received from server: \n{}".format(msg))
        # Process the message as needed

    def on_server_ws_close(self, ws, close_status_code):
        _LOGGER.warning('Server WS Closed - {}'.format(close_status_code))
        self.ws_client = None

    def on_server_ws_open(self, ws):
        _LOGGER.debug('Server WS Opened')
        self.post_update_to_server()

    def post_update_to_server(self, data=None):
        if not data:
            data = self.status()
        self.send_ws_msg_to_server(data)

    def send_ws_msg_to_server(self, data, as_binary=False):
        if not self.ws_client or not self.ws_client.connected():
            self.establish_ws_connection()
        if as_binary:
            raw = bson.dumps(data)
            _LOGGER.debug("Sending binary ({} bytes) to server".format(len(raw)))
        else:
            _LOGGER.debug("Sending to server: \n{}".format(data))
            raw = json.dumps(data, default=str)
        self.ws_client.send(raw, as_binary=as_binary)

    def status(self):
        # *** Replace this with actual data ***
        return {
            "current_print_ts": -1,  # int(time.time()),
            "event": {
                "event_type": "ENDED",
                    # STARTED: Print job started.
                    # ENDED: Print job ended.
                    # PAUSED: Print job paused.
                    # RESUMED: Print job resumed.
                    # FAILURE_ALERTED: Possible failure detected.
                    # ALERT_MUTED: Alerts have been muted.
                    # ALERT_UNMUTED: Alerts have been unmuted.
                    # FILAMENT_CHANGE: Filament change required.
                    # PRINTER_ERROR: Printer error occurred.
            },
            "settings": {
                "webcams": [
                    {
                        "name": "Dummy Camera",
                        "is_primary_camera": True,
                        "stream_mode": "live",
                        "stream_id": 1,
                        "flipV": False,
                        "flipH": False,
                        "rotation": 0,
                        "streamRatio": "16:9"
                    }
                ],
                "temperature": {
                    "profiles": [
                        {"bed": 60, "chamber": None, "extruder": 200, "name": "PLA"},
                        {"bed": 100, "chamber": None, "extruder": 240, "name": "ABS"}
                    ]
                },
                "agent": {
                    "name": "octoprint_obico",
                    "version": "2.5.2"
                }
            },
            "status": {
                "_ts": int(time.time()),
                "state": {
                    "text": "Operational", # or "Offline"... etc
                    "flags": {
                        "operational": True,
                        "printing": False, # true if the printer is currently printing, false otherwise
                        "cancelling": False, # true if the printer is currently printing and in the process of pausing, false otherwise
                        "pausing": False, # true if the printer is currently printing and in the process of pausing, false otherwise
                        "resuming": False,
                        "finishing": False,
                        "closedOrError": False, # true if the printer is disconnected (possibly due to an error), false otherwise
                        "error": False, # true if an unrecoverable error occurred, false otherwise
                        "paused": False, # true if the printer is currently paused, false otherwise
                        "ready": True, # true if the printer is operational and no data is currently being streamed to SD, so ready to receive instructions
                        "sdReady": True # true if the printer’s SD card is available and initialized, false otherwise. This is redundant information to the SD State.
                    },
                    "error": ""
                },
                "job": {
                    "file": {
                        "name": "example.gcode",
                        "path": "/path/to/example.gcode",
                        "display": "Example GCode",
                        "origin": "local",
                        "size": 123456,
                        "date": "2025-01-01T23:00:10.000000Z"
                    },
                    "estimatedPrintTime": 3600,
                    "averagePrintTime": 3500,
                    "lastPrintTime": 3400,
                    "filament": {
                        "tool0": {
                            "length": 1000,
                            "volume": 10
                        }
                    },
                    "user": "User Name",
                },
                "currentLayerHeight": 0.2,
                "currentZ": 5.0,
                "currentFeedRate": 100,
                "currentFlowRate": 100,
                "currentFanSpeed": 100,
                "progress": {
                    "completion": 50,
                    "filepos": 123456,
                    "printTime": 1800,
                    "printTimeLeft": 1800,
                    "printTimeLeftOrigin": "estimate"
                },
                "temperatures": {
                    "tool0": {
                        "actual": 200,
                        "target": 200,
                        "offset": 0
                    },
                    "bed": {
                        "actual": 60,
                        "target": 60,
                        "offset": 0
                    },
                    "chamber": {
                        "actual": None,
                        "target": None,
                        "offset": 0
                    }
                },
                "file_metadata": {
                    "hash": "abc123",
                    "obico": {
                        "totalLayerCount": 100
                    },
                    "analysis": {
                        "printingArea": {
                            "maxX": 200,
                            "maxY": 200,
                            "maxZ": 200,
                            "minX": 0,
                            "minY": 0,
                            "minZ": 0
                        },
                        "dimensions": {
                            "depth": 200,
                            "height": 200,
                            "width": 200
                        },
                        "travelArea": {
                            "maxX": 200,
                            "maxY": 200,
                            "maxZ": 200,
                            "minX": 0,
                            "minY": 0,
                            "minZ": 0
                        },
                        "travelDimensions": {
                            "depth": 200,
                            "height": 200,
                            "width": 200
                        },
                        "estimatedPrintTime": 3600,
                        "filament": {
                            "tool0": {
                                "length": 1000,
                                "volume": 10
                            }
                        }
                    },
                    "history": {
                        "timestamp": "2025-02-22T23:05:10.652919Z",
                        "printTime": 3600,
                        "success": True,
                        "printerProfile": "default"
                    },
                    "statistics": {
                        "averagePrintTime": 3500,
                        "lastPrintTime": 3400
                    }
                }
            }
        }

    def schedule_periodic_status_update(self):
        async def periodic_status_update():
            while True:
                await asyncio.sleep(POST_STATUS_INTERVAL_SECONDS)
                self.post_update_to_server()

        asyncio.create_task(periodic_status_update())