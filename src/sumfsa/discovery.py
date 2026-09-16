#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
import os;
import platform;
import re;
import string;
from pathlib import Path;
from typing import Iterable, List, Optional;

from .model import Mount;
from .paths import windows_native_to_logical;

_MOUNT_ESCAPE_RE=re.compile(r"\\([0-7]{3})");


def detect_platform():
    if os.environ.get("ANDROID_ROOT") or os.environ.get("ANDROID_DATA") or os.environ.get("TERMUX_VERSION"): return "android";
    name=platform.system().lower();
    if name.startswith("win"): return "windows";
    if name=="darwin": return "darwin";
    return "linux" if name=="linux" else (name or "posix");


def decode_mount_field(value):
    return _MOUNT_ESCAPE_RE.sub(lambda match: chr(int(match.group(1),8)),str(value));


def parse_mountinfo(text):
    """Parse Linux /proc/*/mountinfo into SUM Mount objects.""";
    mounts=[];
    for raw_line in str(text or "").splitlines():
        line=raw_line.strip();
        if not line: continue;
        fields=line.split();
        try: separator=fields.index("-");
        except ValueError: continue;
        if separator < 6 or separator+2 >= len(fields): continue;
        native_root=decode_mount_field(fields[4]);
        options=tuple(item for item in fields[5].split(",") if item);
        fs_type=fields[separator+1];
        source=decode_mount_field(fields[separator+2]);
        mounts.append(Mount(logical_root=native_root,native_root=native_root,source=source,fs_type=fs_type,options=options,read_only="ro" in options,removable=native_root.startswith(("/media/","/run/media/","/mnt/"))));
    return mounts;


def discover_linux_mounts(mountinfo_text=None):
    if mountinfo_text is None:
        try: mountinfo_text=Path("/proc/self/mountinfo").read_text(encoding="utf-8",errors="replace");
        except OSError: mountinfo_text="";
    mounts=parse_mountinfo(mountinfo_text);
    if mounts: return mounts;
    return [Mount(logical_root="/",native_root="/",source="/",fs_type="",options=(),read_only=False,removable=False)];


def _windows_drive_type(root):
    try:
        import ctypes;
        drive_type=int(ctypes.windll.kernel32.GetDriveTypeW(str(root)));
        return drive_type;
    except Exception:
        return 0;


def discover_windows_mounts(drives=None):
    roots=[];
    if drives is not None:
        roots=[str(item) for item in drives];
    else:
        for letter in string.ascii_uppercase:
            root="{}:\\".format(letter);
            if os.path.exists(root): roots.append(root);
    mounts=[];
    for root in roots:
        try: logical=windows_native_to_logical(root);
        except Exception: continue;
        drive_type=_windows_drive_type(root);
        mounts.append(Mount(logical_root=logical,native_root=root,source=root,fs_type="",options=(),read_only=False,removable=drive_type in (2,5)));
    return mounts;


def discover_mounts(platform_name=None,mountinfo_text=None,windows_drives=None):
    name=str(platform_name or detect_platform()).lower();
    if name=="windows": return discover_windows_mounts(windows_drives);
    return discover_linux_mounts(mountinfo_text);
