#!/usr/bin/env python3
import configparser
from . import (defaultsettings, checks)

def write_fio_job_file(settings, parser):
    try:
        with open(f"{settings['tmpjobfile']}", 'w') as configfile:
            parser.write(configfile, space_around_delimiters=False)
    except IOError:
        print(f"Failed to write temporary Fio job file at {settings['tmpjobfile']}")

def filter_options(settings, config, mapping, benchmark, output_directory):
    boolean = {"True": 1, "False": 0}
    config['FIOJOB'] = {}
    for k,v in settings.items():
        key = k
        value = v
        if key in settings["loop_items"]:
            value = benchmark[k]
        if key in mapping.keys():
            key = mapping[key]
        if isinstance(value, bool):
            value = boolean[str(value)]
        if settings["entire_device"] and key == "runtime":
            continue
        if key == "type":
            devicetype = checks.check_target_type(benchmark["target"], settings)
            config['FIOJOB'][devicetype] = benchmark["target"]
        if value and not isinstance(value, list) and key not in settings["exclude_list"]:
            config['FIOJOB'][key] = str(value)
    config['FIOJOB']["write_bw_log"] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    config['FIOJOB']["write_lat_log"] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    config['FIOJOB']["write_iops_log"] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    return config

def generate_fio_job_file(settings, benchmark, output_directory):
    config = configparser.ConfigParser()
    mapping = defaultsettings.map_settings_to_fio()
    config = filter_options(settings, config, mapping, benchmark, output_directory)
    write_fio_job_file(settings, config)


