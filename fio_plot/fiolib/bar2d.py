import numpy as np
import matplotlib.pyplot as plt
import pprint

from . import (
    supporting,
    shared_chart as shared,
    tables,
    table_support as ts
)

def format_hostname_labels(settings, data):
    labels = []
    counter = 1
    hostcounter = 0 
    divide = int(len(data["hostname_series"]) / len(data["x_axis"])) # that int convert should work
    for host in data["hostname_series"]:
        hostcounter += 1
        attr = data["x_axis"][counter-1]
        labels.append(f"{host}\n{settings['graphtype'][-2:]} {attr}")
        if hostcounter % divide == 0:
            counter += 1
    return labels

def set_max_yaxis(settings, axes):
    for ax in axes:
        if ax.get_ylabel() == "IOPS":
            if settings["max_iops"]:
                ax.set_ylim(settings["min_iops"],settings["max_iops"])
        if "Latency" in ax.get_ylabel():
            if settings["max_lat"]:
                ax.set_ylim(settings["min_lat"],settings["max_lat"])

def calculate_font_size(settings, x_axis):
    max_label_width = max(ts.get_max_width([x_axis], len(x_axis)))
    #print(max_label_width)
    fontsize = 0
    #
    # This hard-coded font sizing is ugly but if somebody knows a better algorithm...
    #
    cols = len(x_axis)
    if settings["group_bars"]:
        if max_label_width >= 10:
            fontsize = 6
        else:
            fontsize = 8
    else:
        if max_label_width >= 10 and cols > 8:
            fontsize = 6
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

        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                x_axis = format_hostname_labels(settings, data)
        ltest = np.arange(0.45, (len(iops) * 2), 2)

    ax1.set_ylabel(data["y1_axis"]["format"])
    ax3.set_ylabel(data["y2_axis"]["format"])
    ax1.set_xlabel(settings["label"])
    ax1.set_xticks(ltest)

    set_max_yaxis(settings, [ax1, ax3])
    
    fontsize = calculate_font_size(settings, x_axis)
    #print(fontsize)
    if settings["graphtype"] == "compare_graph":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    elif settings["graphtype"] == "bargraph2d_qd" or settings["graphtype"] == "bargraph2d_nj":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize,)
    else:
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize, rotation=-50)

    return_data["rects1"] = rects1
    return_data["rects2"] = rects2
    return_data["ax1"] = ax1
    return_data["ax3"] = ax3
    return_data["fontsize"] = fontsize
    return return_data


def chart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for drawing iops/latency bars for a
    particular iodepth."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types)
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)
    plt.margins(x=0.01)
    #
    # Puts in the credit source (often a name or url)
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax2)

    ax2.axis("off")

    return_data = create_bars_and_xlabels(settings, data, ax1, ax3)

    rects1 = return_data["rects1"]
    rects2 = return_data["rects2"]
    ax1 = return_data["ax1"]
    ax3 = return_data["ax3"]
    fontsize = return_data["fontsize"]

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
    if settings["show_data"]:
        tables.create_values_table(settings, data, ax2, fontsize)
    else:
        tables.create_stddev_table(settings, data, ax2, fontsize)
    
    #
    # Draw the cpu usage table if requested
    # pprint.pprint(data)
    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2, fontsize)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2, fontsize)

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
    plt.margins(x=0.01)

    #
    # Puts in the credit source (often a name or url)
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax2)

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
    fontsize = calculate_font_size(settings, data["x_axis"])

    if settings["show_data"]:
        tables.create_values_table(settings, data, ax2, fontsize)
    else:
        tables.create_stddev_table(settings, data, ax2, fontsize)

    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2, fontsize)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2, fontsize)

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
