#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from matplotlib.font_manager import FontProperties
import fiolib.supporting as supporting
from datetime import datetime
import fiolib.dataimport as logdata
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
    datatypes = data['datatypes']
    directories = logdata.get_unique_directories(dataset)
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
    extra_offset = len(datatypes) * len(settings['iodepth']) * len(
        settings['numjobs']) * len(settings['filter'])

    bottom_offset = 0.18 + (extra_offset/120)
    if 'bw' in datatypes and (len(datatypes) > 2):
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
    fontP = FontProperties(family='monospace')
    fontP.set_size('xx-small')
    maximum = dict.fromkeys(settings['type'], 0)

    for item in data['dataset']:
        for rw in settings['filter']:
            if rw in item.keys():
                if settings['enable_markers']:
                    marker_value = marker_list.pop(0)
                else:
                    marker_value = None

                xvalues = item[rw]['xvalues']
                yvalues = item[rw]['yvalues']

                #
                # Use a moving average as configured by the commandline option
                # to smooth out the graph for better readability.
                #
                if settings['moving_average']:
                    yvalues = supporting.running_mean(
                        yvalues, settings['moving_average'])
                #
                # PLOT
                #
                dataplot = f"{item['type']}_plot"
                axes[dataplot] = axes[item['type']].plot(xvalues,
                                                         yvalues,
                                                         marker=marker_value,
                                                         markevery=(len(
                                                             yvalues) / (len(yvalues) * 10)),
                                                         color=colors.pop(0),
                                                         label=item[rw]['ylabel'])[0]
                host.set_xlabel(item['xlabel'])
                #
                # Assure axes are scaled correctly, starting from zero.
                #
                factor = 1.1
                if item['type'] == 'bw':
                    factor = 1.2

                if settings['max']:
                    maximum[item['type']] = settings['max']
                else:
                    max_yvalue = max(yvalues)
                    if max_yvalue > maximum[item['type']]:
                        maximum[item['type']] = max_yvalue

                axes[item['type']].set_ylim(0, maximum[item['type']] * factor)
                #
                # Label Axis
                #
                padding = axes[f"{item['type']}_pos"]
                axes[item['type']].set_ylabel(
                    item[rw]['ylabel'],
                    labelpad=padding)
                #
                # Add line to legend
                #
                lines.append(axes[dataplot])
                if len(directories) > 1:
                    mydir = f"{item['directory']}-"
                else:
                    mydir = ""
                labels.append(
                    f"|{mydir}{item['type']:>4}|{rw:>5}|qd: {item['iodepth']:>2}|nj: {item['numjobs']:>2}|mean: {item[rw]['mean']:>6}|std%: {item[rw]['stdv']:>6} |P{settings['percentile']}: {item[rw]['percentile']:>6}")

    host.legend(lines, labels, prop=fontP,
                bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=2)
    #
    # Save graph to file (png)
    #
    if settings['source']:
        axis = list(axes.keys())[0]
        ax = axes[axis]
        plt.text(1, -0.10, str(settings['source']), ha='right', va='top',
                 transform=ax.transAxes, fontsize=8, fontfamily='monospace')

    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    title = settings['title'].replace(" ", '-')
    title = title.replace("/", '-')
    plt.tight_layout(rect=[0, 0.00, 0.95, 0.95])
    fig.savefig(f"{title}-{now}.png", dpi=settings['dpi'])
