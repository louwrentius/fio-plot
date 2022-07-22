import numpy as np
import matplotlib.pyplot as plt

# import pprint
from . import (
    shared_chart as shared,
    supporting
)

def sort_latency_keys(latency):
    """The FIO latency data has latency buckets and those are sorted ascending.
    The milisecond data has a >=2000 bucket which cannot be sorted in a 'normal'
    way, so it is just stuck on top. This function resturns a list of sorted keys.
    """
    placeholder = ""
    tmp = []
    for item in latency:
        if item == ">=2000":
            placeholder = ">=2000"
        else:
            tmp.append(item)

    tmp.sort(key=int)
    if placeholder:
        tmp.append(placeholder)
    return tmp


def sort_latency_data(latency_dict):
    """The sorted keys from the sort_latency_keys function are used to create
    a sorted list of values, matching the order of the keys."""
    keys = latency_dict.keys()
    values = {"keys": None, "values": []}
    sorted_keys = sort_latency_keys(keys)
    values["keys"] = sorted_keys
    for key in sorted_keys:
        values["values"].append(latency_dict[key])
    return values


def autolabel(rects, axis):
    """This function puts a value label on top of a 2d bar. If a bar is so small
    it's barely visible, if at all, the label is omitted."""
    fontsize = 6
    for rect in rects:
        height = rect.get_height()
        if height >= 1:
            axis.text(
                rect.get_x() + rect.get_width() / 2.0,
                1 + height,
                "{}%".format(int(height)),
                ha="center",
                fontsize=fontsize,
            )
        elif height > 0.4:
            axis.text(
                rect.get_x() + rect.get_width() / 2.0,
                1 + height,
                "{:3.2f}%".format(height),
                ha="center",
                fontsize=fontsize,
            )


def chart_latency_histogram(settings, dataset):
    """This function is responsible to draw the 2D latency histogram,
    (a bar chart)."""

    record_set = shared.get_record_set_histogram(settings, dataset)

    # We have to sort the data / axis from low to high
    sorted_result_ms = sort_latency_data(record_set["data"]["latency_ms"])
    sorted_result_us = sort_latency_data(record_set["data"]["latency_us"])
    sorted_result_ns = sort_latency_data(record_set["data"]["latency_ns"])

    # This is just to use easier to understand variable names
    x_series = sorted_result_ms["keys"]
    y_series1 = sorted_result_ms["values"]
    y_series2 = sorted_result_us["values"]
    y_series3 = sorted_result_ns["values"]

    # us/ns histogram data is missing 2000/>=2000 fields that ms data has
    # so we have to add dummy data to match x-axis size
    y_series2.extend([0, 0])
    y_series3.extend([0, 0])

    # Create the plot
    fig, ax1 = plt.subplots()
    fig.set_size_inches(10, 6)

    # Make the positioning of the bars for ns/us/ms
    x_pos = np.arange(0, len(x_series) * 3, 3)
    width = 1

    # how much of the IO falls in a particular latency class ns/us/ms
    coverage_ms = round(sum(y_series1), 2)
    coverage_us = round(sum(y_series2), 2)
    coverage_ns = round(sum(y_series3), 2)

    # Draw the bars
    rects1 = ax1.bar(x_pos, y_series1, width, color="r")
    rects2 = ax1.bar(x_pos + width, y_series2, width, color="b")
    rects3 = ax1.bar(x_pos + width + width, y_series3, width, color="g")

    # Configure the axis and labels
    ax1.set_ylabel("Percentage of I/O")
    ax1.set_xlabel("Latency")
    ax1.set_xticks(x_pos + width / 2)
    ax1.set_xticklabels(x_series)

    # Make room for labels by scaling y-axis up (max is 100%)
    ax1.set_ylim(0, 100 * 1.1)

    label_ms = "Latency in ms ({0:05.2f}%)".format(coverage_ms)
    label_us = "Latency in us  ({0:05.2f}%)".format(coverage_us)
    label_ns = "Latency in ns  ({0:05.2f}%)".format(coverage_ns)

    # Configure the title
    settings["type"] = ""
    supporting.create_title_and_sub(settings, plt, ["type", "filter"])
    # Configure legend
    ax1.legend(
        (rects1[0], rects2[0], rects3[0]),
        (label_ms, label_us, label_ns),
        frameon=False,
        loc="best",
    )

    # puts a percentage above each bar (ns/us/ms)
    autolabel(rects1, ax1)
    autolabel(rects2, ax1)
    autolabel(rects3, ax1)

    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, record_set["fio_version"], plt, ax1)

    supporting.save_png(settings, plt, fig)
