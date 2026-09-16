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
import posixpath;
import shutil;
from pathlib import Path;

from .discovery import detect_platform, discover_mounts;
from .errors import UnmappedPathError, VirtualPathError;
from .model import Entry, Location, ResolvedPath, Volume;
from .paths import logical_name, logical_parent, normalize_logical, windows_logical_to_native, windows_native_to_logical;


class FileSystem:
    """Host filesystem exposed through stable SUM logical paths.""";

    def __init__(self, platform_name=None, cwd=None, home=None, mountinfo_text=None, windows_drives=None):
        self.platform_name=str(platform_name or detect_platform()).lower();
        self._mountinfo_text=mountinfo_text;
        self._windows_drives=list(windows_drives) if windows_drives is not None else None;
        self._windows=self.platform_name=="windows";
        native_cwd=str(cwd or os.getcwd());
        native_home=str(home or os.path.expanduser("~"));
        if self._windows and str(native_cwd).startswith("/"):
            native_cwd=windows_logical_to_native(native_cwd);
        if self._windows and str(native_home).startswith("/"):
            native_home=windows_logical_to_native(native_home);
        self.native_cwd=native_cwd;
        self.native_home=native_home;
        self.cwd=self.logical_path(native_cwd);
        self.home=self.logical_path(native_home);

    def normalize(self, path, cwd=None):
        raw=str(path or ".");
        if raw=="~": raw=self.home;
        elif raw.startswith("~/"): raw=posixpath.join(self.home,raw[2:]);
        if self._windows:
            try:
                if len(raw)>=2 and raw[1]==":": return windows_native_to_logical(raw);
            except Exception: pass;
            raw=raw.replace("\\","/");
        return normalize_logical(raw,cwd or self.cwd);

    def resolve(self, path, cwd=None):
        logical=self.normalize(path,cwd=cwd);
        if self._windows:
            if logical in ("/","/mnt"): return ResolvedPath(logical,None,True);
            native=windows_logical_to_native(logical);
            return ResolvedPath(logical,native,False);
        return ResolvedPath(logical,logical,False);

    def native_path(self, path, cwd=None):
        resolved=self.resolve(path,cwd=cwd);
        if resolved.virtual or resolved.native is None: raise VirtualPathError("{} has no direct native path".format(resolved.logical));
        return resolved.native;

    def logical_path(self, native_path):
        if self._windows: return windows_native_to_logical(native_path);
        raw=os.path.abspath(os.path.expanduser(str(native_path)));
        return normalize_logical(raw);

    def parent(self, path):
        return logical_parent(self.normalize(path));

    def name(self, path):
        return logical_name(self.normalize(path));

    def mounts(self):
        return discover_mounts(self.platform_name,mountinfo_text=self._mountinfo_text,windows_drives=self._windows_drives);

    def volumes(self):
        values=[]; seen=set(); pseudo={"proc","sysfs","devtmpfs","devpts","tmpfs","cgroup","cgroup2","pstore","securityfs","debugfs","tracefs","configfs","fusectl","mqueue","hugetlbfs","autofs","binfmt_misc"};
        for mount in self.mounts():
            if mount.logical_root!="/" and mount.fs_type in pseudo: continue;
            key=mount.source or mount.native_root;
            if key in seen: continue;
            seen.add(key); total=None; free=None;
            try:
                usage=shutil.disk_usage(mount.native_root); total=int(usage.total); free=int(usage.free);
            except OSError: pass;
            label=mount.logical_root if mount.logical_root!="/" else "Root";
            values.append(Volume(id=str(key),label=label,logical_root=mount.logical_root,native_root=mount.native_root,source=mount.source,fs_type=mount.fs_type,total_bytes=total,free_bytes=free,read_only=mount.read_only,removable=mount.removable));
        return values;

    def locations(self):
        rows=[]; seen=set();
        def add(name, logical, native, kind="folder"):
            key=(str(name),str(logical));
            if key in seen: return;
            seen.add(key);
            writable=False;
            if native:
                try: writable=os.access(native,os.W_OK);
                except OSError: writable=False;
            rows.append(Location(name=name,logical_path=logical,native_path=native,kind=kind,writable=writable));
        add("Home",self.home,self.native_home,"home");
        add("Current",self.cwd,self.native_cwd,"current");
        for volume in self.volumes():
            name="{}".format(volume.label);
            add(name,volume.logical_root,volume.native_root,"volume");
        return rows;

    def _virtual_entries(self, logical):
        rows=[];
        if not self._windows: return rows;
        if logical=="/":
            rows.append(Entry(name="mnt",logical_path="/mnt",native_path=None,is_dir=True,is_file=False,virtual=True));
            return rows;
        if logical=="/mnt":
            for mount in sorted(self.mounts(),key=lambda item:item.logical_root.casefold()):
                rows.append(Entry(name=logical_name(mount.logical_root),logical_path=mount.logical_root,native_path=mount.native_root,is_dir=True,is_file=False,virtual=True));
            return rows;
        return rows;

    def entries(self, path="."):
        resolved=self.resolve(path);
        if resolved.virtual: return self._virtual_entries(resolved.logical);
        rows=[];
        try: items=list(os.scandir(resolved.native));
        except OSError: return rows;
        items.sort(key=lambda item:(not item.is_dir(follow_symlinks=False),item.name.casefold()));
        for item in items:
            logical=normalize_logical(posixpath.join(resolved.logical,item.name));
            try:
                symlink=item.is_symlink(); is_dir=item.is_dir(follow_symlinks=False); is_file=item.is_file(follow_symlinks=False); stat=item.stat(follow_symlinks=False); size=None if is_dir else int(stat.st_size);
            except OSError:
                symlink=False; is_dir=False; is_file=False; size=None;
            rows.append(Entry(name=item.name,logical_path=logical,native_path=item.path,is_dir=is_dir,is_file=is_file,is_symlink=symlink,size=size,virtual=False));
        return rows;

    def exists(self,path):
        resolved=self.resolve(path);
        if resolved.virtual: return resolved.logical in ("/","/mnt");
        return os.path.exists(resolved.native);

    def is_dir(self,path):
        resolved=self.resolve(path);
        if resolved.virtual: return True;
        return os.path.isdir(resolved.native);

    def is_file(self,path):
        resolved=self.resolve(path);
        if resolved.virtual: return False;
        return os.path.isfile(resolved.native);

    def stat(self,path,follow_symlinks=True):
        return os.stat(self.native_path(path),follow_symlinks=bool(follow_symlinks));
