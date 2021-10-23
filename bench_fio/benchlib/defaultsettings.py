#!/usr/bin/env python3
import os
import sys


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
    settings["precondition"] = False
    settings["precondition_template"] = "precondition.fio"
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
    settings["loginterval"] = 500
    settings["mixed"] = ["readwrite", "rw", "randrw"]
    settings["invalidate"] = 1
    settings["ceph_pool"] = None
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

    for mode in settings["mode"]:
        if mode in settings["mixed"]:
            if settings["rwmixread"]:
                settings["loop_items"].append("rwmixread")
            else:
                print(
                    "\nIf a mixed (read/write) mode is specified, please specify --rwmixread\n"
                )
                sys.exit(8)
        else:
            settings["filter_items"].append("rwmixread")
