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
        self.printer_device_id = config_entry.data["printer_device_id"]
        self.device_type = config_entry.data["device_type"]
        self.ws_client = None
        self.jpeg_poster = JpegPoster(hass, self.camera_entity_id, self)
        self.config_entry = config_entry
        self.schedule_periodic_status_update()

    def auth_headers(self):
        return {
            "Authorization": f"Token {self.auth_token}"
        }

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

    async def fetch_moonraker_data(self):
        # Fetch data from Moonraker component
        data = {}
        try:
            data["nozzle_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_extruder_temperature").state
            data["bed_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_bed_temperature").state
            data["print_progress"] = self.hass.states.get(f"sensor.{self.printer_device_id}_progress").state
            data["print_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_duration").state
            data["print_time_left"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_eta").state
            data["current_layer"] = self.hass.states.get(f"sensor.{self.printer_device_id}_current_layer").state
            data["total_layers"] = self.hass.states.get(f"sensor.{self.printer_device_id}_total_layer").state
            data["bed_target_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_bed_target").state
            data["cooling_fan_speed"] = self.hass.states.get(f"sensor.{self.printer_device_id}_fan_speed").state
            data["current_stage"] = self.hass.states.get(f"sensor.{self.printer_device_id}_current_print_state").state
            data["gcode_filename"] = self.hass.states.get(f"sensor.{self.printer_device_id}_filename").state
            data["print_status"] = self.hass.states.get(f"sensor.{self.printer_device_id}_printer_state").state
            data["remaining_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_eta").state
            data["start_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_duration").state
        except Exception as e:
            _LOGGER.warning(f"Error fetching Moonraker data: {e}")
        return data

    async def fetch_bambu_lab_data(self):
        # Fetch data from Bambu Lab component
        data = {}
        try:
            data["nozzle_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_nozzle_temperature").state
            data["bed_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_bed_temperature").state
            data["print_progress"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_progress").state
            data["print_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_time").state
            data["print_time_left"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_time_left").state
            data["current_layer"] = self.hass.states.get(f"sensor.{self.printer_device_id}_current_layer").state
            data["total_layers"] = self.hass.states.get(f"sensor.{self.printer_device_id}_total_layers").state
            data["active_tray"] = self.hass.states.get(f"sensor.{self.printer_device_id}_active_tray").state
            data["bed_target_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_bed_target_temperature").state
            data["cooling_fan_speed"] = self.hass.states.get(f"sensor.{self.printer_device_id}_cooling_fan_speed").state
            data["current_stage"] = self.hass.states.get(f"sensor.{self.printer_device_id}_current_stage").state
            data["end_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_end_time").state
            data["gcode_filename"] = self.hass.states.get(f"sensor.{self.printer_device_id}_gcode_filename").state
            data["heatbreak_fan_speed"] = self.hass.states.get(f"sensor.{self.printer_device_id}_heatbreak_fan_speed").state
            data["nozzle_size"] = self.hass.states.get(f"sensor.{self.printer_device_id}_nozzle_size").state
            data["nozzle_target_temperature"] = self.hass.states.get(f"sensor.{self.printer_device_id}_nozzle_target_temperature").state
            data["print_status"] = self.hass.states.get(f"sensor.{self.printer_device_id}_print_status").state
            data["remaining_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_remaining_time").state
            data["start_time"] = self.hass.states.get(f"sensor.{self.printer_device_id}_start_time").state
            data["ip_address"] = self.hass.states.get(f"sensor.{self.printer_device_id}_ip_address").state
        except Exception as e:
            _LOGGER.warning(f"Error fetching Bambu Lab data: {e}")
        return data

    async def status(self):
        if self.device_type == "moonraker":
            data = await self.fetch_moonraker_data()
        elif self.device_type == "bambu_lab":
            data = await self.fetch_bambu_lab_data()
        else:
            data = {}

        return {
            "current_print_ts": int(time.time()),  # int(time.time()),
            "event": {
                "event_type": "STARTED" if data.get("print_progress") and float(data["print_progress"]) > 0 else "ENDED",
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
                    "text": "Operational" if data.get("print_progress") and float(data["print_progress"]) > 0 else "Offline",  # or "Offline"... etc
                    "flags": {
                        "operational": True,
                        "printing": float(data.get("print_progress", 0)) > 0,  # true if the printer is currently printing, false otherwise
                        "cancelling": False,  # true if the printer is currently printing and in the process of pausing, false otherwise
                        "pausing": False,  # true if the printer is currently printing and in the process of pausing, false otherwise
                        "resuming": False,
                        "finishing": False,
                        "closedOrError": False,  # true if the printer is disconnected (possibly due to an error), false otherwise
                        "error": False,  # true if an unrecoverable error occurred, false otherwise
                        "paused": False,  # true if the printer is currently paused, false otherwise
                        "ready": True,  # true if the printer is operational and no data is currently being streamed to SD, so ready to receive instructions
                        "sdReady": True  # true if the printer’s SD card is available and initialized, false otherwise. This is redundant information to the SD State.
                    },
                    "error": data.get("print_status", "")
                },
                "job": {
                    "file": {
                        "name": data.get("gcode_filename", "example.gcode"),
                        "path": "/path/to/example.gcode",
                        "display": data.get("gcode_filename", "Example GCode"),
                        "origin": "local",
                        "size": 123456,
                        "date": data.get("start_time", "2025-01-01T23:00:10.000000Z")
                    },
                    "estimatedPrintTime": int(data.get("print_time_left", 0)) + int(data.get("print_time", 0)),
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
                "currentFanSpeed": float(data.get("cooling_fan_speed", 100)),
                "progress": {
                    "completion": float(data.get("print_progress", 0)),
                    "filepos": 123456,
                    "printTime": int(data.get("print_time", 0)),
                    "printTimeLeft": int(data.get("print_time_left", 0)),
                    "printTimeLeftOrigin": "estimate"
                },
                "temperatures": {
                    "tool0": {
                        "actual": float(data.get("nozzle_temperature", 0)),
                        "target": float(data.get("nozzle_target_temperature", 200)),
                        "offset": 0
                    },
                    "bed": {
                        "actual": float(data.get("bed_temperature", 0)),
                        "target": float(data.get("bed_target_temperature", 60)),
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
                        "totalLayerCount": int(data.get("total_layers", 0))
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
                        "timestamp": data.get("start_time", "2025-02-22T23:05:10.652919Z"),
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