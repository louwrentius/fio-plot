import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import sys
import pprint

from . import (
    jsonimport,
    supporting
)


#
# These functions below is just one big mess to get the legend labels to align.
#
def get_json_data(settings):
    list_of_json_files = jsonimport.list_json_files(settings, fail=False)
    if list_of_json_files:
        dataset = jsonimport.import_json_dataset(settings, list_of_json_files)
        parsed_data = jsonimport.get_flat_json_mapping(settings, dataset)
        return parsed_data
    else:
        return None


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


def scale_2dgraph_yaxis(settings, item, rw, maximum):
    factordict = {"iops": 1.05, "lat": 1.25, "bw": 1.5}
    min_y = 0
    if settings["min_y"] == "None":
        min_y = None
    else:
        try:
            min_y = int(settings["min_y"])
        except ValueError:
            print("Min_y value is invalid (not None or integer).")

    max_y = maximum["total"][item["type"]] * factordict[item["type"]]

    if settings[f"max_{item['type']}"]:
        max_y = settings[f"max_{item['type']}"]

    return (min_y, max_y)


def validate_colors(colors):
    listofcolors = []
    listofcolors.extend(list(mcolors.TABLEAU_COLORS.keys()))
    listofcolors.extend(list(mcolors.CSS4_COLORS.keys()))
    listofcolors.extend(list(mcolors.XKCD_COLORS.keys()))
    listofcolors.extend(list(mcolors.BASE_COLORS.keys()))

    for color in colors:
        if color not in listofcolors:
            print(
                f"\n Color {color} is not a known color. Please check the spelling.\n"
            )
            sys.exit(1)


def get_color(settings, supportdata):
    try:
        color = supportdata["colors"].pop(0)
    except IndexError:
        print(
            "\nThere are more lines to draw than there are colors specified. If you used the --colors option: "
            "please specify more colors or remove the --colors parameter.\n"
        )
        sys.exit(1)
    return color


def get_colors(settings):
    cm = settings["colors"]
    if cm:
        return cm
    else:
        colorlist = []
        colorlist.extend(list(mcolors.TABLEAU_COLORS.keys()))
        colorlist.extend(list(mcolors.XKCD_COLORS.keys()))
        return colorlist


def drawline(settings, item, rw, supportdata):
    axes = supportdata["axes"]

    if settings["enable_markers"]:
        marker_value = supportdata["marker_list"].pop(0)
    else:
        marker_value = None

    xvalues = item[rw]["xvalues"]
    yvalues = item[rw]["yvalues"]
    
    #
    # Use a moving average as configured by the commandline option
    # to smooth out the graph for better readability.
    #
    if settings["moving_average"]:
        yvalues = supporting.running_mean(yvalues, settings["moving_average"])
    #
    # Plotting the line
    #
    
    dataplot = f"{item['type']}_plot"
    color = get_color(settings, supportdata)
    axes[dataplot] = axes[item["type"]].plot(
        xvalues,
        yvalues,
        marker=marker_value,
        markevery=(len(yvalues) / (len(yvalues) * 10)),
        color=color,
        label=item[rw]["ylabel"],
        linewidth=settings["line_width"],
    )[0]
    supportdata["host"].set_xlabel(item["xlabel"])
    #
    # Set minimum and maximum values for y-axis where applicable.
    #
    limits = scale_2dgraph_yaxis(settings, item, rw, supportdata["maximum"])
    axes[item["type"]].set_ylim(limits)
    #
    # Label Axis
    #
    padding = axes[f"{item['type']}_pos"]
    axes[item["type"]].set_ylabel(item[rw]["ylabel"], labelpad=padding)
    #
    # Add line to legend
    #
    supportdata["lines"].append(axes[dataplot])
    create_single_label(settings, item, rw, supportdata)


def create_single_label(settings, item, rw, supportdata):
    # print(maxlabelsize)
    mylabel = create_label(settings, item, supportdata["directories"])
    mylabel = get_padding(mylabel, supportdata["maxlabelsize"])

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
    supportdata["labels"].append(labelset)


def generate_labelset(settings, supportdata):
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

    for label in supportdata["labels"]:
        for key in label.keys():
            label_length = len(str(label[key]))
            master_length = master_padding[key]
            if label_length > master_length:
                master_padding[key] = label_length
                if label_length % 2 != 0:
                    master_padding[key] = master_padding[key] + 1

    red_patch = mpatches.Patch(color="white", label="Just filler")
    supportdata["lines"].insert(0, red_patch)
    header = ""

    values = []
    for item in supportdata["labels"]:
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
        supportdata["lines"].insert(position, red_patch)
        values.insert(position, header)

    return (values, ncol)
