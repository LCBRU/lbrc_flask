import pygal
from itertools import groupby
from pygal.style import Style
from collections import Counter


def grouped_bar_chart(title, details, buckets=None):

    details = sorted(details, key=lambda d: d['group'])

    if buckets is None:
        buckets = {d['category'] for d in details}

    chart = pygal.Bar()
    chart.show_minor_y_labels = False
    chart.style = Style(font_family='Lato')
    chart.title = title
    chart.x_labels = buckets

    max_y_label = 0

    for group_name, group_details in groupby(details, lambda d: d['group']):
        count = Counter([d['category'] for d in group_details])
        values = {b: count.get(b, 0) for b in buckets}

        max_y_label = max([max_y_label] + list(values.values()))

        chart.add(group_name, values.values())

    if max_y_label > 0:
        chart.y_labels_major_count = max_y_label + 1

    return chart
