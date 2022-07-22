import sys

def get_default_settings():
    settings = {}
    settings["filter"] = ['read','write']
    settings["type"] = []
    settings["dpi"] = 200
    settings["title_fontsize"] = 16
    settings["subtitle_fontsize"] = 10
    settings["credit_fontsize"] = 10
    settings["source_fontsize"] = 8
    settings["table_fontsize"] = 10
    settings["tablecolumn_spacing"] = 0.01
    settings["colors"] = [None]
    return settings

def get_graphtype(settings):
    graphtypes = 'bargraph3d','bargraph2d_qd','bargraph2d_nj','histogram','loggraph','compare_graph'
    for x in graphtypes:
        if settings[x]:
            return x
    print(f"\n None of the graphtypes is enabled, this is probably a bug.\n")
    sys.exit(1)