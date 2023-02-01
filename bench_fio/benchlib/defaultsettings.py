#!/usr/bin/env python3
import os

def get_default_settings():
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    settings = {}
    settings["target"] = []
    settings["template"] = os.path.join(dir_path, "..", "templates", "fio-job-template.fio")
    settings["engine"] = "libaio"
    settings["mode"] = ["randread"]
    settings["iodepth"] = [1, 2, 4, 8, 16, 32, 64]
    settings["numjobs"] = [1, 2, 4, 8, 16, 32, 64]
    settings["block_size"] = ["4k"]
    settings["direct"] = 1
    settings["size"] = None
    settings["dry_run"] = False
    settings["precondition"] = False
    settings["quiet"] = False
    settings["output"] = False
    settings["precondition_template"] = os.path.join(dir_path, "..", "templates", "precondition.fio") 
    settings["precondition_repeat"] = False
    settings["entire_device"] = False
    settings["ss"] = False
    settings["ss_dur"] = None
    settings["ss_ramp"] = None
    settings["rwmixread"] = None
    settings["runtime"] = 60
    settings["loops"] = 1
    settings["time_based"] = False
    settings["extra_opts"] = []
    settings["loginterval"] = 1000
    settings["mixed"] = ["readwrite", "rw", "randrw"]
    settings["invalidate"] = 1
    settings["ceph_pool"] = None
    settings["destructive"] = False
    settings["remote"] = False
    settings["tmpjobfile"] = "/tmp/tmpjobfile.fio"
    settings["loop_items"] = [
        "target",
        "mode",
        "iodepth",
        "numjobs",
        "block_size",
    ]
    settings["filter_items"] = [
        "filter_items",
        "loop_items",
        "dry_run",
        "mixed",
        "quiet",
        "tmpjobfile",
        "exclude_list",
        "basename_list"
    ]
    ### The exclude list is used when generating temporary fio templates.
    settings["exclude_list"] = [
        "exclude_list",
        "loop_items",
        "filter_items",
        "precondition_template",
        "template",
        "target",
        "output",
        "remote",
        "tmpjobfile",
        "type",
        "benchmarks",
        "entire_device",
        "basename_list"
    ]
    settings["basename_list"] = [
        "template",
        "precondition_template"
    ]
    return settings

def map_settings_to_fio():
    mapping = {
        "mode": "rw",
        "engine": "ioengine",
        "block_size": "bs",
        "ss": "steadystate",
        "ss_dur": "steadystate_duration",
        "ss_ramp": "steadystate_ramp_time",
        "loginterval": "log_avg_msec",
        "ceph_pool": "pool"
    }
    return mapping
    