import zmq

from src.comm_protocol.Packet import Packet


class DummyZMQSub:

    def __init__(self, port: int):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._socket.connect(f"tcp://127.0.0.1:{port}")

    def recv_messages(self, n: int, result: dict, time_fmt: str):
        """
        Receive n number of messages and puts the received frames in `result`
        Params:
            n           -- Number of messages to read
            result      -- Dict to put the data in
            time_fmt    -- String format to print the time in
        """
        i = 0
        for _ in range(n):
            print(f"[SUB - " + eval(f"f'{time_fmt}'") + "] Waiting for message")
            data = self._socket.recv()
            print(f"[SUB - " + eval(f"f'{time_fmt}'") + "] Received one message")
            p = Packet.deserialize(data)
            if p is not None:
                result[i] = p
                i += 1
        self._context.destroy()
