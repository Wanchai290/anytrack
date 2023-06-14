# Communication protocol definition

## Packet structure

- 3 bytes : Packet start magic word
- 1 byte  : Protocol Version and PacketType concatenated together
    - 2 bits : Protocol version
    - 2 bits : PacketType
    - 2 bits : Number of channels in the frame
    - 2 bits : dtype of the NumPy array representing the video frame
- 4 bytes : Frame number
- 4 bytes : Frame shape (same order as np.array().shape)
- 4 bytes : Payload length
- / bytes : Payload (length is never fixed, depends on output video frame)
- 2 bytes : Payload CRC
- 4 bytes : Packet end magic word

## Communication structure
### Initializing the connection

The server should be started on its own and serve forever.  
To start, the client must send a packet with the PacketType set to OK (whatever the content).  
This will start the server to send frames, the packets sent by the server are of type PacketType.FRAME. If the client receives the frames correctly, it can send
a new empty packet with PacketType set to OK to receive another frame.  
If the frame were to be corrupted, the client can send an empty packet with PacketType set to REQUEST 
to acquire again the frame.

It is the client's role to sever to connection, by sending an empty packet with type HALT. Right after,
the client can close the socket, and the server will do the same.

## Additional information
### Including the shape of the NumPy array representing the video frame

Using the NumPy array tobytes() method will flatten the array, so we need to reshape it when 
deserializing it.

Source : ![StackOverflow](https://stackoverflow.com/questions/47637758/how-can-i-make-a-numpy-ndarray-from-bytes)