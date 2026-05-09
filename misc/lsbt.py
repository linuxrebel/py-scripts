#!/usr/bin/env python3

import subprocess
import sys

HELP = """\
This command only checks for Paired or Connected devices.
  So you need to enter Paired or Connected after lsbt
  Example: lsbt Paired (or p) — all paired devices
           lsbt Connected (or c) — devices currently connected"""

def main():
    if len(sys.argv) < 2:
        print("Usage: lsbt <paired|p|connected|c>  (use -h for help)")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action in ("-h", "--help"):
        print(HELP)
        sys.exit(0)
    elif action in ("paired", "p"):
        subprocess.run(["/usr/bin/bluetoothctl", "devices", "Paired"])
    elif action in ("connected", "c"):
        subprocess.run(["/usr/bin/bluetoothctl", "devices", "Connected"])
    else:
        print(f"Unknown argument '{sys.argv[1]}'. Use -h for help.")
        sys.exit(1)

if __name__ == "__main__":
    main()
