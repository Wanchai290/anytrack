import time

from comm_protocol.Packet import Packet


class PacketHandler:
    """
    Defines methods for handling the continuous reading of bytes
    and for handling
    """

    @staticmethod
    def read_start_word(request) -> bytes | None:
        word = request.recv(Packet.LEN_START_MAGIC_WORD)
        if word == Packet.START_MAGIC_WORD:
            return word

    @staticmethod
    def read_until_end_word(request, start_time: float, max_timeout_s: int) -> bytes | None:
        data = b""
        # since we already read the start word, we subtract its size to what we have to read
        received = request.recv(Packet.PAYLOAD_LEN_IDX - Packet.LEN_START_MAGIC_WORD)

        # raw reading payload length for faster reading in tcp connection
        received += request.recv(Packet.LEN_PAYLOAD_LENGTH)
        payload_length = int.from_bytes(received[:Packet.LEN_PAYLOAD_LENGTH], byteorder=Packet.BYTE_ORDER)
        received += request.recv(payload_length)

        data += received

        timed_out = round(time.time() - start_time) >= max_timeout_s
        finished_reading = PacketHandler.check_end(received)

        # accessing an item at a certain index of a bytes object does not give you the representation
        # of the data accessed. Instead, it gives the int value of the read byte
        # so Packet.END_MAGIC_WORD[0] returns 110, and not b"n"
        while not finished_reading and not timed_out:
            received = request.recv(1024**2)  # recv is blocking if we already emptied the buffer in previous reads
            timed_out = round(time.time() - start_time) >= max_timeout_s
            finished_reading = PacketHandler.check_end(received)
            data += received

        # the end word gets skipped, we add it back here
        data += received
        return data if not timed_out else None

    @staticmethod
    def check_end(data: bytes) -> bool:
        if Packet.END_MAGIC_WORD in data:
            idx_end_word_start = data.index(Packet.END_MAGIC_WORD[0])
            idx_end_word_end = idx_end_word_start + Packet.LEN_END_MAGIC_WORD
            if data[idx_end_word_start: idx_end_word_end] == Packet.END_MAGIC_WORD:
                return True
        return False
