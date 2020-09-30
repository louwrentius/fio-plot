#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pprint
import fiolib.supporting as supporting
import fiolib.shared_chart as shared


def create_bars_and_xlabels(settings, data, ax1, ax3):

    return_data = {'ax1': None,
                   'ax3': None,
                   'rects1': None,
                   'rects2': None}

    iops = data['y1_axis']['data']
    latency = np.array(data['y2_axis']['data'], dtype=float)
    width = 0.9

    color_iops = '#a8ed63'
    color_lat = '#34bafa'

    if settings['group_bars']:
        x_pos1 = np.arange(1, len(iops) + 1, 1)
        x_pos2 = np.arange(len(iops) + 1, len(iops) + len(latency) + 1, 1)

        rects1 = ax1.bar(x_pos1, iops, width, color=color_iops)
        rects2 = ax3.bar(x_pos2, latency, width, color=color_lat)

        x_axis = data['x_axis'] * 2
        ltest = np.arange(1, len(x_axis)+1, 1)

    else:
        x_pos = np.arange(0, (len(iops) * 2), 2)

        rects1 = ax1.bar(x_pos, iops, width, color=color_iops)
        rects2 = ax3.bar(x_pos+width, latency, width, color=color_lat)

        x_axis = data['x_axis']
        ltest = np.arange(0.45, (len(iops) * 2), 2)

    ax1.set_ylabel(data['y1_axis']['format'])
    ax3.set_ylabel(data['y2_axis']['format'])

    ax1.set_xticks(ltest)
    ax1.set_xticklabels(x_axis)

    return_data['rects1'] = rects1
    return_data['rects2'] = rects2
    return_data['ax1'] = ax1
    return_data['ax3'] = ax3

    return return_data


def chart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for drawing iops/latency bars for a
    particular iodepth."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types)

    # pprint.pprint(data)

    fig, (ax1, ax2) = plt.subplots(
        nrows=2, gridspec_kw={'height_ratios': [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    #
    # Puts in the credit source (often a name or url)
    if settings['source']:
        plt.text(1, -0.08, str(settings['source']), ha='right', va='top',
                 transform=ax1.transAxes, fontsize=9)

    ax2.axis('off')

    return_data = create_bars_and_xlabels(settings, data, ax1, ax3)

    rects1 = return_data['rects1']
    rects2 = return_data['rects2']
    ax1 = return_data['ax1']
    ax3 = return_data['ax3']

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
    # Draw the standard deviation table
    shared.create_stddev_table(settings, data, ax2)
    #
    # Draw the cpu usage table if requested
    if settings['show_cpu']:
        shared.create_cpu_table(settings, data, ax2)
    #
    # Create legend
    ax2.legend((rects1[0], rects2[0]),
               (data['y1_axis']['format'],
                data['y2_axis']['format']), loc='center left', frameon=False)
    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)


def compchart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for creating bar charts that compare data."""

    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set_improved(settings, dataset, dataset_types)

    # pprint.pprint(data)

    fig, (ax1, ax2) = plt.subplots(
        nrows=2, gridspec_kw={'height_ratios': [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    #
    # Puts in the credit source (often a name or url)
    if settings['source']:
        plt.text(1, -0.08, str(settings['source']), ha='right', va='top',
                 transform=ax1.transAxes, fontsize=9)

    ax2.axis('off')

    iops = data['y1_axis']['data']
    latency = np.array(data['y2_axis']['data'], dtype=float)

    return_data = create_bars_and_xlabels(settings, data, ax1, ax3)
    rects1 = return_data['rects1']
    rects2 = return_data['rects2']
    ax1 = return_data['ax1']
    ax3 = return_data['ax3']
    #
    # Set title
    settings['type'] = ""
    settings['iodepth'] = dataset_types['iodepth']
    if settings['rw'] == 'randrw':
        supporting.create_title_and_sub(settings, plt, skip_keys=['iodepth'])
    else:
        supporting.create_title_and_sub(
            settings, plt, skip_keys=[])
    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    shared.autolabel(rects2, ax3)

    shared.create_stddev_table(settings, data, ax2)

    if settings['show_cpu']:
        shared.create_cpu_table(settings, data, ax2)

    # Create legend
    ax2.legend((rects1[0], rects2[0]),
               (data['y1_axis']['format'],
                data['y2_axis']['format']), loc='center left', frameon=False)

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)
