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
import argparse;

from sumui.cli import SumArgumentParser;
from . import __version__;
from .filesystem import FileSystem;


def _size(value):
    if value is None: return "?";
    n=float(value);
    for suffix in ("B","KiB","MiB","GiB","TiB"):
        if n<1024.0 or suffix=="TiB": return "{} {}".format(int(n),suffix) if suffix=="B" else "{:.1f} {}".format(n,suffix);
        n/=1024.0;
    return str(value);


def main(argv=None):
    parser=SumArgumentParser(prog="sumfsa",description="SUM filesystem abstraction inspector.");
    parser.add_argument("--version",action="version",version="sumfsa {}".format(__version__));
    sub=parser.add_subparsers(dest="command");
    path=sub.add_parser("path"); path.add_argument("value");
    sub.add_parser("mounts"); sub.add_parser("volumes"); sub.add_parser("locations");
    ls=sub.add_parser("ls"); ls.add_argument("value",nargs="?",default=".");
    args=parser.parse_args(argv); fs=FileSystem();
    if args.command=="path":
        resolved=fs.resolve(args.value); print("logical={}".format(resolved.logical)); print("native={}".format(resolved.native if resolved.native is not None else "<virtual>")); return 0;
    if args.command=="mounts":
        for item in fs.mounts(): print("{}\t{}\t{}\t{}".format(item.logical_root,item.native_root,item.fs_type,item.source));
        return 0;
    if args.command=="volumes":
        for item in fs.volumes(): print("{}\t{}\tfree={}\ttotal={}".format(item.logical_root,item.fs_type,_size(item.free_bytes),_size(item.total_bytes)));
        return 0;
    if args.command=="locations":
        for item in fs.locations(): print("{}\t{}\t{}".format(item.name,item.logical_path,item.native_path if item.native_path is not None else "<virtual>"));
        return 0;
    if args.command=="ls":
        for item in fs.entries(args.value): print("{}\t{}\t{}".format("d" if item.is_dir else "f",item.name,"" if item.size is None else item.size));
        return 0;
    parser.print_help(); return 0;
