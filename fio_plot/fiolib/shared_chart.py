import pprint
import sys

from operator import itemgetter
import re
from . import(
    supporting,
    dataimport
)

def get_dataset_types(dataset):
    """This code is probably insane.
    Using only the first item in a list to return because all items should be equal.
    If not, a warning is displayed.
    """
    dataset_types = {"rw": set(), "iodepth": set(), "numjobs": set()}
    operation = {"rw": str, "iodepth": int, "numjobs": int}

    type_list = []

    for item in dataset:
        temp_dict = dataset_types.copy()
        for x in dataset_types.keys():
            for y in item["data"]:
                temp_dict[x].add(operation[x](y[x]))
            temp_dict[x] = sorted(temp_dict[x])
        if len(type_list) > 0:
            tmp = type_list[len(type_list) - 1]
            if tmp != temp_dict:
                print(
                    "Warning: benchmark data may not contain the same kind of data, comparisons may be impossible."
                )
        type_list.append(temp_dict)
    # pprint.pprint(type_list)
    dataset_types = type_list[0]
    return dataset_types


def get_record_set_histogram(settings, dataset):
    rw = settings["rw"]
    iodepth = int(settings["iodepth"][0])
    numjobs = int(settings["numjobs"][0])

    # pprint.pprint(dataset[0])

    # fio_version = dataset["data"]["fio version"]

    record_set = {
        "iodepth": iodepth,
        "numjobs": numjobs,
        "data": None,
        "fio_version": None,
    }

    for record in dataset[0]["data"]:
        if (
            (int(record["iodepth"]) == iodepth)
            and (int(record["numjobs"]) == numjobs)
            and record["rw"] == rw
        ):
            record_set["data"] = record
            record_set["fio_version"] = record["fio_version"]
            return record_set

def validate_get_record_set(settings, mismatch, dataset):
    if mismatch == len(dataset):
        print(f"\n   It seems that none of the data matched your selection criteria.\n \
    Check the filenames of the JSON files check the following parameters \n \
    -r {settings['rw']}  -d {settings['iodepth']} -n {settings['numjobs']}\n")
        print("\nIf you think everything is correct, feel free to report a bug.\n")
        sys.exit(1)

def get_record_set_3d(settings, dataset, dataset_types, rw, metric):
    mismatch = 0
    record_set = {
        "iodepth": dataset_types["iodepth"],
        "numjobs": dataset_types["numjobs"],
        "values": [],
        "fio_version": [],
    }
    # pprint.pprint(dataset)
    if settings["rw"] == "randrw":
        if len(settings["filter"]) > 1 or not settings["filter"]:
            print(
                "Since we are processing randrw data, you must specify a "
                "filter for either read or write data, not both."
            )
            exit(1)

    for depth in dataset_types["iodepth"]:
        row = []
        for jobs in dataset_types["numjobs"]:
            for record in dataset[0]["data"]:
                # pprint.pprint(record)
                if (
                    (int(record["iodepth"]) == int(depth))
                    and int(record["numjobs"]) == jobs
                    and record["rw"] == rw
                    and record["type"] in settings["filter"]
                ):
                    row.append(record[metric])
                else:
                    mismatch+=1    
        record_set["values"].append(supporting.round_metric_series(row))
    record_set["fio_version"].append(dataset[0]["data"][0]["fio_version"])
    validate_get_record_set(settings, mismatch, dataset)
    return record_set

def get_record_set_improved(settings, dataset, dataset_types):
    """The supplied dataset, a list of flat dictionaries with data is filtered based
    on the parameters as set by the command line. The filtered data is also scaled and rounded.
    """
    mismatch = 0

    if settings["rw"] == "randrw" or settings["rw"] == "readwrite":
        if len(settings["filter"]) > 1 or not settings["filter"]:
            print(
                f"Since we are processing {settings['rw']} data, you must specify a"
                " filter for either read or write data, not both."
            )
            exit(1)

    labels = []
    # This is mostly for debugging purposes.
    for record in dataset:
        record["label"] = dataimport.return_folder_name(record["directory"], settings)
        labels.append(record["label"])

    datadict = {
        "fio_version": [],
        "iops_series_raw": [],
        "iops_stddev_series_raw": [],
        "lat_series_raw": [],
        "lat_stddev_series_raw": [],
        "cpu": {"cpu_sys": [], "cpu_usr": []},
        "x_axis": labels,
        "y1_axis": None,
        "y2_axis": None,
    }

    depth = settings["iodepth"][0]
    numjobs = settings["numjobs"][0]
    rw = settings["rw"]
    for depth in dataset_types["iodepth"]:
        for data in dataset:
            # pprint.pprint(data.keys())
            # pprint.pprint(data['directory'])
            for record in data["data"]:
                #pprint.pprint(record.keys())
                #pprint.pprint(f"-> {record['type']}")
                #print(f"{depth} - {record['iodepth']} + {numjobs} - {record['numjobs']} + {record['rw']} + {record['type']}")
                #print(f"{settings['filter']}") 
                if (
                    (int(record["iodepth"]) == int(depth))
                    and int(record["numjobs"]) == int(numjobs)
                    and record["rw"] == rw
                    and record["type"] in settings["filter"]
                ):
                    datadict["fio_version"].append(record["fio_version"])
                    datadict["iops_series_raw"].append(record["iops"])
                    datadict["lat_series_raw"].append(record["lat"])
                    datadict["iops_stddev_series_raw"].append(record["iops_stddev"])
                    datadict["lat_stddev_series_raw"].append(record["lat_stddev"])
                    datadict["cpu"]["cpu_sys"].append(int(round(record["cpu_sys"], 0)))
                    datadict["cpu"]["cpu_usr"].append(int(round(record["cpu_usr"], 0)))
                else:
                    mismatch+=1

    validate_get_record_set(settings, mismatch, dataset)
    return scale_data(datadict)


def get_record_set(settings, dataset, dataset_types):
    """The supplied dataset, a list of flat dictionaries with data is filtered based
    on the parameters as set by the command line. The filtered data is also scaled and rounded.
    """
    dataset = dataset[0]
    rw = settings["rw"]
    numjobs = settings["numjobs"]
    mismatch = 0

    if settings["rw"] == "randrw":
        if len(settings["filter"]) > 1 or not settings["filter"]:
            print(
                "Since we are processing randrw data, you must specify a filter for either"
                "read or write data, not both."
            )
            exit(1)

    labels = dataset_types[settings["query"]]

    datadict = {
        "fio_version": [],
        "iops_series_raw": [],
        "iops_stddev_series_raw": [],
        "lat_series_raw": [],
        "lat_stddev_series_raw": [],
        "cpu": {"cpu_sys": [], "cpu_usr": []},
        "bs": [],
        "x_axis": labels,
        "y1_axis": None,
        "y2_axis": None,
        "numjobs": numjobs,
        "ss_settings": [],
        "ss_attained": [],
        "ss_data_bw_mean": [],
        "ss_data_iops_mean": [],
    }

    newlist = sorted(dataset["data"], key=itemgetter(settings["query"]))

    for record in newlist:
        for x in settings["iodepth"]:
            for y in settings["numjobs"]:
                #print(f"{x} - {record['iodepth']} + {y} - {record['numjobs']} + {record['rw']} + {record['type']}")
                #print(f"{settings['filter']}") 
                
                if (
                    (int(record["iodepth"]) == int(x))
                    and int(record["numjobs"]) == int(y)
                    and record["rw"] == rw
                    and record["type"] in settings["filter"]
                ):
                    datadict["fio_version"].append(record["fio_version"])
                    datadict["iops_series_raw"].append(record["iops"])
                    datadict["lat_series_raw"].append(record["lat"])
                    datadict["iops_stddev_series_raw"].append(record["iops_stddev"])
                    datadict["lat_stddev_series_raw"].append(record["lat_stddev"])
                    datadict["bs"].append(record["bs"])
                    datadict["cpu"]["cpu_sys"].append(int(round(record["cpu_sys"], 0)))
                    datadict["cpu"]["cpu_usr"].append(int(round(record["cpu_usr"], 0)))

                    if "ss_attained" in record.keys():
                        if record["ss_settings"]:
                            datadict["ss_settings"].append(str(record["ss_settings"])),
                            datadict["ss_attained"].append(int(record["ss_attained"])),
                            datadict["ss_data_bw_mean"].append(
                                int(round(record["ss_data_bw_mean"], 0))
                            ),
                            datadict["ss_data_iops_mean"].append(
                                int(round(record["ss_data_iops_mean"], 0))
                            ),
                else:
                    mismatch+=1

    validate_get_record_set(settings, mismatch, dataset)
    return scale_data(datadict)


def scale_data(datadict):
    if not datadict['fio_version']:
        print(f"\n function scale_data did not receive any data\n")
        sys.exit(1)
    iops_series_raw = datadict["iops_series_raw"]
    iops_stddev_series_raw = datadict["iops_stddev_series_raw"]
    lat_series_raw = datadict["lat_series_raw"]
    lat_stddev_series_raw = datadict["lat_stddev_series_raw"]
    cpu_usr = datadict["cpu"]["cpu_usr"]
    cpu_sys = datadict["cpu"]["cpu_sys"]

    if "ss_settings" in datadict.keys():
        ss_data_bw_mean = datadict["ss_data_bw_mean"]
        ss_data_iops_mean = datadict["ss_data_iops_mean"]

    #
    # Latency data must be scaled, IOPs will not be scaled.
    #
    
    latency_scale_factor = supporting.get_scale_factor_lat(lat_series_raw)
    scaled_latency_data = supporting.scale_yaxis(lat_series_raw, latency_scale_factor)
    #
    # Latency data must be rounded.
    #
    scaled_latency_data_rounded = supporting.round_metric_series(
        scaled_latency_data["data"]
    )
    scaled_latency_data["data"] = scaled_latency_data_rounded
    #
    # Latency stddev must be scaled with same scale factor as the data
    #
    lat_stdev_scaled = supporting.scale_yaxis(
        lat_stddev_series_raw, latency_scale_factor
    )

    lat_stdev_scaled_rounded = supporting.round_metric_series(lat_stdev_scaled["data"])

    #
    # Latency data is converted to percent.
    #
    lat_stddev_percent = supporting.raw_stddev_to_percent(
        scaled_latency_data["data"], lat_stdev_scaled_rounded
    )

    lat_stddev_percent = [int(x) for x in lat_stddev_percent]

    scaled_latency_data["stddev"] = supporting.round_metric_series(lat_stddev_percent)
    #
    # IOPS data is rounded
    iops_series_rounded = supporting.round_metric_series(iops_series_raw)
    #
    # IOPS stddev is converted to percent
    iops_stdev_rounded = supporting.round_metric_series(iops_stddev_series_raw)
    iops_stdev_rounded_percent = supporting.raw_stddev_to_percent(
        iops_series_rounded, iops_stdev_rounded
    )
    iops_stdev_rounded_percent = [int(x) for x in iops_stdev_rounded_percent]
    #
    #

    # Steady state bandwidth data must be scaled.
    if "ss_settings" in datadict.keys():
        if datadict["ss_settings"]:
            ss_bw_scalefactor = supporting.get_scale_factor_bw_ss(ss_data_bw_mean)
            ss_data_bw_mean = supporting.scale_yaxis(ss_data_bw_mean, ss_bw_scalefactor)
            ss_data_bw_mean["data"] = supporting.round_metric_series(
                ss_data_bw_mean["data"]
            )

            ss_iops_scalefactor = supporting.get_scale_factor_iops(ss_data_iops_mean)
            ss_data_iops_mean = supporting.scale_yaxis(
                ss_data_iops_mean, ss_iops_scalefactor
            )
            ss_data_iops_mean["data"] = supporting.round_metric_series(
                ss_data_iops_mean["data"]
            )

    datadict["y1_axis"] = {
        "data": iops_series_rounded,
        "format": "IOPS",
        "stddev": iops_stdev_rounded_percent,
    }

    datadict["y2_axis"] = scaled_latency_data
    if cpu_sys and cpu_usr:
        datadict["cpu"] = {"cpu_sys": cpu_sys, "cpu_usr": cpu_usr}

    if "ss_settings" in datadict.keys():
        if datadict["ss_settings"]:
            datadict["ss_data_bw_mean"] = ss_data_bw_mean
            datadict["ss_data_iops_mean"] = ss_data_iops_mean

    return datadict


def autolabel(rects, axis):
    for rect in rects:
        height = rect.get_height()
        if height < 10:
            formatter = "%.2f"
        else:
            formatter = "%d"
        value = rect.get_x()

        if height >= 10000:
            value = int(round(height / 1000, 0))
            formatter = "%dK"
        else:
            value = height

        axis.text(
            rect.get_x() + rect.get_width() / 2,
            1.015 * height,
            formatter % value,
            ha="center",
            fontsize=8,
        )
