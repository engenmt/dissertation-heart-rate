import matplotlib.pyplot as pp
import numpy as np
import os
import pandas as pd
import sys


from datetime import datetime, timedelta
from dateutil.parser import isoparse
from matplotlib.ticker import MultipleLocator, NullFormatter
from matplotlib.dates import DateFormatter, MinuteLocator
from data_types import TYPES
from xml.etree import ElementTree


# "5-class Paired" from colorbrewer2.com
cb_light_blue  = '#a6cee3'
cb_dark_blue   = '#1f78b4'
cb_light_green = '#b2df8a'
cb_dark_green  = '#33a02c'
cb_pink        = '#fb9a99'

COLORS = [
    cb_light_blue, # Heart rate points
    cb_pink,       # Presentation HR average
    cb_dark_blue,  # Rolling minute average
    cb_dark_green  # Resting HR
]


def parse_datetime(datetime_str):
    """Convert a (roughly ISO-8601) string into a datetime.datetime object.
    
    The format of datetime strings from the xml file is 'YYYY-MM-DD hh:mm:ss -HHMM',
    and isoparse doesn't like the space before the '-HHMM', so we remove it.
    """
    return isoparse(datetime_str.replace(' -', '-')).replace(tzinfo=None)


class Extractor(object):
    """A class for extracting data from exported from Apple Health."""
    def __init__(self, input_file):

        self.file_dir = os.path.abspath(os.path.split(input_file)[0])
        with open(input_file) as f:
            self.log(f"Ingesting data from '{input_file}'... ", end = '')
            self.data_raw = ElementTree.parse(f)
            self.log("Done!")
        self.root = self.data_raw.getroot()
    
    def log(self, message, **kwargs):
        print(message, file=sys.stdout, **kwargs)
        sys.stdout.flush()
    
    def get_data_by_type(self, data_type):
        return [
            datum.attrib 
            for datum in self.root 
            if datum.attrib.get('type') == TYPES[data_type]
        ]


def time_weighted_sum(data):
    """Given a list of (datetime, value) pairs, compute the average of the linear interpolation.
    
    Notes:
        Assumes that the data is sorted chronologically.
    """
    values = []
    weights = []
    for (time_prev, val_prev), (time_curr, val_curr) in zip(data, data[1:]):
        # For each interval between data points, include the average of values on either side.
        values.append( (val_prev + val_curr)/2 )

        # The weight of a value is the duration of the interval.
        weights.append( (time_curr - time_prev).total_seconds() )
    
    return np.average(values, weights=weights)


def make_plot(file_name):

    all_data = Extractor(file_name)
    hr_data = [
        (parse_datetime(datum['startDate']), float(datum['value'])) 
        for datum in all_data.get_data_by_type('HeartRate')
    ]

    # Hardcoded values
    defense_date = datetime(2021, 4, 27, 9)
    time_presentation_start = defense_date.replace(hour=9, minute=37, second=30)
    time_presentation_end = defense_date.replace(hour=10, minute=29)
    time_min = defense_date.replace(hour=9, minute=8) # Earliest relevant time
    time_max = defense_date.replace(hour=10, minute=57) # Latest relevant time
    hr_resting = 65

    # Only include values in the relevant timespan
    hr_array = np.array(
        sorted([
            datum for datum in hr_data if time_min <= datum[0] <= time_max
        ])
    )
    hr_array_presentation = np.array([
        datum for datum in hr_data 
        if time_presentation_start <= datum[0] <= time_presentation_end
    ])
    hr_avg_presentation = time_weighted_sum(hr_array_presentation)

    hr_df = pd.DataFrame(index=hr_array[:,0], data=hr_array[:,1])
    hr_rolling_mean_df = hr_df.rolling('60s').mean()
    hr_rolling_mean_df.index = hr_rolling_mean_df.index.shift(-30, freq='s')
    # The dataframe hr_rolling_mean_df is now centered, e.g. the value at
    # any given time is the rolling average for the surrounding minute.

    fig_width  = 11
    fig_height = 6
    fig_size = (fig_width, fig_height)
    fig = pp.figure(figsize = fig_size)
    ax = fig.add_subplot()
    
    # Plotted values
    ax.plot(
        hr_df,
        # hr_array[:,0], 
        # hr_array[:,1], 
        marker='.',
        color=COLORS[0], 
        ls='',
        label='Heart rate (HR)'
    )
    # Lines
    ax.hlines(
        y=hr_avg_presentation,
        xmin=time_min,
        xmax=time_max,
        color=COLORS[1],
        label='Presentation HR average'
    )
    ax.plot(
        hr_rolling_mean_df,
        color=COLORS[2],
        label='Rolling minute average'
    )
    ax.hlines(
        y=hr_resting,
        xmin=time_min,
        xmax=time_max,
        color=COLORS[3],
        label='Resting HR'
    )

    # Annotations
    annotation_kwargs = dict(
        horizontalalignment='center',
        arrowprops={'arrowstyle': '->'}
    )
    time_committee_member_late = defense_date.replace(hour=9, minute=35)
    ax.annotate(
        'Final committee\nmember late',
        xy=(time_committee_member_late, 109),
        xytext=(time_committee_member_late, 90),
        **annotation_kwargs
    )
    ax.annotate(
        'Quorum attained,\nPresentation begins', 
        xy=(time_presentation_start, 149),
        xytext=(time_presentation_start, 170),
        **annotation_kwargs
    )
    ax.annotate(
        'Presentation ends', 
        xy=(time_presentation_end, 116),
        xytext=(time_presentation_end, 135),
        **annotation_kwargs
    )
    time_gen_audience_leaves = defense_date.replace(hour=10, minute=39)
    ax.annotate(
        'General audience leaves', 
        xy=(time_gen_audience_leaves, 107),
        xytext=(time_gen_audience_leaves, 85),
        **annotation_kwargs
    )
    time_waiting_room_enter = defense_date.replace(hour=10, minute=46, second=45)
    ax.annotate(
        'Enter (virtual)\nwaiting room', 
        xy=(time_waiting_room_enter, 110),
        xytext=(time_waiting_room_enter, 145),
        **annotation_kwargs
    )
    time_waiting_room_leave = defense_date.replace(hour=10, minute=50, second=37)
    ax.annotate(
        'Reenter room\nwith committee', 
        xy=(time_waiting_room_leave, 90),
        xytext=(time_waiting_room_leave, 70),
        **annotation_kwargs
    )
    time_success = defense_date.replace(hour=10, minute=51, second=45)
    ax.annotate(
        'Officially\npassed!', 
        xy=(time_success, 116),
        xytext=(time_success, 130),
        **annotation_kwargs
    )

    # Titles, legend
    fig.suptitle(None)
    ax.set_title('Doctoral Defense Heart Rate')
    ax.legend(frameon=False, loc='upper right') 

    # x-axis
    ax.set_xlabel("Time (24 hr)")
    ax.set_xlim(time_min, time_max)
    ax.xaxis.set_major_locator(MinuteLocator(byminute=range(0,60,15))) # Major ticks every 15 minutes
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M')) # With labels
    ax.xaxis.set_minor_locator(MinuteLocator(byminute=range(0,60,5))) # Minor ticks every 5 minutes
    ax.xaxis.set_minor_formatter(NullFormatter()) # Without labels

    # y-axis
    ax.set_ylabel("Heart Rate (bpm)")
    ax.set_ylim(40, 200)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_minor_locator(MultipleLocator(10))

    pp.tight_layout()

    figure_name = 'figure.png'
    pp.savefig(figure_name)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} /path/to/export.xml", file=sys.stderr)
        sys.exit(1)

    file_name = sys.argv[1]
    make_plot(file_name)
