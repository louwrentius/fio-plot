import pprint as pprint
import sys
import statistics
import numpy as np
from datetime import datetime
from PIL.PngImagePlugin import PngImageFile, PngInfo
import random
import string


def running_mean(l, N):
    """From a list of values (N), calculate the running mean with a
    window of (l) items. How larger the value l is, the more smooth the graph.
    """
    sum = 0
    result = list(0 for x in l)

    for i in range(0, N):
        sum = sum + l[i]
        result[i] = sum / (i + 1)

    for i in range(N, len(l)):
        sum = sum - l[i - N] + l[i]
        result[i] = sum / N

    return result


def scale_xaxis_time(dataset):
    """FIO records log data time stamps in microseconds. To prevent huge numbers
    on the x-axis, the values are scaled to seconds, minutes or hours basedon the
    mean value of all data."""
    result = {"format": "Time (ms)", "data": dataset}
    mean = statistics.mean(dataset)

    if (mean > 1000) & (mean < 1000000):
        result["data"] = [x / 1000 for x in dataset]
        result["format"] = "Time (s)"
    if mean > 1000000:
        result["data"] = [x / 60000 for x in dataset]
        result["format"] = "Time (m)"
    if mean > 36000000:  # only switch to hours with enough datapoints (+10)
        result["data"] = [x / 3600000 for x in dataset]
        result["format"] = "Time (h)"
    return result


def get_scale_factor_lat(dataset):
    """The mean of the dataset is calculated. The size of the mean will determine
    which scale factor should be used on the data. The data is not scaled, only
    the scale factor and the y-axis label is returned in a dictionary.
    """
    try:
        mean = statistics.mean(dataset)
    except statistics.StatisticsError as e:
        print(f"\n Long story short, something went wrong: {e}\n")
        sys.exit(1)
        
    scale_factors = [
        {"scale": 1000000, "label": "Latency (ms)"},
        {"scale": 1000, "label": "Latency (\u03BCs)"},
        {"scale": 1, "label": "Latency (ns)"},
    ]
    for item in scale_factors:
        """Notice the factor, prevents scaling the graph up too soon if values
        are small, thus becomming almost unreadable"""
        if mean > item["scale"] * 5:
            return item

    # Fallback case when latency is very small 
    return scale_factors[-1]


def get_largest_scale_factor(scale_factors):
    """Based on multiple dataset, it is determined what the highest scale factor
    is. This assures that the values on the y-axis don't become too large.
    """
    return max([x for x in scale_factors if x], key=lambda x: x["scale"])


def scale_yaxis(dataset, scale):
    """The dataset supplied is scaled with the supplied scale. The scaled
    dataset is returned."""
    result = {}
    result["data"] = [x / scale["scale"] for x in dataset]
    result["format"] = scale["label"]
    return result


def get_scale_factor_iops(dataset):
    mean = statistics.mean(dataset)
    scale_factors = [
        {"scale": 1000000, "label": "M IOPs"},
        {"scale": 1000, "label": "K IOPs"},
        {"scale": 1, "label": "IOPs"},
    ]

    for item in scale_factors:
        if mean > item["scale"] * 5:
            return item

    # Fallback case when IOPS is very small 
    return scale_factors[-1]


def get_scale_factor_bw(dataset):
    mean = statistics.mean(dataset)
    scale_factors = [
        {"scale": 1048576, "label": "GB/s"},
        {"scale": 1024, "label": "MB/s"},
        {"scale": 1, "label": "KB/s"},
    ]

    for item in scale_factors:
        if mean > item["scale"] * 5:
            return item

    # Fallback case when BW is very small 
    return scale_factors[-1]


def get_scale_factor_bw_ss(dataset):
    mean = statistics.mean(dataset)
    scale_factors = [
        {"scale": 1073741824, "label": "GB/s"},
        {"scale": 1048576, "label": "MB/s"},
        {"scale": 1024, "label": "KB/s"},
        {"scale": 1, "label": "B/s"},
    ]

    for item in scale_factors:
        if mean > item["scale"] * 5:
            return item

    # Fallback case when BW (steady-state) is very small 
    return scale_factors[-1]


def lookupTable(metric):

    lookup = {
        "iops": {"ylabel": "IOPS", "label_pos": 0, "label_rot": "vertical"},
        "bw": {"ylabel": "Througput (KB/s)", "label_pos": -55, "label_rot": "vertical"},
        "lat": {"ylabel": "LAT Latency (ms)", "label_pos": 5, "label_rot": "vertical"},
        "slat": {
            "ylabel": "SLAT Latency (ms)",
            "label_pos": 5,
            "label_rot": "vertical",
        },
        "clat": {
            "ylabel": "CLAT Latency (ms)",
            "label_pos": 5,
            "label_rot": "vertical",
        },
    }
    return lookup[metric]


def generate_axes(ax, datatypes):

    axes = {}
    metrics = ["iops", "lat", "bw", "clat", "slat"]
    tkw = dict(size=4, width=1.5)
    first_not_used = True

    for item in metrics:
        if item in datatypes:
            if first_not_used:
                value = ax
                value.tick_params(axis="x", **tkw)
                first_not_used = False
                ax.grid(ls="dotted")
            else:
                value = ax.twinx()
                value.tick_params(axis="y", **tkw)
            axes[item] = value
            axes[item].ticklabel_format(style="plain")
            axes[f"{item}_pos"] = lookupTable(item)["label_pos"]
            if len(axes) == 6:
                axes[item].spines["right"].set_position(("axes", -0.16))
                break
    return axes


def round_metric(value):

    if value > 1:
        value = round(value, 2)
    if value <= 1:
        value = round(value, 3)
    if value >= 20:
        value = int(round(value, 0))
    return value


def round_metric_series(dataset):
    data = [round_metric(x) for x in dataset]
    return data


def raw_stddev_to_percent(values, stddev_series):
    result = []
    for x, y in zip(values, stddev_series):
        # pprint.pprint(f"{x} - {y}")
        try:
            percent = round((int(y) / int(x)) * 100, 0)
        except ZeroDivisionError:
            percent = 0
        result.append(percent)
    # pprint.pprint(result)
    return result


def process_dataset(settings, dataset):

    datatypes = []
    new_list = []
    new_structure = {"datatypes": None, "dataset": None}
    final_list = []
    scale_factors_bw = []
    scale_factors_lat = []

    """
    This first loop is to unpack the data in series and add scale the xaxis
    """
   
    for item in dataset:
        for rw in settings["filter"]:
            if len(item["data"][rw]) > 0:
                datatypes.append(item["type"])
                #pprint.pprint(item['data'][rw])
                unpacked = list(zip(*item["data"][rw]))
                
                item[rw] = {}

                item[rw]["xvalues"] = unpacked[0]
                item[rw]["yvalues"] = unpacked[1]

                scaled_xaxis = scale_xaxis_time(item[rw]["xvalues"])
                item["xlabel"] = scaled_xaxis["format"]
                item[rw]["xvalues"] = scaled_xaxis["data"]

                itemtype = []
                if isinstance(item["type"], str):
                    itemtype.append(item["type"])
                if isinstance(item["type"], list):
                    itemtype = item["type"]
                for x in itemtype:
                    if x == "lat":
                        scale_factors_lat.append(get_scale_factor_lat(item[rw]["yvalues"]))
                    if x == "bw":
                        scale_factors_bw.append(get_scale_factor_bw(item[rw]["yvalues"]))
        if settings["draw_total"] and len(settings["filter"]) == 2:
            readdata = item["read"]["yvalues"]
            writedata = item["write"]["yvalues"]
            item["total"] = {}
            item["total"]["yvalues"] = [x + y for x, y in zip(readdata, writedata)]
            item["total"]["xvalues"] = item["read"]["xvalues"] # hack
            if "lat" in item["type"]:
                scale_factors_lat.append(get_scale_factor_lat(item["total"]["yvalues"]))
            if "bw" in item["type"]:
                scale_factors_bw.append(get_scale_factor_bw(item["total"]["yvalues"]))
        
        item.pop("data")
        new_list.append(item)

    """
    This second loop assures that all data is scaled with the same factor
    """

    if len(scale_factors_lat) > 0:
        scale_factor_lat = get_largest_scale_factor(scale_factors_lat)
    if len(scale_factors_bw) > 0:
        scale_factor_bw = get_largest_scale_factor(scale_factors_bw)

    modi = settings["filter"]
    if settings["draw_total"] and len(settings["filter"]) == 2:
        modi.append("total")

    for item in new_list:
        for rw in modi:
            if rw in item.keys():
                if item["type"] == "lat":
                    scaled_data = scale_yaxis(item[rw]["yvalues"], scale_factor_lat)
                    item[rw]["ylabel"] = scaled_data["format"]
                    item[rw]["yvalues"] = scaled_data["data"]

                elif item["type"] == "bw":
                    scaled_data = scale_yaxis(item[rw]["yvalues"], scale_factor_bw)
                    item[rw]["ylabel"] = scaled_data["format"]
                    item[rw]["yvalues"] = scaled_data["data"]
                else:
                    item[rw]["ylabel"] = lookupTable(item["type"])["ylabel"]

                max = np.max(item[rw]["yvalues"])
                mean = np.mean(item[rw]["yvalues"])
                stdv = round((np.std(item[rw]["yvalues"]) / mean) * 100, 2)
                percentile = round(
                    np.percentile(item[rw]["yvalues"], settings["percentile"]), 2
                )

                if mean > 1:
                    mean = round(mean, 2)
                if mean <= 1:
                    mean = round(mean, 3)
                if mean >= 20:
                    mean = int(round(mean, 0))

                if percentile > 1:
                    percentile = round(percentile, 2)
                if percentile <= 1:
                    percentile = round(percentile, 3)
                if percentile >= 20:
                    percentile = int(round(percentile, 0))

                item[rw]["max"] = max
                item[rw]["mean"] = mean
                item[rw]["stdv"] = stdv
                item[rw]["percentile"] = percentile

        final_list.append(item)

    new_structure["datatypes"] = list(set(datatypes))
    new_structure["dataset"] = final_list
                    
    return new_structure


def get_highest_maximum(settings, data):
    highest_max = {
        "read": {"iops": 0, "lat": 0, "bw": 0},
        "write": {"iops": 0, "lat": 0, "bw": 0},
        "total": {"iops": 0, "lat": 0, "bw": 0 }
    }
    for item in data["dataset"]:
        for rw in settings["filter"]:
            if rw in item.keys():
                if item[rw]["max"] > highest_max[rw][item["type"]]:
                    highest_max[rw][item["type"]] = item[rw]["max"]
    
    for rw in settings["filter"]:
        for metric in highest_max[rw].keys():
            if highest_max[rw][metric] > highest_max["total"][metric]:
                highest_max["total"][metric] = highest_max[rw][metric] 

    return highest_max


def create_title_and_sub(
    settings, plt, bs=None, skip_keys=[], sub_x_offset=0, sub_y_offset=0
):
    #
    # Offset title/subtitle if there is a 3rd y-axis
    #
    number_of_types = len(settings["type"])
    y_offset = 1.02
    if number_of_types <= 2:
        x_offset = 0.5
    else:
        x_offset = 0.425

    if sub_x_offset > 0:
        x_offset = sub_x_offset
    if sub_y_offset > 0:
        y_offset = sub_y_offset

    #
    # plt.subtitle sets title and plt.title sets subtitle ....
    #
    plt.suptitle(settings["title"],fontsize=settings["title_fontsize"])
    subtitle = None
    sub_title_items = {
        "rw": settings["rw"],
        "iodepth": str(settings["iodepth"]).strip("[]"),
        "numjobs": str(settings["numjobs"]).strip("[]"),
        "type": str(settings["type"]).strip("[]").replace("'", ""),
        "filter": str(settings["filter"]).strip("[]").replace("'", ""),
    }

    if bs:
        sub_title_items.update({"bs": bs})

    if settings["subtitle"]:
        subtitle = settings["subtitle"]
    else:
        temporary_string = "|"
        for key in sub_title_items.keys():
            if key not in skip_keys:
                if len(sub_title_items[key]) > 0:
                    temporary_string += f" {key} {sub_title_items[key]} |"
        subtitle = temporary_string

    plt.title(
        subtitle, fontsize=settings["subtitle_fontsize"], horizontalalignment="center", x=x_offset, y=y_offset
    )


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def plot_source(settings, plt, ax1, vertical=-0.08):
    if settings["source"]:
        calculation = len(settings["source"]) / 130
        horizontal = 1 - calculation
        align = "left"
        plot_text_line(
            settings["source"], plt, ax1, horizontal, align, vertical, fontsize=settings["source_fontsize"]
        )


def plot_fio_version(settings, value, plt, ax1, vertical=-0.08):
    if not settings["disable_fio_version"]:
        horizontal = 0
        align = "left"
        if value:
            text = f"Fio version: {value} - Graph generated with fio-plot"
        else:
            text = "Data generated by Fio, graph generated with Fio-plot"
        plot_text_line(text, plt, ax1, horizontal, align, vertical, fontsize=(int(settings["credit_fontsize"])-2))


def plot_text_line(value, plt, ax1, horizontal, align, vertical, fontsize=12):
    plt.text(
        horizontal,
        vertical,
        str(value),
        ha=align,
        va="top",
        transform=ax1.transAxes,
        fontsize=fontsize,
    )

def random_char(y):
    return "".join(random.choice(string.ascii_letters) for x in range(y))


def save_png(settings, plt, fig):
    now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    title = settings["title"].replace(" ", "-")
    title = title.replace("/", "-")
    plt.tight_layout(rect=[0, 0, 1, 1])
    random = random_char(2)
    if settings["output_filename"] is None or len(settings["output_filename"]) == 0:
        savename = f"{title}_{now}_{random}.png"
    else:
        savename = settings["output_filename"]
    print(f"\n Saving to file {savename}\n")
    fig.savefig(savename, dpi=settings["dpi"])
    write_png_metadata(savename, settings)


def write_png_metadata(filename, settings):
    targetImage = PngImageFile(filename)
    metadata = PngInfo()
    for (k, v) in settings.items():
        if type(v) == list:
            value = ""
            for item in v:
                value += str(item) + " "
            v = value
        if type(v) == bool:
            v = str(v)
        if v is None:
            continue
        else:
            metadata.add_text(k, str(v))
    targetImage.save(filename, pnginfo=metadata)
