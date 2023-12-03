#!/usr/bin/env python3
import datetime
import os
from rich.style import Style
from rich.table import Table
from rich.console import Console
from rich.text import Text
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
    if settings["parallel"]:
        number_of_tests = number_of_tests/len(settings["target"])
    time_per_test = settings["runtime"]
    if time_per_test:
        duration_in_seconds = number_of_tests * time_per_test
        duration = str(datetime.timedelta(seconds=duration_in_seconds))
    else:
        duration = None
    return duration

def print_dryrun(settings, table):

    if settings["dry_run"]:
        table.add_row("Dry Run","True", style="bold green")

def get_duration(settings, tests):
    duration = calculate_duration(settings, tests)
    returnvalue = "Unable to estimate (not an error)"
    if duration:
        returnvalue = duration
    return returnvalue

def print_options(settings, table):
    descriptions = argp.get_argument_description()
    data = parse_settings_for_display(settings)
    for item in settings.keys():
        if item not in settings["filter_items"]: # filter items are internal options that aren't relevant
            if item not in descriptions.keys(): 
                customitem = item + "*"  # These are custom fio options so we mark them as such
                #print(f"{customitem:<{fl}}: {data[item]:<}")
                table.add_row(customitem, data[item])
            else:
                description = descriptions[item]
                if item in data.keys():
                    table.add_row(description, data[item])
                else:
                    if settings[item]:
                        table.add_row(description, data[item])


def display_header(settings, tests):
    
    duration = calculate_duration(settings, tests)
    table = Table(title="Bench-fio",title_style=Style(bgcolor="dodger_blue2",bold=True))
    table.add_column(no_wrap=True, header="Setting")
    table.add_column(no_wrap=True,justify="left", header="value")
    print_dryrun(settings, table)
    table.add_row("Estimated Duration",duration)
    print_options(settings, table)
    console = Console()
    console.print(table)    