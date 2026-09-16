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
#
#import warnings;
#warnings.filterwarnings("ignore", category=UserWarning);
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
from pathlib import Path;

import pytest;

from sumfsa import FileSystem, VirtualPathError, normalize_logical, parse_mountinfo, windows_logical_to_native, windows_native_to_logical;


def test_logical_normalization_is_host_independent():
    assert normalize_logical("../logs","/home/me/work")=="/home/me/logs";
    assert normalize_logical("C:\\Users\\wm\\code")=="/mnt/c/Users/wm/code";


def test_windows_roundtrip_and_virtual_mnt():
    assert windows_native_to_logical("D:\\data\\src")=="/mnt/d/data/src";
    assert windows_logical_to_native("/mnt/d/data/src")=="D:\\data\\src";
    fs=FileSystem(platform_name="windows",cwd="C:\\Users\\wm",home="C:\\Users\\wm",windows_drives=["C:\\","D:\\"]);
    assert fs.cwd=="/mnt/c/Users/wm";
    assert fs.resolve("/mnt").virtual is True;
    assert [entry.name for entry in fs.entries("/mnt")]==["c","d"];
    with pytest.raises(VirtualPathError): fs.native_path("/mnt");


def test_linux_path_mapping_is_transparent(tmp_path):
    fs=FileSystem(platform_name="linux",cwd=str(tmp_path),home=str(tmp_path));
    target=tmp_path/"folder"/"x.txt"; target.parent.mkdir(); target.write_text("hello",encoding="utf-8");
    logical=fs.logical_path(target);
    assert fs.native_path(logical)==str(target);
    assert fs.is_file(logical);
    assert [item.name for item in fs.entries(str(target.parent))]==["x.txt"];


def test_mountinfo_parser_decodes_kernel_escapes():
    text="36 25 8:1 / / rw,relatime - ext4 /dev/sda1 rw\n41 36 8:2 / /media/My\\040Disk rw,nosuid - vfat /dev/sdb1 rw\n";
    mounts=parse_mountinfo(text);
    assert mounts[0].logical_root=="/";
    assert mounts[0].fs_type=="ext4";
    assert mounts[1].logical_root=="/media/My Disk";
    assert mounts[1].removable is True;


def test_locations_expose_home_current_and_mounts(tmp_path):
    text="36 25 8:1 / / rw,relatime - ext4 /dev/sda1 rw\n";
    fs=FileSystem(platform_name="linux",cwd=str(tmp_path),home=str(tmp_path),mountinfo_text=text);
    locations=fs.locations(); names=[item.name for item in locations];
    assert "Home" in names;
    assert "Current" in names;
    assert any(item.logical_path=="/" for item in locations);
