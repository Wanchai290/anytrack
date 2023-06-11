# Communication protocol definition

## Packet structure

- 3 bytes : Packet start magic word
- 1 byte  : Protocol Version and PacketType concatenated together
    - 2 bits : Protocol version
    - 2 bits : PacketType
    - 2 bits : Number of channels in the frame
    - 2 bits : Padding
- 4 bytes : Frame number
- 2 bytes : Frame shape (same order as np.array().shape)
- 4 bytes : Payload length
- / bytes : Payload (length is never fixed, depends on output video frame)
- 2 bytes : Payload CRC
- 4 bytes : Packet end magic word

## Additional information
### Including the shape of the NumPy array representing the video frame

Using the NumPy array tobytes() method will flatten the array, so we need to reshape it when 
deserializing it.

Source : ![StackOverflow](https://stackoverflow.com/questions/47637758/how-can-i-make-a-numpy-ndarray-from-bytes)