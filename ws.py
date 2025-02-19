# octoprint_obico/ws.py
import websocket
import threading
import logging

_logger = logging.getLogger('homeassistant.components.obico')

class WebSocketConnectionException(Exception):
    pass

class WebSocketClient:
    def __init__(self, url, token=None, on_ws_msg=None, on_ws_close=None, on_ws_open=None, subprotocols=None, waitsecs=120):
        self._mutex = threading.RLock()

        def on_error(ws, error):
            _logger.warning('Server WS ERROR: {}'.format(error))
            threading.Thread(target=self.close).start()

        def on_message(ws, msg):
            if on_ws_msg:
                on_ws_msg(ws, msg)

        def on_close(ws, close_status_code, close_msg):
            _logger.warning('WS Closed - {} - {}'.format(close_status_code, close_msg))
            if on_ws_close:
                on_ws_close(ws, close_status_code=close_status_code)

        def on_open(ws):
            _logger.debug('WS Opened')
            threading.Thread(target=on_ws_open, args=(ws,)).start() if on_ws_open else None

        _logger.debug('Connecting to websocket: {}'.format(url))
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

        for i in range(waitsecs * 10):
            if self.connected():
                return
            time.sleep(0.1)
        self.ws.close()
        raise WebSocketConnectionException('Not connected to websocket server after {}s'.format(waitsecs))

    def send(self, data, as_binary=False):
        with self._mutex:
            if as_binary:
                self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
            else:
                self.ws.send(data)

    def connected(self):
        return self.ws.sock and self.ws.sock.connected

    def close(self):
        self.ws.close()