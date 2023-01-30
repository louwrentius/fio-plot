#!/usr/bin/env python3
import os
import sys
import configparser
from pathlib import Path
from . import defaultsettings

def write_fio_job_file(settings, parser):
    try:
        with open(f"{settings['tmpjobfile']}", 'w') as configfile:
            parser.write(configfile, space_around_delimiters=False)
    except IOError:
        print(f"Failed to write temporary Fio job file at {settings['tmpjobfile']}")

def generate_fio_job_file(settings, benchmark, output_directory):
    mapping = defaultsettings.map_settings_to_fio()
    boolean = {"True": 1, "False": 0}
    config = configparser.ConfigParser()
    config['FIOJOB'] = {}
    config['FIOJOB']["write_bw_log"] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    config['FIOJOB']["write_lat_log"] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    config['FIOJOB']["write_iops_log"] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    for k,v in settings.items():
        key = k
        value = v
        if key in settings["loop_items"]:
            value = benchmark[k]
        if key in mapping.keys():
            key = mapping[key]
        if isinstance(value, bool):
            value = boolean[str(value)]
        if value and not isinstance(value, list) and key not in settings["exclude_list"]:
            config['FIOJOB'][key] = str(value)
    
    write_fio_job_file(settings, config)


