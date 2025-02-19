import logging
import json
import requests
import websocket
import threading
import time
import bson  # Import bson for binary serialization
import inspect  # Import inspect for inspecting function arguments
import asyncio  # Import asyncio for non-blocking sleep

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
        self.auth_token = config_entry["auth_token"]
        self.endpoint_prefix = config_entry["endpoint_prefix"]
        self.ws_client = None

    def setup(self):
        _LOGGER.debug("Setting up ObicoComponent")
        if self.auth_token and self.endpoint_prefix:
            self.establish_ws_connection()

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
        # Implement your status retrieval logic here
        return {"status": "ok"}