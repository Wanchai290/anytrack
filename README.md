# Tixier-Mita laboratory - Anytrack

## Authors (of software and summary)
- Thomas Wanchaï MENIER (2023)

## Developed thanks to
- Agnès TIXIER-MITA, Associate professor at the IIS
- Gilgueng Hwang, researcher at the IIS
- Hiroshi TOSHIYOSHI, head researcher of the Toshiyoshi laboratory, IIS
- Alex DUFOUR, French colleague, 3rd year engineering student at ENSEIRB-MATMECA, Bordeaux
- Gabriel Faure, French colleague, engineering student at the University of Tokyo
- Universitary Institute of Technology (IUT) of Bordeaux-Gradignan, France
- Institute of Industrial Science (IIS), The University of Tokyo, Tokyo

## Guides
- [User Manual](./docs/USER_MANUAL.md)
- [Installation](./INSTALL.md)
- [Development Guide](./docs/DEV_MANUAL.md)

## Context
### About the project

Upon request of Agnès TIXIER-MITA, associate professor at the Institute of Industrial Science, this software
was created to allow for tracking operations on cardyomyocyte cells. The software allows to perform distance analysis
between two tracked points, on videos and/or in real-time.

It has been designed with the idea of flexibility, adding new trackers to the software does not require to have a deep knowledge 
of the whole architecture, but only of a few files.

The motivation for the project is because I had to perform a 2-month internship in the Tixier-Mita laboratory, this problem was given
to me and this was the solution that has been developed.

### Features
- Tracking with currently 2 types of tracker implemented 
    - Normalize Cross Correlation (template matching)
    - KCF Tracker (implementation of OpenCV)
- Live tracking from a video feed
- Client/Server architecture available for remote or linked integration with a microscope
(more details ![below](#client-server-protocol))

### Why not use ImageJ or integrate other open-source software ?
I was a 2nd year Computer Science student at the time, and I had only heard about those software. The problem is that I had the choice of
either trying to delve in an open-source software and trying to extend it, or develop something from scratch.

Given the limited time frame I had, and knowing that I had never performed the former, I went with the more second approach
to ensure a result could be produced at the end. This way, I was sure my university would consider my work as valid, I wasn't very
sure if integration would get me a good enough grade as well.

## <p id=client-server-protocol>Client Server protocol</p>
The main idea of Agnès-sensei, my mentor, was to retrieve the live video feed of a microscope to perform real-time analyses
on an external software. Learning that it was not possible to retrieve the feed of the existing microscopes at the laboratory,
the task has been changed to allow the software to communicate with a RaspberryPI containing a camera. This system would imitate
a microscope, and because the RaspberryPI is open-source, it was possible to realize the communication between my software and
the custom microscope.

To perform this, a Client/Server architecture has been developed that also implements a custom 
Application Layer communication protocol. Consider that the RaspberryPI acts as a server, which sends video
frames to the live tracking software, namely the client. More information about the communication protocol definition ![here](src/comm_protocol/comm_protocol_definition.md)

Any developer can implement the protocol to send frames over the TCP protocol. A guide to implement this
will be written in the future.
