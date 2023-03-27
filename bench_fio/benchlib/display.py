#!/usr/bin/env python3
import datetime
import os
from . import argparsing as argp


def parse_settings_for_display(settings):
    """
    We are focussing here on making the length of the top/down bars match the length of the data rows.
    """
    data = {}
    max_length = 0
    action = {list: lambda a: " ".join(map(str, a)), str: str, int: str, bool: str}
    for k, v in settings.items():
        if v:
            if k not in settings["filter_items"]:
                if k in settings["basename_list"]:
                    data[str(k)] = os.path.basename(v)
                else:
                    data[str(k)] = action[type(v)](v)
                length = len(data[k])
                if length > max_length:
                    max_length = length
    data["length"] = max_length
    return data

def calculate_duration(settings, tests):
    number_of_tests = len(tests) * settings["loops"]
    time_per_test = settings["runtime"]
    if time_per_test:
        duration_in_seconds = number_of_tests * time_per_test
        duration = str(datetime.timedelta(seconds=duration_in_seconds))
    else:
        duration = None
    return duration

def print_header(settings, ds):
    print(f"{ds['blockchar']}" * (ds['fl'] + ds['width']))
    print((" " * int(ds['width'] / 2)) + ds['header'])
    print(f"-" * (ds['fl'] + ds['width']))
    if settings["dry_run"]:
        print()
        print(" ====---> WARNING - DRY RUN <---==== ")
        print()

def print_duration(settings, tests, ds):
    fl = ds["fl"]
    duration = calculate_duration(settings, tests)
    if duration:
        estimated = "Estimated duration"
        print(f"{estimated:<{fl}}: {duration:<}")
    else:
        print(f"Unable to estimate runtime (not an error)")

def print_options(settings, ds):
    data = ds["data"]
    fl = ds["fl"]
    descriptions = argp.get_argument_description()
    for item in settings.keys():
        if item not in settings["filter_items"]: # filter items are internal options that aren't relevant
            if item not in descriptions.keys(): 
                customitem = item + "*"  # These are custom fio options so we mark them as such
                print(f"{customitem:<{fl}}: {data[item]:<}")
            else:
                description = descriptions[item]
                if item in data.keys():
                    print(f"{description:<{fl}}: {data[item]:<}")
                else:
                    if settings[item]:
                        print(f"{description}:<{fl}: {settings[item]:<}")

def get_display_settings(settings, tests):
    data = parse_settings_for_display(settings)
    header = "+++ FIO BENCHMARK SCRIPT +++"
    fl = 30
    length = data["length"]
    displaysettings = {
        "header": header,
        "blockchar": "\u2588",
        "data": data,
        "fl": fl,  # Width of left column of text
        "length": length,
        "width": length + fl - len(header) 
    }
    return displaysettings

def print_footer(ds):
    print(f"-" * (ds['fl'] + ds['width']))
    print(f"{ds['blockchar']}" * (ds['fl'] + ds['width']))

def display_header(settings, tests):
    ds = get_display_settings(settings, tests)
    print_header(settings, ds)
    print_duration(settings, tests, ds)
    print_options(settings, ds)
    print_footer(ds)
    