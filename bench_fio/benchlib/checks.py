#!/usr/bin/env python3
import shutil
import sys
import os
from pathlib import Path
from . import runfio

def check_if_fio_exists():
    command = "fio"
    if shutil.which(command) is None:
        print("Fio executable not found in path. Is Fio installed?")
        print()
        sys.exit(1)


def check_fio_version():
    """The 3.x series .json format is different from the 2.x series format.
    This breaks fio-plot, thus this older version is not supported.
    """

    command = ["fio", "--version"]
    result = runfio.run_raw_command(command).stdout
    result = result.decode("UTF-8").strip()
    if "fio-3" in result:
        return True
    elif "fio-2" in result:
        print(f"Your Fio version ({result}) is not compatible. Please use Fio-3.x")
        sys.exit(1)
    else:
        print("Could not detect Fio version.")
        sys.exit(1)

def check_encoding():
    try:
        print("\u3000")  # blank space
    except UnicodeEncodeError:
        print()
        print(
            "It seems your default encoding is not UTF-8. This script requires UTF-8."
        )
        print(
            "You can change the default encoding with 'export PYTHONIOENCODING=UTF-8'"
        )
        print("Or you can run the script like: PYTHONIOENCODING=utf-8 ./bench_fio")
        print("Changing the default encoding could affect other applications, beware.")
        print()
        exit(90)

def check_target_type(target, settings):
    """Validate path and file/directory type and return fio command line parameter."""
    filetype = settings["type"]
    types = ["file", "device", "directory", "rbd"]
    path_target = Path(target)

    if filetype == "rbd":
        return None

    if not filetype in types:
        print(f"Error, filetype {filetype} is an unknown option.")
        exit(123)

    if not os.path.exists(target) and not settings["remote"] and not settings["create"]:
        print(f"Benchmark target {filetype} {target} does not exist.")
        sys.exit(10)

    check = {"file": Path.is_file, "device": Path.is_block_device, "directory": Path.is_dir}[filetype]

    if not settings["remote"] and not settings["create"]:
        if check(path_target):
            return {"file": "filename", "device": "filename", "directory": "directory"}[filetype]
        else:
            print(f"Target {filetype} {target} is not {filetype}.")
            sys.exit(10)
    else:
        return {"file": "filename", "device": "filename", "directory": "directory"}[filetype]


def check_settings(settings):
    """Some basic error handling."""

    check_fio_version()

    if settings["entire_device"]:
        settings.update(runtime=None, size="100%")
        if settings["type"] != "device":
            print("\nPreconditioning only makes sense for (flash) devices, not files or directories.\n")
            sys.exit(9)

    if settings["type"] in ["device", "rbd"] and not settings["size"]:
        print("\nWhen the target is a file or directory, --size must be specified.\n")
        sys.exit(4)

    if settings["type"] == "directory" and not settings["remote"] and not settings["create"]:
        for item in settings["target"]:
            if not os.path.exists(item):
                print(f"\nThe target directory ({item}) doesn't seem to exist.\n")
                sys.exit(5)

    if settings["type"] == "rbd" and not settings["ceph_pool"]:
        print("\nCeph pool (--ceph-pool) must be specified when target type is rbd.\n")
        sys.exit(6)

    if settings["type"] == "rbd" and settings["ceph_pool"] and settings["engine"] != "rbd":
        print(f"\nPlease specify engine 'rbd' when benchmarking Ceph, not {settings['engine']}\n")
        sys.exit(7)

    if not settings["output"]:
        print("\nMust specify mandatory --output parameter (name of benchmark output folder)\n")
        sys.exit(9)

    writemodes = ['write', 'randwrite', 'rw', 'readwrite', 'trimwrite']
    for mode in settings["mode"]:
        if mode in writemodes and not settings["destructive"]:
            print(f"\n Mode {mode} will overwrite data on {settings['target']} but destructive flag not set.\n")
            sys.exit(1)
        if mode in settings["mixed"] and not settings["rwmixread"]:
            print("\nIf a mixed (read/write) mode is specified, please specify --rwmixread\n")
            sys.exit(8)

    if settings["mixed"]:
        settings["loop_items"].append("rwmixread")

    if settings["remote"]:
        hostlist = os.path.expanduser(settings["remote"])
        settings["remote"] = hostlist
        if not os.path.exists(hostlist):
            print(f"The list of remote hosts ({hostlist}) doesn't seem to exist.\n")
            sys.exit(5)

    if settings["precondition_template"] and not os.path.exists(settings["precondition_template"]):
        print(f"Precondition template ({settings['precondition_template']}) doesn't seem to exist.\n")
        sys.exit(5)

    if not settings["precondition"]:
        settings["filter_items"].append("precondition_template")

    if settings["loops"] == 0:
        print("setting loops to 0 is likely not what you want as no benchmarks would be run\n")
        print("If you want to change the precondition loop count, edit precondition.fio or supply your own config\n")
        print("with the parameter --precondition-template")
        sys.exit(6)
