import zmq

from src.comm_protocol.Packet import Packet


class DummyZMQSub:

    def __init__(self, port: int):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._socket.connect(f"tcp://127.0.0.1:{port}")

    def recv_messages(self, n: int, result: dict):
        i = 0
        for _ in range(n):
            print("[SUB] Waiting for message")
            data = self._socket.recv()
            p = Packet.deserialize(data)
            if p is not None:
                result[i] = p
                i += 1
        self._context.destroy()
