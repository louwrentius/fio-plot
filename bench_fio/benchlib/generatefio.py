#!/usr/bin/env python3
import configparser
from . import defaultsettings, checks


def write_fio_job_file(tmpjobfile, parser):
    try:
        with open(tmpjobfile, "w") as configfile:
            parser.write(configfile, space_around_delimiters=False)
    except IOError:
        print(f"Failed to write temporary Fio job file at tmpjobfile")


def filter_options(settings, config, mapping, benchmark, output_directory):
    boolean = {"True": 1, "False": 0}
    config["FIOJOB"] = {}
    for k, v in settings.items():
        key = k
        value = v
        if (
            key in settings["loop_items"]
        ):  # This is looping throught the benchmark parameters
            value = benchmark[k]
        if (
            key in mapping.keys()
        ):  # This is about translating bench-fio parameters to fio parameters
            key = mapping[key]
        if isinstance(value, bool):
            value = boolean[str(value)]
        if key == "type":  # we check if we target a file directory or block device
            devicetype = checks.check_target_type(benchmark["target_base"], settings)
            config["FIOJOB"][devicetype] = benchmark["target"]
        if (
            value
            and not isinstance(value, list)
            and key not in settings["exclude_list"]
        ):
            config["FIOJOB"][key] = str(value).replace(
                "%", "%%"
            )  # just add all key values, % character needs replacing
        if settings["extra_opts"]:
            for item in settings["extra_opts"]:
                key, value = item.split("=")
                config["FIOJOB"][key] = str(value)
        # print(f"key: {key} - Value: {value} - {type(value)}")

    config["FIOJOB"][
        "write_bw_log"
    ] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    config["FIOJOB"][
        "write_lat_log"
    ] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    config["FIOJOB"][
        "write_iops_log"
    ] = f"{output_directory}/{benchmark['mode']}-iodepth-{benchmark['iodepth']}-numjobs-{benchmark['numjobs']}"
    return config


def generate_fio_job_file(settings, benchmark, output_directory, tmpjobfile):
    config = configparser.ConfigParser()
    mapping = defaultsettings.map_settings_to_fio()
    config = filter_options(settings, config, mapping, benchmark, output_directory)
    write_fio_job_file(tmpjobfile, config)
