#!/usr/bin/env python3

import subprocess
import sys

USAGE = """\
This command only checks for Paired or Connected devices.
  So you need to enter Paired or Connected after lsbt
  Example: lsbt Paired (all paired devices) or
           lsbt Connected (Devices currently connected)"""

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "paired":
        subprocess.run(["/usr/bin/bluetoothctl", "devices", "Paired"])
    elif action == "connected":
        subprocess.run(["/usr/bin/bluetoothctl", "devices", "Connected"])
    else:
        print(USAGE)
        sys.exit(1)

if __name__ == "__main__":
    main()
