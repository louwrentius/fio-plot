import numpy as np
import matplotlib.pyplot as plt
import pprint

from . import (
    supporting,
    shared_chart as shared,
    tables
)


def calculate_font_size(settings, x_axis):
    max_label_width = max(tables.get_max_width([x_axis], len(x_axis)))
    fontsize = 0
    #
    # This hard-coded font sizing is ugly but if somebody knows a better algorithm...
    #
    if settings["group_bars"]:
        if max_label_width > 10:
            fontsize = 6
        elif max_label_width > 15:
            fontsize = 5
        else:
            fontsize = 8
    else:
        if max_label_width > 18:
            fontsize = 5
        else:
            fontsize = 8
    return fontsize


def create_bars_and_xlabels(settings, data, ax1, ax3):

    return_data = {"ax1": None, "ax3": None, "rects1": None, "rects2": None}

    iops = data["y1_axis"]["data"]
    latency = np.array(data["y2_axis"]["data"], dtype=float)
    width = 0.9

    color_iops = "#a8ed63"
    color_lat = "#34bafa"

    if settings["group_bars"]:
        x_pos1 = np.arange(1, len(iops) + 1, 1)
        x_pos2 = np.arange(len(iops) + 1, len(iops) + len(latency) + 1, 1)

        rects1 = ax1.bar(x_pos1, iops, width, color=color_iops)
        rects2 = ax3.bar(x_pos2, latency, width, color=color_lat)

        x_axis = data["x_axis"] * 2
        ltest = np.arange(1, len(x_axis) + 1, 1)

    else:
        x_pos = np.arange(0, (len(iops) * 2), 2)

        rects1 = ax1.bar(x_pos, iops, width, color=color_iops)
        rects2 = ax3.bar(x_pos + width, latency, width, color=color_lat)

        x_axis = data["x_axis"]
        ltest = np.arange(0.45, (len(iops) * 2), 2)

    ax1.set_ylabel(data["y1_axis"]["format"])
    ax3.set_ylabel(data["y2_axis"]["format"])
    ax1.set_xlabel(settings["label"])
    ax1.set_xticks(ltest)

    if settings["graphtype"] == "compare_graph":
        fontsize = calculate_font_size(settings, x_axis)
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    else:
        ax1.set_xticklabels(labels=x_axis)

    return_data["rects1"] = rects1
    return_data["rects2"] = rects2
    return_data["ax1"] = ax1
    return_data["ax3"] = ax3

    return return_data


def chart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for drawing iops/latency bars for a
    particular iodepth."""
    dataset_types = shared.get_dataset_types(dataset)
    #pprint.pprint(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types)
    # pprint.pprint(data)
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    #
    # Puts in the credit source (often a name or url)
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax1)

    ax2.axis("off")

    return_data = create_bars_and_xlabels(settings, data, ax1, ax3)

    rects1 = return_data["rects1"]
    rects2 = return_data["rects2"]
    ax1 = return_data["ax1"]
    ax3 = return_data["ax3"]

    #
    # Set title
    settings["type"] = ""
    settings[settings["query"]] = dataset_types[settings["query"]]
    if settings["rw"] == "randrw":
        supporting.create_title_and_sub(
            settings,
            plt,
            bs=data["bs"][0],
            skip_keys=[settings["query"]],
        )
    else:
        supporting.create_title_and_sub(
            settings,
            plt,
            bs=data["bs"][0],
            skip_keys=[settings["query"], "filter"],
        )
    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    shared.autolabel(rects2, ax3)
    #
    # Draw the standard deviation table
    tables.create_stddev_table(settings, data, ax2)
    #
    # Draw the cpu usage table if requested
    # pprint.pprint(data)

    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2)

    #
    # Create legend
    ax2.legend(
        (rects1[0], rects2[0]),
        (data["y1_axis"]["format"], data["y2_axis"]["format"]),
        loc="center left",
        frameon=False,
    )
    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)


def compchart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for creating bar charts that compare data."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set_improved(settings, dataset, dataset_types)
    
    # pprint.pprint(data)

    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    #
    # Puts in the credit source (often a name or url)
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax1)

    ax2.axis("off")

    return_data = create_bars_and_xlabels(settings, data, ax1, ax3)
    rects1 = return_data["rects1"]
    rects2 = return_data["rects2"]
    ax1 = return_data["ax1"]
    ax3 = return_data["ax3"]
    #
    # Set title
    settings["type"] = ""
    settings["iodepth"] = dataset_types["iodepth"]
    if settings["rw"] == "randrw":
        supporting.create_title_and_sub(settings, plt, skip_keys=["iodepth"])
    else:
        supporting.create_title_and_sub(settings, plt, skip_keys=[])

    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    shared.autolabel(rects2, ax3)

    tables.create_stddev_table(settings, data, ax2)

    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2)

    # Create legend
    ax2.legend(
        (rects1[0], rects2[0]),
        (data["y1_axis"]["format"], data["y2_axis"]["format"]),
        loc="center left",
        frameon=False,
    )

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)
