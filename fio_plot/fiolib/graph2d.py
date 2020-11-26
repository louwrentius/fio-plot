#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from matplotlib.font_manager import FontProperties
import fiolib.supporting as supporting

# from datetime import datetime
import fiolib.dataimport as logdata
import matplotlib.patches as mpatches


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def chart_2d_log_data(settings, dataset):
    #
    # Raw data must be processed into series data + enriched
    #
    data = supporting.process_dataset(settings, dataset)
    datatypes = data["datatypes"]
    directories = logdata.get_unique_directories(dataset)
    # pprint.pprint(data)
    #
    # Create matplotlib figure and first axis. The 'host' axis is used for
    # x-axis and as a basis for the second and third y-axis
    #
    fig, host = plt.subplots()
    fig.set_size_inches(9, 5)
    plt.margins(0)
    #
    # Generates the axis for the graph with a maximum of 3 axis (per type of
    # iops,lat,bw)
    #
    axes = supporting.generate_axes(host, datatypes)
    #
    # Create title and subtitle
    #
    supporting.create_title_and_sub(settings, plt)
    #
    # The extra offsets are requred depending on the size of the legend, which
    # in turn depends on the number of legend items.
    #
    extra_offset = (
        len(datatypes)
        * len(settings["iodepth"])
        * len(settings["numjobs"])
        * len(settings["filter"])
    )

    bottom_offset = 0.18 + (extra_offset / 120)
    if "bw" in datatypes and (len(datatypes) > 2):
        #
        # If the third y-axis is enabled, the graph is ajusted to make room for
        # this third y-axis.
        #
        fig.subplots_adjust(left=0.21)
        fig.subplots_adjust(bottom=bottom_offset)
    else:
        fig.subplots_adjust(bottom=bottom_offset)

    lines = []
    labels = []
    colors = supporting.get_colors()
    marker_list = list(markers.MarkerStyle.markers.keys())
    fontP = FontProperties(family="monospace")
    fontP.set_size("xx-small")

    maximum = supporting.get_highest_maximum(settings, data)

    for item in data["dataset"]:
        for rw in settings["filter"]:
            if rw in item.keys():
                if settings["enable_markers"]:
                    marker_value = marker_list.pop(0)
                else:
                    marker_value = None

                xvalues = item[rw]["xvalues"]
                yvalues = item[rw]["yvalues"]

                #
                # Use a moving average as configured by the commandline option
                # to smooth out the graph for better readability.
                #
                if settings["moving_average"]:
                    yvalues = supporting.running_mean(
                        yvalues, settings["moving_average"]
                    )
                #
                # PLOT
                #
                dataplot = f"{item['type']}_plot"
                axes[dataplot] = axes[item["type"]].plot(
                    xvalues,
                    yvalues,
                    marker=marker_value,
                    markevery=(len(yvalues) / (len(yvalues) * 10)),
                    color=colors.pop(0),
                    label=item[rw]["ylabel"],
                    linewidth=settings["line_width"],
                )[0]
                host.set_xlabel(item["xlabel"])
                #
                # Assure axes are scaled correctly, starting from zero.
                #
                factordict = {"iops": 1.05, "lat": 1.25, "bw": 1.5}

                #
                # Set minimum and maximum values for y-axis where applicable.
                #
                min_y = 0
                if settings["min_y"] == "None":
                    min_y = None
                else:
                    try:
                        min_y = int(settings["min_y"])
                    except ValueError:
                        print("Min_y value is invalid (not None or integer).")

                max_y = maximum[rw][item["type"]] * factordict[item["type"]]

                if settings[f"max_{item['type']}"]:
                    max_y = settings[f"max_{item['type']}"]

                axes[item["type"]].set_ylim(min_y, max_y)
                #
                # Label Axis
                #
                padding = axes[f"{item['type']}_pos"]
                axes[item["type"]].set_ylabel(item[rw]["ylabel"], labelpad=padding)
                #
                # Add line to legend
                #
                lines.append(axes[dataplot])
                maxlabelsize = get_max_label_size(settings, data, directories)
                # print(maxlabelsize)
                mylabel = create_label(settings, item, directories)
                mylabel = get_padding(mylabel, maxlabelsize)

                labelset = {
                    "name": mylabel,
                    "rw": rw,
                    "type": item["type"],
                    "qd": item["iodepth"],
                    "nj": item["numjobs"],
                    "mean": item[rw]["mean"],
                    "std%": item[rw]["stdv"],
                    f"P{settings['percentile']}": item[rw]["percentile"],
                }
                # pprint.pprint(labelset)
                labels.append(labelset)

    master_padding = {
        "name": 0,
        "rw": 5,
        "type": 4,
        "qd": 2,
        "nj": 2,
        "mean": 0,
        "std%": 0,
        f"P{settings['percentile']}": 0,
    }

    for label in labels:
        for key in label.keys():
            label_length = len(str(label[key]))
            master_length = master_padding[key]
            if label_length > master_length:
                master_padding[key] = label_length
                if label_length % 2 != 0:
                    master_padding[key] = master_padding[key] + 1

    red_patch = mpatches.Patch(color="white", label="Just filler")
    lines.insert(0, red_patch)
    header = ""

    values = []
    for item in labels:
        line = ""
        for key in item.keys():
            line += f"| {item[key]:>{master_padding[key]}} "
        values.append(line)

    for column in master_padding.keys():
        size = master_padding[column]
        header = f"{header}| {column:<{size}} "
    values.insert(0, header)

    ncol = 1
    if len(values) > 3:
        ncol = 2
        number = len(values)
        position = int(number / 2) + 1
        lines.insert(position, red_patch)
        values.insert(position, header)

    host.legend(
        lines,
        values,
        prop=fontP,
        bbox_to_anchor=(0.5, -0.18),
        loc="upper center",
        ncol=ncol,
        frameon=False,
    )
    #
    # Save graph to file (png)
    #
    if settings["source"]:
        axis = list(axes.keys())[0]
        ax = axes[axis]
        plt.text(
            1,
            -0.10,
            str(settings["source"]),
            ha="right",
            va="top",
            transform=ax.transAxes,
            fontsize=8,
            fontfamily="monospace",
        )
    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)


#
# These functions below is just one big mess to get the legend labels to align.
#


def create_label(settings, item, directories):
    mydir = f"{item['directory']}"
    return mydir


def get_max_label_size(settings, data, directories):
    labels = []
    for item in data["dataset"]:
        for rw in settings["filter"]:
            if rw in item.keys():
                label = create_label(settings, item, directories)
                labels.append(label)

    maxlabelsize = 0
    for label in labels:
        size = len(label)
        if size > maxlabelsize:
            maxlabelsize = size

    return maxlabelsize


def get_padding(label, maxlabelsize):
    size = len(label)
    diff = maxlabelsize - size
    if diff > 0:
        label = label + " " * diff
    return label
