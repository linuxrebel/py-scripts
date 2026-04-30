#!/usr/bin/python

import os
import sys
import time
import stat

def list_files_and_directories(path, show_hidden=False, verbose=False):
    entries = os.listdir(path)

    if not show_hidden:
        entries = [entry for entry in entries if not entry.startswith(".") or not os.path.basename(entry).startswith(".")]

    if verbose:
        total_size = 0
        for entry in entries:
            entry_path = os.path.join(path, entry)
            total_size += os.stat(entry_path).st_size

        print(f"total {total_size}")

        for entry in entries:
            entry_path = os.path.join(path, entry)
            st = os.stat(entry_path)
            mode = st.st_mode
            rwx = get_rwx(mode)
            owner = st.st_uid
            group = st.st_gid
            size = st.st_size
            date_time = time.ctime(st.st_ctime)
            print(f"{rwx} {owner} {group} {size} {date_time} {entry}")
    else:
        for entry in entries:
            print(entry)

def get_rwx(mode):
    r = (mode & 0o400) >> 2
    w = (mode & 0o200) >> 1
    x = mode & 0o100
    g = (mode & 0o040) >> 1
    o = mode & 0o004

    return f"{'r' if r else '-'}{'w' if w else '-'}{'x' if x else '-'}{'r' if g else '-'}{'w' if o else '-'}"

if __name__ == "__main__":
    path = os.getcwd()
    if len(sys.argv) > 1:
        if sys.argv[1] == "-a":
            list_files_and_directories(path, show_hidden=True)
        elif sys.argv[1] == "-l":
            list_files_and_directories(path, verbose=True)
        else:
            print("Invalid arguments. Use -a to include hidden files/directories or -l for detailed info.")
    else:
        list_files_and_directories(path)

