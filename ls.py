#!/usr/bin/python

import os
import sys
import time
import stat
import pwd
import grp

def list_files_and_directories(path, show_hidden=False, verbose=False, columns=4):
    entries = os.listdir(path)

    if not show_hidden:
        entries = [entry for entry in entries if not os.path.basename(entry).startswith(".")]

    if verbose:
        # Compute block count (ls uses 512-byte blocks internally, displays in 1K blocks)
        total_blocks = 0
        for entry in entries:
            entry_path = os.path.join(path, entry)
            total_blocks += os.lstat(entry_path).st_blocks
        print(f"total {total_blocks // 2}")

        rows = []
        for entry in entries:
            entry_path = os.path.join(path, entry)
            st = os.lstat(entry_path)
            mode_str = get_rwx(st.st_mode)
            nlink = st.st_nlink
            try:
                owner = pwd.getpwuid(st.st_uid).pw_name
            except KeyError:
                owner = str(st.st_uid)
            try:
                group = grp.getgrgid(st.st_gid).gr_name
            except KeyError:
                group = str(st.st_gid)
            size = st.st_size
            # Match ls date format: "Mon DD HH:MM" (no year if current year)
            mtime = st.st_mtime
            t = time.localtime(mtime)
            current_year = time.localtime().tm_year
            if t.tm_year == current_year:
                date_str = time.strftime("%b %e %H:%M", t)
            else:
                date_str = time.strftime("%b %e  %Y", t)
            rows.append((mode_str, nlink, owner, group, size, date_str, entry))

        # Align columns like ls -l
        max_nlink = max(len(str(r[1])) for r in rows)
        max_owner = max(len(str(r[2])) for r in rows)
        max_group = max(len(str(r[3])) for r in rows)
        max_size  = max(len(str(r[4])) for r in rows)

        for mode_str, nlink, owner, group, size, date_str, entry in rows:
            print(f"{mode_str} {nlink:{max_nlink}} {owner:{max_owner}} {group:{max_group}} {size:{max_size}} {date_str} {entry}")
    else:
        if not entries:
            return
        col_width = max(len(e) for e in entries) + 2  # 2-space padding between columns
        rows = [entries[i:i + columns] for i in range(0, len(entries), columns)]
        for row in rows:
            print(''.join(f"{entry:<{col_width}}" for entry in row))

def get_rwx(mode):
    # File type character
    if stat.S_ISDIR(mode):
        ftype = 'd'
    elif stat.S_ISLNK(mode):
        ftype = 'l'
    elif stat.S_ISFIFO(mode):
        ftype = 'p'
    elif stat.S_ISSOCK(mode):
        ftype = 's'
    elif stat.S_ISBLK(mode):
        ftype = 'b'
    elif stat.S_ISCHR(mode):
        ftype = 'c'
    else:
        ftype = '-'

    # Owner
    ur = 'r' if mode & stat.S_IRUSR else '-'
    uw = 'w' if mode & stat.S_IWUSR else '-'
    ux = 'x' if mode & stat.S_IXUSR else '-'
    # setuid
    if mode & stat.S_ISUID:
        ux = 's' if mode & stat.S_IXUSR else 'S'

    # Group
    gr = 'r' if mode & stat.S_IRGRP else '-'
    gw = 'w' if mode & stat.S_IWGRP else '-'
    gx = 'x' if mode & stat.S_IXGRP else '-'
    # setgid
    if mode & stat.S_ISGID:
        gx = 's' if mode & stat.S_IXGRP else 'S'

    # Other
    or_ = 'r' if mode & stat.S_IROTH else '-'
    ow  = 'w' if mode & stat.S_IWOTH else '-'
    ox  = 'x' if mode & stat.S_IXOTH else '-'
    # sticky bit
    if mode & stat.S_ISVTX:
        ox = 't' if mode & stat.S_IXOTH else 'T'

    return f"{ftype}{ur}{uw}{ux}{gr}{gw}{gx}{or_}{ow}{ox}"

def print_help():
    print("usage: pyls [-h] [-a] [-l] [-C [COLUMNS]]  [path]")
    print("List files and directories in a given path")
    print()
    print("positional arguments:")
    print("  path                  The path to list (default: current directory)")
    print()
    print("options:")
    print("  -h, --help            Show this help message and exit")
    print("  -a, --all             Include hidden files and directories")
    print("  -l, --long            Show full information for each item")
    print("  -C, --columns [N]     Number of columns for output (default: 4)")

if __name__ == "__main__":
    path = os.getcwd()
    show_hidden = False
    verbose = False
    columns = 4

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif arg == "-a":
            show_hidden = True
        elif arg == "-l":
            verbose = True
        elif arg in ("-la", "-al"):
            show_hidden = True
            verbose = True
        elif arg == "-C":
            # Optional column count: -C alone uses default 4, -C <N> sets N columns
            if i + 1 < len(args) and args[i + 1].isdigit():
                i += 1
                columns = int(args[i])
                if columns < 1:
                    print("Error: column count must be at least 1.")
                    sys.exit(1)
        else:
            print(f"Invalid argument: {arg}. Use -h for usage information.")
            sys.exit(1)
        i += 1

    list_files_and_directories(path, show_hidden=show_hidden, verbose=verbose, columns=columns)
