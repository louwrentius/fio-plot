#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from matplotlib.font_manager import FontProperties
import numpy as np
import pprint as pprint
import fiolib.supporting as supporting
from datetime import datetime


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def create_title_and_sub(settings, plt):
    number_of_types = len(settings['type'])
    if number_of_types <= 2:
        x_offset = 0.5
    else:
        x_offset = 0.425

    plt.suptitle(settings['title'])

    if settings['subtitle']:
        subtitle = settings['subtitle']

    else:
        iodepth = str(settings['iodepth']).strip('[]')
        numjobs = str(settings['numjobs']).strip('[]')
        datatype = str(settings['type']).strip('[]').replace('\'', '')
        subtitle = f"{settings['rw']} | iodepth {iodepth} | numjobs {numjobs} | {datatype}"

    plt.title(subtitle, fontsize=8,
              horizontalalignment='center', x=x_offset, y=1.02)


def chart_2d_log_data(settings, dataset):

    # Raw data must be processed into series data + enriched
    data = supporting.process_dataset(settings, dataset)
    datatypes = data['datatypes']
    # Create matplotlib figure and first axis
    fig, host = plt.subplots()
    fig.set_size_inches(9, 5)
    # Generate axes for the graph
    axes = supporting.generate_axes(host, datatypes)
    # Create title
    create_title_and_sub(settings, plt)
    extra_offset = len(datatypes) * len(settings['iodepth']) * len(
        settings['numjobs']) * len(settings['filter'])
    # pprint.pprint(extra_offset)
    bottom_offset = 0.18 + (extra_offset/120)
    if 'bw' in datatypes and (len(datatypes) > 2):
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

                # Moving Average
                if settings['moving_average']:
                    yvalues = supporting.running_mean(
                        yvalues, settings['moving_average'])

                # PLOT
                dataplot = f"{item['type']}_plot"
                axes[dataplot] = axes[item['type']].plot(xvalues, yvalues, marker=marker_value, markevery=(len(
                    yvalues) / (len(yvalues) * 10)), color=colors.pop(0), label=item[rw]['ylabel'])[0]
                host.set_xlabel(item['xlabel'])

                max_yvalues = max(yvalues)
                if max_yvalues > maximum[item['type']]:
                    maximum[item['type']] = max_yvalues
                    axes[item['type']].set_ylim(0, max_yvalues)

                # Label Axis
                padding = axes[f"{item['type']}_pos"]
                axes[item['type']].set_ylabel(
                    item[rw]['ylabel'],
                    labelpad=padding)

                # Add line to legend
                lines.append(axes[dataplot])
                labels.append(
                    f"|{item['type']:>4}|{rw:>5}|qd: {item['iodepth']:>2}|nj: {item['numjobs']:>2}|mean: {item[rw]['mean']:>6}|std: {item[rw]['stdv']:>6} |P{settings['percentile']}: {item[rw]['percentile']:>6}")

    # Create Legend
    if len(lines) >= 100:
        ncol = 3
    else:
        ncol = 2
    host.legend(lines, labels, prop=fontP,
                bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=ncol)

    # Save graph to file (png)
    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    fig.savefig(f"{now}.png", dpi=settings['dpi'])
