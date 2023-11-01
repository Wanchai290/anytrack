#!/bin/bash
logfile="$0_log"

# Return to root folder to properly launch the test script
# This nifty code prevents user from launching the Python script improperly
# (because of modules, links etc...)
while pwd | grep -q src
do
  cd ..
done

# Launch the script
python3 -m src.comm_protocol.dummy_zmq_pub_sub.test_pub_sub "$@" 2> >(tee -a "$logfile" >&2)

if [ $? -ne 0 ]
then
  if grep -q "No module named 'src'" < "$logfile"
  then
    printf "\x1b[31m"  # ANSI color escape : color text red
    echo "ERROR : Script must be started inside the application's root folder (any sub-folder will do)" 1>&2
    printf "\x1b[0m"  # reset coloring
  fi
fi

rm "$logfile"