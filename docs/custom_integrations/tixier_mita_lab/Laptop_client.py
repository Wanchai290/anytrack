import cv2
import zmq
import numpy as np

# Ask user for the Raspberry Pi's IP address
ip_address = input("Enter the IP address of the Raspberry Pi on interface eth0: ")

# ZeroMQ context and socket initialization
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages
socket.connect("tcp://{}:5555".format(ip_address))  # Connect to the Raspberry Pi's IP address


# Main function for receiving and displaying frames
def main():
    # Ask the width and height of the window
    width  = int(input('input the width of the stream window'))
    height = int(input('input the height of the stream window'))
    while True:
        frame = socket.recv()  # Receive the frame as bytes via ZeroMQ
        img_arr = np.frombuffer(frame, dtype=np.uint8)

        #Reshape the received Numpy array to the original image shape
        img_shape = (4032,3040,3) #camera resolution
        img = img_arr.reshape(img_shape)

        #Display the image using OpenCV
        cv2.imshow("Video Stream", img)
        cv2.resizeWindow("Video stream",width,height) #fix the window size
        cv2.waitKey(1)  # Adjust the delay as needed


if __name__ == '__main__':
    main()
