#!/usr/bin/env python3
import datetime

import sys

from . import argparsing as argp


def parse_settings_for_display(settings):
    data = {}
    max_length = 0
    action = {list: lambda a: " ".join(map(str, a)), str: str, int: str, bool: str}
    for k, v in settings.items():
        if v:
            data[str(k)] = action[type(v)](v)
            length = len(data[k])
            if length > max_length:
                max_length = length
    data["length"] = max_length
    return data


def calculate_duration(settings, tests):
    number_of_tests = len(tests) * settings["loops"]
    time_per_test = int(settings["runtime"])
    duration_in_seconds = number_of_tests * time_per_test
    duration = str(datetime.timedelta(seconds=duration_in_seconds))
    return duration


def display_header(settings, tests):
    header = "+++ Fio Benchmark Script +++"
    blockchar = "\u2588"
    data = parse_settings_for_display(settings)
    fl = 30  # Width of left column of text
    length = data["length"]
    width = length + fl - len(header)
    duration = calculate_duration(settings, tests)
    print(f"{blockchar}" * (fl + width))
    print((" " * int(width / 2)) + header)
    print()
    if settings["dry_run"]:
        print()
        print(" ====---> WARNING - DRY RUN <---==== ")
        print()
    estimated = "Estimated duration"
    print(f"{estimated:<{fl}}: {duration:<}")
    descriptions = argp.get_argument_description()
    for item in settings.keys():
        if item not in settings["filter_items"]:
            description = descriptions[item]
            if item in data.keys():
                print(f"{description:<{fl}}: {data[item]:<}")
            else:
                if settings[item]:
                    print(f"{description}:<{fl}: {settings[item]:<}")
    print()
    print(f"{blockchar}" * (fl + width))
