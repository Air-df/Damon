import json
from ws4py.client.threadedclient import WebSocketClient


class DummyClient(WebSocketClient):
    def opened(self):
        print('opened')

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, m):
        print(m)


if __name__ == '__main__':
    ws = DummyClient('ws://127.0.0.1:8888/socket', protocols=['chat'])
    ws.connect()
    ws.send(json.dumps({'reciever': 'test', 'msg': '搞笑呢'}))
    ws.close()

