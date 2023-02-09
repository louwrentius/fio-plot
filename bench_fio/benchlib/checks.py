#!/usr/bin/env python3
import shutil
import sys
import os
from pathlib import Path


def check_if_fio_exists():
    command = "fio"
    if shutil.which(command) is None:
        print("Fio executable not found in path. Is Fio installed?")
        print()
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

def check_target_type(target, filetype):
    """Validate path and file / directory type.
    It also returns the appropritate fio command line parameter based on the
    file type.

    In case of target type 'file' it will be created if it doesn't exist, which is fio default behaviour'.
    """

    keys = ["file", "device", "directory", "rbd"]

    test = {keys[0]: Path.is_file, keys[1]: Path.is_block_device, keys[2]: Path.is_dir}

    parameter = {keys[0]: "--filename", keys[1]: "--filename", keys[2]: "--directory"}

    if not filetype == "rbd":
        
        if filetype == "file":
            return parameter[filetype]

        if not os.path.exists(target):
            print(f"Benchmark target {filetype} {target} does not exist.")
            sys.exit(10)

        if filetype not in keys:
            print(f"Error, filetype {filetype} is an unknown option.")
            exit(123)

        check = test[filetype]

        path_target = Path(target)  # path library needs to operate on path object

        if check(path_target):
            return parameter[filetype]
        else:
            print(f"Target {filetype} {target} is not {filetype}.")
            sys.exit(10)
    else:
        return None
