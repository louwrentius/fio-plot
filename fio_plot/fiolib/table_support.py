import matplotlib.font_manager as font_manager

def get_widest_col(data):

    sizes = []
    for x in data:
        s = str(x)
        length = len(s)
        sizes.append(length)
    return sizes


def get_max_width(dataset, cols):
    matrix = []
    returndata = []
    for item in dataset:
        matrix.append(get_widest_col(item))

    col = 0
    while col < cols:
        column = 3
        for item in matrix:
            if item[col] > column:
                column = item[col]
        returndata.append(column)
        col += 1
    return returndata


def calculate_colwidths(settings, cols, matrix):
    collist = []
    for item in matrix:
        value = item * settings["tablecolumn_spacing"]
        collist.append(value)
    return collist


def scale_iops(data):
    scaled = []
    for x in data:
        if len(str(x)) > 4:
            scale = int(round((x/1000),0))
            scaled.append(f"{scale}K")
        elif len(str(x)) > 5:
            scale = round((x/1000000),1)
            scaled.append(f"{scale}M")
        else:
            scaled.append(str(x))
    return scaled


def alternate_cell_height(number=2,stepsize=2):
    start = 5
    stop = start + (number * stepsize)
    while True:
        for x in range(start, stop, stepsize):
            yield x / 10


def get_host_metric_data(data):
    returndata = []
    counter = 1
    hostcounter = 0 
    divide = int(len(data["hostname_series"]) / len(data["x_axis"])) # that int convert should work
    for host in data["hostname_series"]:
        hostcounter += 1
        metricvalue = data["x_axis"][counter-1]
        returndata.append({ "hostname": host, "value": metricvalue })
        if hostcounter % divide == 0:
            counter += 1
    return returndata


def create_data_for_table_with_hostname_data(settings, data, type):
    returndata = {}
    hostmetric = get_host_metric_data(data)
    returndata["hostnames"] = [ x["hostname"] for x in hostmetric ]
    returndata["metric"] = [ x["value"] for x in hostmetric ]
    returndata["table_vals"] = [ returndata["hostnames"], returndata["metric"], data["y1_axis"][type], data["y2_axis"][type]]
    returndata["metricname"] = f"{settings['graphtype'][-2:]}"
    return returndata


def convert_number_to_yes_no(data):
    newlist = []
    lookup = {1: "yes", 0: "no"}
    for item in data:
        newlist.append(lookup[item])
    return newlist

def tablelines(settings):
    if settings["table_lines"]:
        linewidth = 0.25
        alpha = 1
    else:
        alpha = 0
        linewidth = 0
    return linewidth, alpha

def get_alternator_value(matrix):
    if max(matrix) <= 10:
        alternator = alternate_cell_height()
    if max(matrix) > 10:
        alternator = alternate_cell_height(3,14)
    else:
        alternator = alternate_cell_height(1,10)
    return alternator

def format_table_cells(settings, table, fontsize, matrix, cols):
    linewidth, alpha = tablelines(settings)
    counter = 0 
    alternator = get_alternator_value(matrix)

    for key, cell in table.get_celld().items():
        cell.set_linewidth(linewidth)
        flip = next(alternator) # creates the alternating height pattern when the top lables are too long.
        ### This section below formats the top row of the table
        if counter < (cols): # the first cells up to the number of collums is the top row
            cell._text.set_verticalalignment('bottom') # this is required to reduce cell height
            cell.set_alpha(alpha) # this is a fix for text being cut off, maybe better solution?
            cell.set_fontsize(fontsize)
            height = cell.get_height()
            cell.set_height(height * flip) # prevens cell text overlap
        else:
            cell.set_fontsize(settings["table_fontsize"])
        ## This is some trial and error formatting, don't remove the stuff below.
        if fontsize == 8 and max(matrix) > 5:
            cell.set_width(0.08)
        else:
           cell.set_width(0.042)
        counter += 1
    return None