#!/usr/bin/env python3
import os
import sys
import configparser
from pathlib import Path

def get_settings_from_ini(args):
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    listtypes = ['target','mode','block_size', 'iodepth', 'numjobs','extra_opts', 'rwmixread']
    booltypes = ['precondition','precondition_repeat','entire_device','time_based','destructive','dry_run','quiet']
    returndict = {}
    if len(args) == 2:
        filename = args[1]
        path = Path(filename)
        if path.is_file():
            try:
                config.read(filename)
            except configparser.DuplicateOptionError as e:
                print(f"{e}\n")
                sys.exit(1)
            for x in config["benchfio"]:
                if x in listtypes:
                    returndict[x] = config.getlist('benchfio', x)
                elif x in booltypes:
                    returndict[x] = config.getboolean('benchfio', x)
                else:
                    returndict[x] = config["benchfio"][x]
            #print(returndict)
            return returndict
        else:
            print(f"Config file {filename} not found.")
            sys.exit(1)
    return None

def get_default_settings():
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    settings = {}
    settings["target"] = []
    settings["template"] = os.path.join(dir_path, "..", "templates", "fio-job-template.fio")
    settings["engine"] = "libaio"
    settings["mode"] = ["randread", "randwrite"]
    settings["iodepth"] = [1, 2, 4, 8, 16, 32, 64]
    settings["numjobs"] = [1, 2, 4, 8, 16, 32, 64]
    settings["block_size"] = ["4k"]
    settings["direct"] = 1
    settings["size"] = None
    settings["dry_run"] = False
    settings["precondition"] = False
    settings["quiet"] = False
    settings["output"] = False
    settings["precondition_template"] = os.path.join(dir_path, "..", "templates", "precondition.fio") 
    settings["precondition_repeat"] = False
    settings["entire_device"] = False
    settings["ss"] = False
    settings["ss_dur"] = None
    settings["ss_ramp"] = None
    settings["rwmixread"] = None
    settings["runtime"] = 60
    settings["loops"] = 1
    settings["time_based"] = False
    settings["extra_opts"] = []
    settings["loginterval"] = 1000
    settings["mixed"] = ["readwrite", "rw", "randrw"]
    settings["invalidate"] = 1
    settings["ceph_pool"] = None
    settings["destructive"] = False
    settings["loop_items"] = [
        "target",
        "mode",
        "iodepth",
        "numjobs",
        "block_size",
    ]
    settings["filter_items"] = [
        "filter_items",
        "loop_items",
        "dry_run",
        "mixed",
        "quiet",
    ]
    return settings


def check_settings(settings):
    """Some basic error handling."""
    if not os.path.exists(settings["template"]):
        print()
        print(f"The specified template {settings['template']} does not exist.")
        print()
        sys.exit(6)

    if settings["type"] not in ["device", "rbd"] and not settings["size"]:
        print()
        print("When the target is a file or directory, --size must be specified.")
        print()
        sys.exit(4)

    if settings["type"] == "directory":
        for item in settings["target"]:
            if not os.path.exists(item):
                print(f"\nThe target directory ({item}) doesn't seem to exist.\n")
                sys.exit(5)

    if settings["type"] == "rbd":
        if not settings["ceph_pool"]:
            print(
                "\nCeph pool (--ceph-pool) must be specified when target type is rbd.\n"
            )
            sys.exit(6)

    if settings["type"] == "rbd" and settings["ceph_pool"]:
        if settings["template"] == "./fio-job-template.fio":
            print(
                "Please specify the appropriate Fio template (--template).\n\
                    The example fio-job-template-ceph.fio can be used."
            )
            sys.exit(7)

    if not settings["output"]:
        print()
        print("Must specify mandatory --output parameter (name of benchmark output folder)")
        print()
        sys.exit(9)

    mixed_count = 0
    for mode in settings["mode"]:
        writemodes = ['write', 'randwrite', 'rw', 'readwrite', 'trimwrite']
        if mode in writemodes and not settings["destructive"]:
            print(f"\n Mode {mode} will overwrite data on {settings['target']} but destructive flag not set.\n")
            sys.exit(1)
        if mode in settings["mixed"]:
            mixed_count+=1
            if not settings["rwmixread"]:
                print(
                    "\nIf a mixed (read/write) mode is specified, please specify --rwmixread\n"
                )
                sys.exit(8)
        if mixed_count > 0:
            settings["loop_items"].append("rwmixread")
    
