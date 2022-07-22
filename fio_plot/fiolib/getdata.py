import pprint

from . import(
    dataimport as logdata,
    graph2d as graph,
    jsonimport,
    bar2d,
    bar3d,
    barhistogram as histogram
)


def configure_default_settings(settings, routing_dict, key):
    if not settings["iodepth"]:
        settings["iodepth"] = routing_dict[key]["iodepth_default"]
    if not settings["numjobs"]:
        settings["numjobs"] = routing_dict[key]["numjobs_default"]
    settings["query"] = routing_dict[key]["query"]
    settings["label"] = routing_dict[key]["label"]
    return settings


def get_log_data(settings):
    if not settings["iodepth"]:
        settings["iodepth"] = [1]
    if not settings["numjobs"]:
        settings["numjobs"] = [1]

    benchmarkfiles = []
    for input_dir in settings["input_directory"]:
        benchmarkfiles.extend(logdata.list_fio_log_files(input_dir))
    logfiles = logdata.filterLogFiles(settings, benchmarkfiles)
    # pprint.pprint(logfiles)
    rawdata = logdata.readLogDataFromFiles(settings, logfiles)
    # pprint.pprint(rawdata)
    merged = logdata.mergeDataSet(settings, rawdata)
    return merged


def get_json_data(settings):
    list_of_json_files = jsonimport.list_json_files(settings)
    # pprint.pprint(list_of_json_files)
    dataset = jsonimport.import_json_dataset(settings, list_of_json_files)
    parsed_data = jsonimport.get_flat_json_mapping(settings, dataset)
    # pprint.pprint(parsed_data)
    return parsed_data


def get_routing_dict():
    routing_dict = {
        "loggraph": {
            "function": graph.chart_2d_log_data,
            "get_data": get_log_data,
            "iodepth_default": [1],
            "numjobs_default": [1],
            "query": None,
            "label": None,
        },
        "bargraph3d": {
            "function": bar3d.plot_3d,
            "get_data": get_json_data,
            "iodepth_default": [1, 2, 4, 8, 16, 32, 64],
            "numjobs_default": [1, 2, 4, 8, 16, 32, 64],
            "query": None,
            "label": None,
        },
        "bargraph2d_qd": {
            "function": bar2d.chart_2dbarchart_jsonlogdata,
            "get_data": get_json_data,
            "iodepth_default": [1, 2, 4, 8, 16, 32, 64],
            "numjobs_default": [1],
            "query": "iodepth",
            "label": "Queue depth",
        },
        "bargraph2d_nj": {
            "function": bar2d.chart_2dbarchart_jsonlogdata,
            "get_data": get_json_data,
            "iodepth_default": [1],
            "numjobs_default": [1, 2, 4, 8, 16, 32, 64],
            "query": "numjobs",
            "label": "Number of jobs",
        },
        "histogram": {
            "function": histogram.chart_latency_histogram,
            "get_data": get_json_data,
            "iodepth_default": [1],
            "numjobs_default": [1],
            "query": None,
            "label": None,
        },
        "compare_graph": {
            "function": bar2d.compchart_2dbarchart_jsonlogdata,
            "get_data": get_json_data,
            "iodepth_default": [1],
            "numjobs_default": [1],
            "query": None,
            "label": None,
        },
    }
    return routing_dict
