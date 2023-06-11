# Communication protocol definition

## Packet structure

- 3 bytes : Packet start magic word
- 1 byte  : Protocol Version and PacketType concatenated together
    - 2 bits : Protocol version
    - 2 bits : PacketType
    - 4 bits : Padding
- 4 bytes : Frame number
- 4 bytes : Payload length
- / bytes : Payload (length is never fixed, depends on output video frame)
- 1 byte  : Payload CRC
- 4 bytes : Packet end magic word