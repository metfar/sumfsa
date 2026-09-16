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
import posixpath;
import re;
from pathlib import PureWindowsPath;

from .errors import UnmappedPathError, VirtualPathError;

_WINDOWS_DRIVE_RE=re.compile(r"^([A-Za-z]):(?:[\\/](.*))?$");
_MNT_DRIVE_RE=re.compile(r"^/mnt/([A-Za-z])(?:/(.*))?$");


def normalize_logical(path, cwd="/"):
    """Normalize a SUM logical path using POSIX separators on every host.""";
    raw=str(path or ".");
    match=_WINDOWS_DRIVE_RE.match(raw);
    if match:
        suffix=(match.group(2) or "").replace("\\","/");
        raw="/mnt/{}/{}".format(match.group(1).lower(),suffix) if suffix else "/mnt/{}".format(match.group(1).lower());
    if not raw.startswith("/"):
        base=str(cwd or "/");
        if not base.startswith("/"): raise ValueError("logical cwd must be absolute");
        raw=posixpath.join(base,raw);
    value=posixpath.normpath(raw);
    if not value.startswith("/"): value="/"+value;
    return value;


def windows_native_to_logical(path):
    raw=str(path);
    match=_WINDOWS_DRIVE_RE.match(raw);
    if not match:
        pure=PureWindowsPath(raw);
        drive=pure.drive;
        if not drive or not drive.endswith(":"): raise UnmappedPathError("Windows path has no drive: {}".format(path));
        letter=drive[0].lower();
        parts=list(pure.parts[1:]);
    else:
        letter=match.group(1).lower();
        suffix=(match.group(2) or "").replace("\\","/");
        parts=[part for part in suffix.split("/") if part];
    return normalize_logical("/mnt/{}/{}".format(letter,"/".join(parts)) if parts else "/mnt/{}".format(letter));


def windows_logical_to_native(path):
    logical=normalize_logical(path);
    if logical in ("/", "/mnt"): raise VirtualPathError("{} is a virtual SUM path on Windows".format(logical));
    match=_MNT_DRIVE_RE.match(logical);
    if not match: raise UnmappedPathError("unmapped Windows logical path: {}".format(logical));
    drive=match.group(1).upper()+":\\";
    suffix=match.group(2) or "";
    if not suffix: return drive;
    return str(PureWindowsPath(drive,*[part for part in suffix.split("/") if part]));


def logical_parent(path):
    logical=normalize_logical(path);
    if logical=="/": return "/";
    return posixpath.dirname(logical) or "/";


def logical_name(path):
    logical=normalize_logical(path);
    return "/" if logical=="/" else posixpath.basename(logical);
