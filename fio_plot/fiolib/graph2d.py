#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from matplotlib.font_manager import FontProperties
import fiolib.supporting as supporting
import fiolib.dataimport as logdata
import fiolib.graph2dsupporting as support2d
import pprint


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
    if settings["colors"]:
        support2d.validate_colors(settings["colors"])

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

    supportdata = {
        "lines": [],
        "labels": [],
        "colors": support2d.get_colors(settings),
        "marker_list": list(markers.MarkerStyle.markers.keys()),
        "fontP": FontProperties(family="monospace"),
        "maximum": supporting.get_highest_maximum(settings, data),
        "axes": axes,
        "host": host,
        "maxlabelsize": support2d.get_max_label_size(settings, data, directories),
        "directories": directories,
    }

    supportdata["fontP"].set_size("xx-small")

    #
    # Converting the data and drawing the lines
    #
    for item in data["dataset"]:
        for rw in settings["filter"]:
            if rw in item.keys():
                support2d.drawline(settings, item, rw, supportdata)

    #
    # Generating the legend
    #
    values, ncol = support2d.generate_labelset(settings, supportdata)

    host.legend(
        supportdata["lines"],
        values,
        prop=supportdata["fontP"],
        bbox_to_anchor=(0.5, -0.18),
        loc="upper center",
        ncol=ncol,
        frameon=False,
    )

    def get_axis_for_label(axes):
        axis = list(axes.keys())[0]
        ax = axes[axis]
        return ax

    #
    # A ton of work to get the Fio-version from .json output if it exists.
    #
    jsondata = support2d.get_json_data(settings)
    if jsondata[0]["data"] and not settings["disable_fio_version"]:
        fio_version = jsondata[0]["data"][0]["fio_version"]
        ax = get_axis_for_label(axes)
        supporting.plot_fio_version(settings, fio_version, plt, ax, -0.12)

    #
    # Print source
    #
    ax = get_axis_for_label(axes)
    supporting.plot_source(settings, plt, ax, -0.12)

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)
