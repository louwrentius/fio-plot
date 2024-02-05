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
    settings["output"] = os.path.expanduser(settings["output"])
    if benchmark["mode"] in settings["mixed"]:
        directory = (
            f"{settings['output']}/{os.path.basename(benchmark['target_base'])}/"
            f"{benchmark['mode']}{benchmark['rwmixread']}/{benchmark['block_size']}"
        )
    else:
        directory = f"{settings['output']}/{os.path.basename(benchmark['target_base'])}/{benchmark['block_size']}"

    if "run" in benchmark.keys():
        directory = directory + f"/run-{benchmark['run']}"

    return directory

def import_fio_template(template):
    config = configparser.ConfigParser()
    config.read(template)
    return config
