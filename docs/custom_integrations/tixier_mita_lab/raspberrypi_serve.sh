#!/bin/bash
while pwd | grep -q docs
do
  cd ..
done

python3 -m docs.custom_integrations.tixier_mita_lab.custom_raspberrypi_headless_zmq.py