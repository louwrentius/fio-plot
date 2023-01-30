#!/usr/bin/env python3
import sys
import os
import itertools
import configparser


def generate_test_list(settings):
    """All options that need to be tested are multiplied together.
    This creates a full list of all possible benchmark permutations that
    need to be run.
    """
    loop_items = settings["loop_items"]
    dataset = []

    for item in loop_items:
        result = settings[item]
        dataset.append(result)

    benchmark_list = list(itertools.product(*dataset))
    result = [dict(zip(loop_items, item)) for item in benchmark_list]
    settings["benchmarks"] = len(result)  # Augment display with extra sanity check
    return result


def convert_dict_vals_to_str(dictionary):
    """Convert dictionary to format in uppercase, suitable as env vars."""
    return {k.upper(): str(v) for k, v in dictionary.items()}


def make_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print(f"Failed to create {directory}")
        sys.exit(1)


def generate_output_directory(settings, benchmark):

    if benchmark["mode"] in settings["mixed"]:
        directory = (
            f"{settings['output']}/{os.path.basename(benchmark['target'])}/"
            f"{benchmark['mode']}{benchmark['rwmixread']}/{benchmark['block_size']}"
        )
    else:
        directory = f"{settings['output']}/{os.path.basename(benchmark['target'])}/{benchmark['block_size']}"

    if "run" in benchmark.keys():
        directory = directory + f"/run-{benchmark['run']}"

    return directory


def expand_command_line(command, settings, benchmark):
    if settings["size"]:
        command.append(f"--size={settings['size']}")

    if settings["runtime"] and not settings["entire_device"]:
        command.append(f"--runtime={settings['runtime']}")

    if settings["time_based"]:
        command.append("--time_based")

    if settings["rwmixread"] and benchmark["mode"] in settings["mixed"]:
        command.append(f"--rwmixread={benchmark['rwmixread']}")

    if settings["extra_opts"]:
        for option in settings["extra_opts"]:
            option = str(option)
            command.append("--" + option)

    if settings["ss"]:
        command.append(f"--steadystate={settings['ss']}")
        if settings["ss_dur"]:
            command.append(f"--ss_dur={settings['ss_dur']}")
        if settings["ss_ramp"]:
            command.append(f"--ss_ramp={settings['ss_ramp']}")

    return command


def import_fio_template(template):
    config = configparser.ConfigParser()
    config.read(template)
    return config
