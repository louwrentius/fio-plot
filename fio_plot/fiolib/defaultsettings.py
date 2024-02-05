import sys

def get_default_settings():
    settings = {}
    settings["disable_grid"] = False
    settings["enable_markers"] = False
    settings["subtitle"] = None
    settings["maxdepth"] = 64
    settings["maxjob"] = 64
    settings["filter"] = ['read','write']
    settings["type"] = []
    settings["dpi"] = 200
    settings["percentile"] = 99.99
    settings["moving_average"] = None
    settings["max_z"] = None
    settings["min_lat"] = 0
    settings["min_iops"] = 0
    settings["truncate_xaxis"] = None
    settings["xlabel_depth"] = 0
    settings["xlabel_parent"] = 1
    settings["xlabel_segment_size"] = 1000
    settings["xlabel_single_column"] = False
    settings["line_width"] = 1
    settings["group_bars"] = False
    settings["show_cpu"] = False
    settings["show_data"] = False
    settings["show_ss"] = False
    settings["table_lines"] = False 
    settings["max_lat"] = None
    settings["max_clat"] = None
    settings["max_slat"] = None
    settings["max_iops"] = None
    settings["max_bw"] = None
    settings["draw_total"] = False
    settings["colors"] = [None]
    settings["disable_fio_version"] = False
    settings["title_fontsize"] = 16
    settings["subtitle_fontsize"] = 10
    settings["source_fontsize"] = 8
    settings["credit_fontsize"] = 10
    settings["table_fontsize"] = 8
    settings["tablecolumn_spacing"] = 0.01
    settings["include_hosts"] = None
    settings["exclude_hosts"] = None
    settings["colors"] = None
    return settings

def get_graphtype(settings):
    graphtypes = 'bargraph3d','bargraph2d_qd','bargraph2d_nj','histogram','loggraph','compare_graph'
    for x in graphtypes:
        if settings[x]:
            return x
    print("\n None of the graphtypes is enabled, this is probably a bug.\n")
    sys.exit(1)
