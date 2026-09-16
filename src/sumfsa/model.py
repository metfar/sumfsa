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
from dataclasses import dataclass;
from typing import Optional, Tuple;


@dataclass(frozen=True)
class ResolvedPath:
    logical: str;
    native: Optional[str];
    virtual: bool = False;


@dataclass(frozen=True)
class Mount:
    logical_root: str;
    native_root: str;
    source: str = "";
    fs_type: str = "";
    options: Tuple[str, ...] = ();
    read_only: bool = False;
    removable: bool = False;


@dataclass(frozen=True)
class Volume:
    id: str;
    label: str;
    logical_root: str;
    native_root: str;
    source: str = "";
    fs_type: str = "";
    total_bytes: Optional[int] = None;
    free_bytes: Optional[int] = None;
    read_only: bool = False;
    removable: bool = False;


@dataclass(frozen=True)
class Location:
    name: str;
    logical_path: str;
    native_path: Optional[str];
    kind: str = "folder";
    writable: bool = True;


@dataclass(frozen=True)
class Entry:
    name: str;
    logical_path: str;
    native_path: Optional[str];
    is_dir: bool;
    is_file: bool;
    is_symlink: bool = False;
    size: Optional[int] = None;
    virtual: bool = False;
