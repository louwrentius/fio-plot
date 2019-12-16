#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pprint
import fiolib.supporting as supporting
from datetime import datetime
import fiolib.shared_chart as shared


def chart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for drawing iops/latency bars for a
    particular iodepth."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types,
                                 settings['rw'], settings['numjobs'])

    fig, (ax1, ax2) = plt.subplots(
        nrows=2, gridspec_kw={'height_ratios': [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    if settings['source']:
        plt.text(1, -0.08, str(settings['source']), ha='right', va='top',
                 transform=ax1.transAxes, fontsize=9)

    ax2.axis('off')
    #
    # Creating the bars and chart
    x_pos = np.arange(0, len(data['x_axis']) * 2, 2)
    width = 0.9

    n = np.array(data['y2_axis']['data'], dtype=float)

    rects1 = ax1.bar(x_pos, data['y1_axis']['data'], width,
                     color='#a8ed63')
    rects2 = ax3.bar(x_pos + width, n, width,
                     color='#34bafa')

    #
    # Configure axis labels and ticks
    ax1.set_ylabel(data['y1_axis']['format'])
    ax1.set_xlabel(data['x_axis_format'])
    ax3.set_ylabel(data['y2_axis']['format'])

    ax1.set_xticks(x_pos + width / 2)
    ax1.set_xticklabels(data['x_axis'])
    #
    # Set title
    settings['type'] = ""
    settings['iodepth'] = dataset_types['iodepth']
    if settings['rw'] == 'randrw':
        supporting.create_title_and_sub(settings, plt, skip_keys=['iodepth'])
    else:
        supporting.create_title_and_sub(
            settings, plt, skip_keys=['iodepth', 'filter'])
    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    shared.autolabel(rects2, ax3)
    #
    #
    shared.create_stddev_table(data, ax2)
    #
    # Create legend
    ax2.legend((rects1[0], rects2[0]),
               (data['y1_axis']['format'],
                data['y2_axis']['format']), loc='center left', frameon=False)
    #
    # Save graph to file
    #
    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    title = settings['title'].replace(" ", '-')
    title = title.replace("/", '-')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f"{title}_{now}.png", dpi=settings['dpi'])
