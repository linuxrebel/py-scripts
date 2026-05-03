#!/usr/bin/python

import grp
import os
import pwd
import stat
import sys
import time


def list_files_and_directories(path, show_hidden=False, verbose=False, columns=4):
    try:
        with os.scandir(path) as it:
            entries = [entry for entry in it if show_hidden or not entry.name.startswith(".")]
    except OSError as exc:
        print(f"Error reading {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print_verbose(entries)
    else:
        print_columns(entries, columns)


def print_verbose(entries):
    if not entries:
        print("total 0")
        return

    uid_cache = {}
    gid_cache = {}
    current_year = time.localtime().tm_year
    rows = []
    total_blocks = 0

    for entry in entries:
        st = entry.stat(follow_symlinks=False)
        total_blocks += st.st_blocks
        rows.append(
            (
                get_rwx(st.st_mode),
                st.st_nlink,
                lookup_owner(st.st_uid, uid_cache),
                lookup_group(st.st_gid, gid_cache),
                st.st_size,
                format_mtime(st.st_mtime, current_year),
                entry.name,
            )
        )

    print(f"total {total_blocks // 2}")

    max_nlink = max(len(str(row[1])) for row in rows)
    max_owner = max(len(row[2]) for row in rows)
    max_group = max(len(row[3]) for row in rows)
    max_size = max(len(str(row[4])) for row in rows)

    for mode_str, nlink, owner, group, size, date_str, name in rows:
        print(
            f"{mode_str} {nlink:{max_nlink}} {owner:{max_owner}} "
            f"{group:{max_group}} {size:{max_size}} {date_str} {name}"
        )


def print_columns(entries, columns):
    if not entries:
        return

    names = [entry.name for entry in entries]
    col_width = max(len(name) for name in names) + 2
    for start in range(0, len(names), columns):
        row = names[start:start + columns]
        print("".join(f"{name:<{col_width}}" for name in row))


def lookup_owner(uid, cache):
    owner = cache.get(uid)
    if owner is None:
        try:
            owner = pwd.getpwuid(uid).pw_name
        except KeyError:
            owner = str(uid)
        cache[uid] = owner
    return owner


def lookup_group(gid, cache):
    group = cache.get(gid)
    if group is None:
        try:
            group = grp.getgrgid(gid).gr_name
        except KeyError:
            group = str(gid)
        cache[gid] = group
    return group


def format_mtime(mtime, current_year):
    t = time.localtime(mtime)
    if t.tm_year == current_year:
        return time.strftime("%b %e %H:%M", t)
    return time.strftime("%b %e  %Y", t)


def get_rwx(mode):
    if stat.S_ISDIR(mode):
        ftype = "d"
    elif stat.S_ISLNK(mode):
        ftype = "l"
    elif stat.S_ISFIFO(mode):
        ftype = "p"
    elif stat.S_ISSOCK(mode):
        ftype = "s"
    elif stat.S_ISBLK(mode):
        ftype = "b"
    elif stat.S_ISCHR(mode):
        ftype = "c"
    else:
        ftype = "-"

    ur = "r" if mode & stat.S_IRUSR else "-"
    uw = "w" if mode & stat.S_IWUSR else "-"
    ux = "x" if mode & stat.S_IXUSR else "-"
    if mode & stat.S_ISUID:
        ux = "s" if mode & stat.S_IXUSR else "S"

    gr = "r" if mode & stat.S_IRGRP else "-"
    gw = "w" if mode & stat.S_IWGRP else "-"
    gx = "x" if mode & stat.S_IXGRP else "-"
    if mode & stat.S_ISGID:
        gx = "s" if mode & stat.S_IXGRP else "S"

    or_ = "r" if mode & stat.S_IROTH else "-"
    ow = "w" if mode & stat.S_IWOTH else "-"
    ox = "x" if mode & stat.S_IXOTH else "-"
    if mode & stat.S_ISVTX:
        ox = "t" if mode & stat.S_IXOTH else "T"

    return f"{ftype}{ur}{uw}{ux}{gr}{gw}{gx}{or_}{ow}{ox}"


def print_help():
    print("usage: pyls [-h] [-a] [-l] [-C [COLUMNS]] [path]")
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
        if arg == "-a":
            show_hidden = True
        elif arg == "-l":
            verbose = True
        elif arg in ("-la", "-al"):
            show_hidden = True
            verbose = True
        elif arg == "-C":
            if i + 1 < len(args) and args[i + 1].isdigit():
                i += 1
                columns = int(args[i])
                if columns < 1:
                    print("Error: column count must be at least 1.")
                    sys.exit(1)
        elif arg.startswith("-"):
            print(f"Invalid argument: {arg}. Use -h for usage information.")
            sys.exit(1)
        else:
            path = arg
        i += 1

    try:
        list_files_and_directories(path, show_hidden=show_hidden, verbose=verbose, columns=columns)
    except BrokenPipeError:
        # Downstream consumers like less/head may stop early; exit quietly.
        sys.stdout = None
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
