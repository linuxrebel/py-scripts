#!/usr/bin/env python3

import subprocess
import sys
import os

HELP = """\
This command only checks for Paired or Connected devices.
  So you need to enter Paired or Connected after lsbt
  Example: lsbt Paired (or p) — all paired devices
           lsbt Connected (or c) — devices currently connected"""

def main():
    # Check if an argument was provided
    if len(sys.argv) < 2:
        print("Usage: lsbt <paired|p|connected|c>  (use -h for help)")
        sys.exit(1)

    # Get the device type from the command line argument
    sysArg = sys.argv[1].lower()

    # Display help message if -h or --help is provided
    if sysArg in ("-h", "--help"):
        print(HELP)
        sys.exit(0)

    # Check if the provided argument is valid
    if sysArg in ("paired", "p"):
        command = ["bluetoothctl", "devices", "Paired"]
    elif sysArg in ("connected", "c"):
        command = ["bluetoothctl", "devices", "Connected"]
    else:
        print(f"Unknown argument '{sysArg}'. Use -h for help.")
        sys.exit(1)

    # Execute the bluetoothctl command and handle errors
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running bluetoothctl: {e}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
