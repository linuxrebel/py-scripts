#!/bin/bash

action="$1"

if [ "$action" == "Paired" ] || [ "$action" == "paired" ]; then
  /usr/bin/bluetoothctl devices Paired
elif [ "$action" == "Connected" ] || [ "$action" == "connected" ]; then
  /usr/bin/bluetoothctl devices Connected
else
   echo "This command only checks for Paired or Connected devices."
   echo "  So you need to enter Paired or Connected after lsbt"
   echo "  Example: lsbt Paired (all paired devices) or "
   echo "           lsbt Connected (Devices currently connected)" 
fi
