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
        timed_out = round(time.time() - start_time) >= max_timeout_s
        finished_reading = False

        # accessing an item at a certain index of a bytes object does not give you the representation
        # of the data accessed. Instead, it gives the int value of the read byte
        # so Packet.END_MAGIC_WORD[0] returns 110, and not b"n"
        while not finished_reading and not timed_out:
            data += received
            received = request.recv(16)
            timed_out = round(time.time() - start_time) >= max_timeout_s
            if Packet.END_MAGIC_WORD in received:
                idx_end_word_start = received.index(Packet.END_MAGIC_WORD[0])
                idx_end_word_end = idx_end_word_start + Packet.LEN_END_MAGIC_WORD
                if received[idx_end_word_start : idx_end_word_end] == Packet.END_MAGIC_WORD:
                    finished_reading = True

        # the end word gets skipped, we add it back here
        data += received
        return data if not timed_out else None
