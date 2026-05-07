#!/usr/bin/python

import grp
import os
import pwd
import stat
import sys
import time


# ANSI color codes
_RESET  = "\033[0m"
_DIR    = "\033[1;34m"   # bold blue    — directories
_LINK   = "\033[1;36m"   # bold cyan    — symbolic links
_EXEC   = "\033[1;32m"   # bold green   — executables
_PIPE   = "\033[33m"     # yellow       — named pipes (FIFOs)
_SOCK   = "\033[1;35m"   # bold magenta — sockets
_BLK    = "\033[1;33m"   # bold yellow  — block devices
_CHR    = "\033[1;33m"   # bold yellow  — character devices


def use_color():
    return sys.stdout.isatty()


def colorize_name(name, mode):
    if not use_color():
        return name
    if stat.S_ISDIR(mode):
        return f"{_DIR}{name}{_RESET}"
    if stat.S_ISLNK(mode):
        return f"{_LINK}{name}{_RESET}"
    if stat.S_ISFIFO(mode):
        return f"{_PIPE}{name}{_RESET}"
    if stat.S_ISSOCK(mode):
        return f"{_SOCK}{name}{_RESET}"
    if stat.S_ISBLK(mode):
        return f"{_BLK}{name}{_RESET}"
    if stat.S_ISCHR(mode):
        return f"{_CHR}{name}{_RESET}"
    if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        return f"{_EXEC}{name}{_RESET}"
    return name


def type_indicator(mode):
    if stat.S_ISDIR(mode):
        return "/"
    if stat.S_ISLNK(mode):
        return "@"
    if stat.S_ISFIFO(mode):
        return "|"
    if stat.S_ISSOCK(mode):
        return "="
    if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        return "*"
    return ""


def sort_entries(entries, sort_by, group_dirs_first, reverse=False):
    if sort_by == "mtime":
        entries = sorted(entries, key=lambda e: e.stat(follow_symlinks=False).st_mtime, reverse=not reverse)
    elif sort_by == "size":
        entries = sorted(entries, key=lambda e: e.stat(follow_symlinks=False).st_size, reverse=not reverse)
    else:
        entries = sorted(entries, key=lambda e: e.name.lower(), reverse=reverse)

    if group_dirs_first:
        dirs  = [e for e in entries if stat.S_ISDIR(e.stat(follow_symlinks=False).st_mode)]
        files = [e for e in entries if not stat.S_ISDIR(e.stat(follow_symlinks=False).st_mode)]
        entries = dirs + files

    return entries


def list_files_and_directories(path, show_hidden=False, verbose=False,
                                human_readable=False, columns=4,
                                sort_by="name", group_dirs_first=False,
                                reverse=False, recursive=False, classify=False,
                                dirs_only=False):
    def _list_one(current_path, label, first=True):
        try:
            with os.scandir(current_path) as it:
                entries = [e for e in it if show_hidden or not e.name.startswith(".")]
        except OSError as exc:
            print(f"Error reading {current_path}: {exc}", file=sys.stderr)
            return

        if dirs_only:
            entries = [e for e in entries if e.is_dir(follow_symlinks=False)]

        entries = sort_entries(entries, sort_by, group_dirs_first, reverse=reverse)

        if recursive:
            if not first:
                print()
            print(f"{label}:")

        if verbose:
            print_verbose(entries, human_readable=human_readable, classify=classify)
        else:
            print_columns(entries, columns, classify=classify)

        if recursive:
            subdirs = [
                e for e in entries
                if e.is_dir(follow_symlinks=False)
            ]
            for sub in subdirs:
                sub_label = f"{label}/{sub.name}"
                _list_one(sub.path, sub_label, first=False)

    start_label = "."
    if os.path.abspath(path) != os.path.abspath(os.getcwd()):
        start_label = path.rstrip("/")

    _list_one(path, start_label, first=True)


def format_size(size):
    if size >= 1024 ** 3:
        value = size / (1024 ** 3)
        return f"{value:.1f}G" if value < 10 else f"{value:.0f}G"
    elif size >= 1024 ** 2:
        value = size / (1024 ** 2)
        return f"{value:.1f}M" if value < 10 else f"{value:.0f}M"
    elif size >= 1024:
        value = size / 1024
        return f"{value:.1f}K" if value < 10 else f"{value:.0f}K"
    else:
        return str(size)


def print_verbose(entries, human_readable=False, classify=False):
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
                st.st_mode,
            )
        )

    print(f"total {total_blocks // 2}")

    max_nlink = max(len(str(row[1])) for row in rows)
    max_owner = max(len(row[2]) for row in rows)
    max_group = max(len(row[3]) for row in rows)

    if human_readable:
        size_strs = [format_size(row[4]) for row in rows]
        max_size = max(len(s) for s in size_strs)
        for (mode_str, nlink, owner, group, size, date_str, name, file_mode), size_str in zip(rows, size_strs):
            colored = colorize_name(name, file_mode)
            indicator = type_indicator(file_mode) if classify else ""
            print(
                f"{mode_str} {nlink:{max_nlink}} {owner:{max_owner}} "
                f"{group:{max_group}} {size_str:>{max_size}} {date_str} {colored}{indicator}"
            )
    else:
        max_size = max(len(str(row[4])) for row in rows)
        for mode_str, nlink, owner, group, size, date_str, name, file_mode in rows:
            colored = colorize_name(name, file_mode)
            indicator = type_indicator(file_mode) if classify else ""
            print(
                f"{mode_str} {nlink:{max_nlink}} {owner:{max_owner}} "
                f"{group:{max_group}} {size:{max_size}} {date_str} {colored}{indicator}"
            )


def print_columns(entries, columns, classify=False):
    if not entries:
        return

    # Column width accounts for the indicator character when -F is active
    col_width = max(
        len(entry.name) + len(type_indicator(entry.stat(follow_symlinks=False).st_mode) if classify else "")
        for entry in entries
    ) + 2
    for start in range(0, len(entries), columns):
        row_entries = entries[start:start + columns]
        parts = []
        for entry in row_entries:
            st = entry.stat(follow_symlinks=False)
            indicator = type_indicator(st.st_mode) if classify else ""
            colored = colorize_name(entry.name, st.st_mode)
            # Pad by the plain display width so ANSI codes don't break alignment
            display_len = len(entry.name) + len(indicator)
            padding = col_width - display_len
            parts.append(colored + indicator + " " * padding)
        print("".join(parts))


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
    print("usage: pyls [--help] [-a] [-l] [-h] [-F] [-d] [-t] [-S] [-r] [-R] [--group-directories-first] [-C [COLUMNS]] [path]")
    print("List files and directories in a given path")
    print()
    print("positional arguments:")
    print("  path                       The path to list (default: current directory)")
    print()
    print("options:")
    print("  --help                     Show this help message and exit")
    print("  -a, --all                  Include hidden files and directories")
    print("  -l, --long                 Show full information for each item")
    print("  -h                         With -l, show file sizes in human-readable form")
    print("                             (e.g. 1.2K, 3.7M, 2.1G) instead of raw bytes")
    print("  -F                         Append a type indicator to each name:")
    print("                               /  directory    *  executable")
    print("                               @  symlink      |  named pipe    =  socket")
    print("  -d                         List only directories, not their contents")
    print("  -t                         Sort by modification time, newest first")
    print("  -S                         Sort by file size, largest first")
    print("  -r                         Reverse the sort order")
    print("  -R                         Recursively list subdirectories")
    print("  --group-directories-first  List directories before files")
    print("  -C, --columns [N]          Number of columns for output (default: 4)")
    print()
    print("  Short flags can be combined freely, e.g. -lath, -Salt")
    print()
    print("colors (when output is a terminal):")
    print("  bold blue                  directories")
    print("  bold cyan                  symbolic links")
    print("  bold green                 executables")
    print("  yellow                     named pipes (FIFOs)")
    print("  bold magenta               sockets")
    print("  bold yellow                block/character devices")
    print()
    print("  Colors are suppressed automatically when output is piped or redirected.")


# Single-character flags that consume no extra argument.
_SHORT_FLAGS = {
    'a': 'show_hidden',
    'l': 'verbose',
    'h': 'human_readable',
    'F': 'classify',
    'd': 'dirs_only',
    't': 'sort_mtime',
    'S': 'sort_size',
    'r': 'reverse',
    'R': 'recursive',
}


def parse_args(args):
    opts = {
        'path': None,
        'show_hidden': False,
        'verbose': False,
        'human_readable': False,
        'classify': False,
        'dirs_only': False,
        'sort_by': 'name',
        'reverse': False,
        'recursive': False,
        'group_dirs_first': False,
        'columns': 4,
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--help":
            print_help()
            sys.exit(0)

        elif arg == "--group-directories-first":
            opts['group_dirs_first'] = True

        elif arg == "--all":
            opts['show_hidden'] = True

        elif arg == "--long":
            opts['verbose'] = True

        elif arg == "--columns":
            if i + 1 < len(args) and args[i + 1].isdigit():
                i += 1
                opts['columns'] = int(args[i])
                if opts['columns'] < 1:
                    print("Error: column count must be at least 1.")
                    sys.exit(1)

        elif arg.startswith("--"):
            print(f"Invalid option: {arg}. Use --help for usage information.")
            sys.exit(1)

        elif arg.startswith("-") and len(arg) > 1:
            # Parse each character in the combined flag (e.g. -lath)
            chars = arg[1:]
            j = 0
            while j < len(chars):
                ch = chars[j]
                if ch == 'C':
                    # -C may be followed by digits in the same token or next arg
                    remainder = chars[j + 1:]
                    if remainder.isdigit():
                        opts['columns'] = int(remainder)
                        if opts['columns'] < 1:
                            print("Error: column count must be at least 1.")
                            sys.exit(1)
                        break
                    elif i + 1 < len(args) and args[i + 1].isdigit():
                        i += 1
                        opts['columns'] = int(args[i])
                        if opts['columns'] < 1:
                            print("Error: column count must be at least 1.")
                            sys.exit(1)
                        break
                    else:
                        break
                elif ch in _SHORT_FLAGS:
                    key = _SHORT_FLAGS[ch]
                    if key == 'sort_mtime':
                        opts['sort_by'] = 'mtime'
                    elif key == 'sort_size':
                        opts['sort_by'] = 'size'
                    elif key == 'reverse':
                        opts['reverse'] = True
                    else:
                        opts[key] = True
                else:
                    print(f"Invalid flag: -{ch}. Use --help for usage information.")
                    sys.exit(1)
                j += 1

        else:
            opts['path'] = arg

        i += 1

    return opts


if __name__ == "__main__":
    opts = parse_args(sys.argv[1:])

    path = opts['path'] if opts['path'] is not None else os.getcwd()

    try:
        list_files_and_directories(
            path,
            show_hidden=opts['show_hidden'],
            verbose=opts['verbose'],
            human_readable=opts['human_readable'],
            classify=opts['classify'],
            dirs_only=opts['dirs_only'],
            columns=opts['columns'],
            sort_by=opts['sort_by'],
            reverse=opts['reverse'],
            recursive=opts['recursive'],
            group_dirs_first=opts['group_dirs_first'],
        )
    except BrokenPipeError:
        # Downstream consumers like less/head may stop early; exit quietly.
        sys.stdout = None
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
