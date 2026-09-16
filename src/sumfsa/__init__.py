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
from .discovery import decode_mount_field, detect_platform, discover_mounts, parse_mountinfo;
from .errors import FSAError, UnmappedPathError, VirtualPathError;
from .filesystem import FileSystem;
from .model import Entry, Location, Mount, ResolvedPath, Volume;
from .paths import logical_name, logical_parent, normalize_logical, windows_logical_to_native, windows_native_to_logical;

__version__="0.1.0a1";
__all__=["Entry","FSAError","FileSystem","Location","Mount","ResolvedPath","UnmappedPathError","VirtualPathError","Volume","decode_mount_field","detect_platform","discover_mounts","logical_name","logical_parent","normalize_logical","parse_mountinfo","windows_logical_to_native","windows_native_to_logical"];
