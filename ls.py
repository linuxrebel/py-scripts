#!/usr/bin/python

import sys
import os

def list_files_and_directories(path, show_hidden=False, verbose=False):
    entries = os.listdir(path)

    if not show_hidden:
        entries = [entry for entry in entries if not entry.startswith(".") or not os.path.basename(entry).startswith(".")]

    if verbose:
        print("Permissions Owner Group Size Date Time Name")
        for entry in entries:
            entry_path = os.path.join(path, entry)
            permissions = format(os.stat(entry_path).st_mode & 0o777, '03o')
            owner = os.stat(entry_path).st_uid
            group = os.stat(entry_path).st_gid
            size = os.stat(entry_path).st_size / 1024
            date_time = time.ctime(os.stat(entry_path).st_ctime)
            print(f"{permissions} {owner} {group} {size:.2f} {date_time} {entry}")
    else:
        for entry in entries:
            print(entry)

if __name__ == "__main__":
    path = os.path.expanduser("$HOME/JamesOne")
    if len(sys.argv) > 1:
        if sys.argv[1] == "-a":
            list_files_and_directories(path, show_hidden=True)
        elif sys.argv[1] == "-l":
            list_files_and_directories(path, verbose=True)
        else:
            print("Invalid arguments. Use -a to include hidden files/directories or -l for detailed info.")
    else:
        list_files_and_directories(path)

