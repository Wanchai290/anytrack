#!/bin/bash
while pwd | grep -q src
do
  cd ..
done

python3 -m src.custom_integrations.tixier_mita_lab.custom_raspberrypi_headless_zmq