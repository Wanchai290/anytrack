#!/bin/bash
while !(pwd | ls . | grep -q src)
do
  cd ..
done

python3 -m custom_integrations.tixier_mita_lab.custom_raspberrypi_headless_zmq
