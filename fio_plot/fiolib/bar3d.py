import sys
import numpy as np
import matplotlib.pyplot as plt

# import pprint
import matplotlib as mpl
import pprint

from matplotlib import cm
from . import (
    supporting,
    shared_chart as shared
)


def plot_3d(settings, dataset):
    """This function is responsible for plotting the entire 3D plot."""

    if not settings["type"]:
        print("The type of data must be specified with -t (iops/lat/bw).")
        exit(1)

    dataset_types = shared.get_dataset_types(dataset)
    metric = settings["type"][0]
    rw = settings["rw"]
    iodepth = dataset_types["iodepth"]
    numjobs = dataset_types["numjobs"]
    data = shared.get_record_set_3d(settings, dataset, dataset_types, rw, metric)

    fig = plt.figure()
    ax1 = fig.add_subplot(projection="3d", elev=25)
    fig.set_size_inches(15, 10)
    ax1.set_box_aspect((4, 4, 3), zoom=1.2)

    lx = len(dataset_types["iodepth"])
    ly = len(dataset_types["numjobs"])

    # This code is meant to make the 3D chart to honour the maxjobs and
    # the maxdepth command line settings. It won't win any prizes for sure.
    if settings["maxjobs"]:
        numjobs = [x for x in numjobs if x <= settings["maxjobs"]]
        ly = len(numjobs)
    if settings["maxdepth"]:
        iodepth = [x for x in iodepth if x <= settings["maxdepth"]]
        lx = len(iodepth)
        if not iodepth:
            print(
                f"\nDefault maximum iodepth {settings['maxdepth']} is lower than specified iops {settings['iodepth']}."
            )
            print(
                "\nPlease specify a higher maximum iodepth for the graph with -M <iodepth> like '-M 512'\n"
            )
            sys.exit(1)
    if settings["maxjobs"] or settings["maxdepth"]:
        temp_x = []
        for item in data["values"]:
            if len(temp_x) < len(iodepth):
                temp_y = []
                for record in item:
                    if len(temp_y) < len(numjobs):
                        temp_y.append(record)
                temp_x.append(temp_y)
        data["iodepth"] = iodepth
        data["numjobs"] = numjobs
        data["values"] = temp_x

    # Ton of code to scale latency or bandwidth
    if metric == "lat" or metric == "bw":
        scale_factors = []
        for row in data["values"]:
            if metric == "lat":
                scale_factor = supporting.get_scale_factor_lat(row)
            if metric == "bw":
                scale_factor = supporting.get_scale_factor_bw(row)
            scale_factors.append(scale_factor)
        largest_scale_factor = supporting.get_largest_scale_factor(scale_factors)
        # pprint.pprint(largest_scale_factor)

        scaled_values = []
        for row in data["values"]:
            result = supporting.scale_yaxis(row, largest_scale_factor)
            scaled_values.append(result["data"])
        z_axis_label = largest_scale_factor["label"]

    else:
        scaled_values = data["values"]
        z_axis_label = metric

    n = np.array(scaled_values, dtype=float)

    if lx < ly:
        size = ly * 0.03  # thickness of the bar
    else:
        size = lx * 0.05  # thickness of the bar

    xpos_orig = np.arange(0, lx, 1)
    ypos_orig = np.arange(0, ly, 1)

    xpos = np.arange(0, lx, 1)
    ypos = np.arange(0, ly, 1)
    xpos, ypos = np.meshgrid(xpos - (size / lx), ypos - (size * (ly / lx)))

    xpos_f = xpos.flatten()  # Convert positions to 1D array
    ypos_f = ypos.flatten()

    zpos = np.zeros(lx * ly)

    # Positioning and sizing of the bars
    dx = size * np.ones_like(zpos)
    dy = size * (ly / lx) * np.ones_like(zpos)
    dz = n.flatten(order="F")
    values = dz / (dz.max() / 1)

    # Configure max value for z-axis
    if settings["max_z"]:
        ax1.set_zlim(0, settings["max_z"])
        cutoff_values = []
        warning = False
        for value in dz:
            if value < settings["max_z"]:
                cutoff_values.append(value)
            else:
                warning = True
                cutoff_values.append(settings["max_z"])
        dz = np.array(cutoff_values)
        if warning:
            print("Warning: z-axis values above ")
            warning_text = f"WARNING: values above {settings['max_z']} have been cutoff"
            fig.text(0.55, 0.85, warning_text)

    # Create the 3D chart with positioning and colors
    cmap = plt.get_cmap("rainbow", xpos.ravel().shape[0])
    colors = cm.rainbow(values)
    ax1.bar3d(xpos_f, ypos_f, zpos, dx, dy, dz, color=colors, zsort="max")

    # Create the color bar to the right
    norm = mpl.colors.Normalize(vmin=0, vmax=dz.max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    res = fig.colorbar(sm, fraction=0.046, pad=0.19, ax=ax1)
    res.ax.set_title(z_axis_label)

    # Set tics for x/y axis
    float_x = [float(x) for x in (xpos_orig)]

    ax1.w_xaxis.set_ticks(float_x)
    ax1.w_yaxis.set_ticks(ypos_orig)
    ax1.w_xaxis.set_ticklabels(iodepth)
    ax1.w_yaxis.set_ticklabels(numjobs)

    # axis labels
    fontsize = 16
    ax1.set_xlabel("iodepth", fontsize=fontsize)
    ax1.set_ylabel("numjobs", fontsize=fontsize)
    ax1.set_zlabel(z_axis_label, fontsize=fontsize)

    [t.set_verticalalignment("center_baseline") for t in ax1.get_yticklabels()]
    [t.set_verticalalignment("center_baseline") for t in ax1.get_xticklabels()]

    ax1.zaxis.labelpad = 25

    tick_label_font_size = 16
    for t in ax1.xaxis.get_major_ticks():
        t.label.set_fontsize(tick_label_font_size)

    for t in ax1.yaxis.get_major_ticks():
        t.label.set_fontsize(tick_label_font_size)

    ax1.zaxis.set_tick_params(pad=10)
    for t in ax1.zaxis.get_major_ticks():
        t.label.set_fontsize(tick_label_font_size)

    # title
    supporting.create_title_and_sub(
        settings,
        plt,
        skip_keys=["iodepth", "numjobs"],
        sub_x_offset=0.57,
        sub_y_offset=1.15,
    )

    # Source
    if settings["source"]:
        fig.text(0.65, 0.075, settings["source"], fontsize=settings["source_fontsize"])
    if not settings["disable_fio_version"]:
        fio_version = data["fio_version"][0]
        fig.text(
            0.05,
            0.075,
            f"Fio version: {fio_version}\nGraph generated by fio-plot",
            fontsize=settings["credit_fontsize"],
        )

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)
