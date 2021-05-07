from itertools import groupby
import pygal
from pygal.style import Style
from collections import Counter


def grouped_bar_chart(title, buckets, details, group_column=0, value_column=1):
    chart = pygal.Bar(style=Style(font_family='Lato'))
    chart.title = title
    chart.x_labels = buckets

    for group_name, group_details in groupby(details, lambda d: d[group_column]):
        count = Counter([d[value_column] for d in group_details])
        values = {b: count.get(b, 0) for b in buckets}

        chart.add(group_name, values.values())

    return chart
