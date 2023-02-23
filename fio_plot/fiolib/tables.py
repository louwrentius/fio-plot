import sys
from . import table_support as ts

def create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize):
    cols = len(table_vals[0])
    matrix = ts.get_max_width(table_vals, cols)
    #matrix = [ x / 4 for x in matrix ]
    print(matrix)
    #print(fontsize)
    colwidths = ts.calculate_colwidths(settings, cols, matrix)
    #colwidths = [ x * 0.4 for x in colwidths]
    #print(colwidths)
    table = ax2.table(
        cellText=table_vals,
        loc=location,
        rowLabels=rowlabels,
        colLoc="center",
        colWidths=colwidths,
        cellLoc="center",
        rasterized=False,
    )
    table.auto_set_font_size(False) # Very Small
    table.scale(1, 1.2)
    print(settings["table_lines"])
    if settings["table_lines"]:
        linewidth = 0.25
        alpha = 1
    else:
        alpha = 0
        linewidth = 0
    counter = 0 
    if max(matrix) <= 10:
        alternator = ts.alternate_cell_height()
    else:
        alternator = ts.alternate_cell_height(3,14)
    for key, cell in table.get_celld().items():
        cell.set_linewidth(linewidth)
        flip = next(alternator)
        if counter < (cols):
            cell._text.set_verticalalignment('bottom')
            cell.set_alpha(alpha)
            cell.set_fontsize(fontsize)
            height = cell.get_height()
            if "hostname_series" in data.keys():
                if data["hostname_series"]:
                    cell.set_height(height * flip)
            else:
                cell.set_height(height * flip)
        else:
            cell.set_fontsize(settings["table_fontsize"])
        if fontsize == 8 and max(matrix) > 5:
            cell.set_width(0.08)
        else:
           cell.set_width(0.042)
        counter += 1

def create_cpu_table(settings, data, ax2, fontsize):
    table_vals = [data["x_axis"], data["cpu"]["cpu_usr"], data["cpu"]["cpu_sys"]]
    rowlabels = ["CPU Usage", "cpu_usr %", "cpu_sys %"]
    location = "lower center"
    create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)


def create_values_table(settings, data, ax2, fontsize):
    iops = ts.scale_iops(data["y1_axis"]["data"])
    table_vals = [data["x_axis"], iops, data["y2_axis"]["data"]]
    if "hostname_series" in data.keys():
        if data["hostname_series"]:
            tabledata = ts.create_data_for_table_with_hostname_data(settings, data, "data")
            table_vals = tabledata["table_vals"]
            metricname = tabledata["metricname"]
            rowlabels = [ "Hostname", metricname , "IOP/s", "Latency"]
    else:
        rowlabels = ["IOPs/Lat", data["y1_axis"]["format"], data["y2_axis"]["format"]]
    location = "lower right"
    create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)


def create_stddev_table(settings, data, ax2, fontsize):
    print(data["y1_axis"].keys())
    table_vals = [data["x_axis"], data["y1_axis"]["stddev"], data["y2_axis"]["stddev"]]    
    if "hostname_series" in data.keys():
        if data["hostname_series"]:
            tabledata = ts.create_data_for_table_with_hostname_data(settings, data, "stddev")
            table_vals = tabledata["table_vals"]
            metricname = tabledata["metricname"]
            rowlabels = [ "Hostname", metricname , "IOP/s \u03C3 %", "Latency \u03C3 %"]
    else:
        table_name = settings["label"]
        rowlabels = [table_name, "IOP/s \u03C3 %", "Latency \u03C3 %"]
    location = "lower right"
    create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)


def create_steadystate_table(settings, data, ax2):
    # pprint.pprint(data)
    ## This error is required until I address this
    if "hostname_series" in data.keys():
        print(f"\n Sorry, the steady state table is not compatible (yet) with client/server data\n")
        sys.exit(1)

    if data["ss_attained"]:
        data["ss_attained"] = ts.convert_number_to_yes_no(data["ss_attained"])
        table_vals = [
            data["x_axis"],
            data["ss_data_bw_mean"]["data"],
            data["ss_data_iops_mean"]["data"],
            data["ss_attained"],
        ]

        rowlabels = [
            "Steady state",
            f"BW mean {data['ss_data_bw_mean']['format']}",
            f"{data['ss_data_iops_mean']['format']}  mean",
            f"{data['ss_settings'][0]} attained",
        ]
        location = "lower center"
        create_generic_table(settings, table_vals, ax2, rowlabels, location)
    else:
        print(
            "\n No steadystate data was found, so the steadystate table cannot be displayed.\n"
        )
