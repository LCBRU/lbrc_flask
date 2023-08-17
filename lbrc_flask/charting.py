from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from tempfile import NamedTemporaryFile

import pygal
from flask import send_file
from pygal.style import Style


@dataclass
class BarChartItem:
    series: str
    bucket: str
    count: int = 1


class BarChart:
    def __init__(self, title: str, items: list[BarChartItem], buckets: list[str]=None, show_total: bool=False, **kwargs) -> None:
        self.title: str = title
        self.items: list[BarChartItem] = sorted(items, key=lambda i: i.series)
        self.buckets: list[str] = buckets or sorted({i.bucket for i in self.items})
        self.series: list[str] = sorted({i.series for i in self.items})
        self.value_formatter : function = None
        self.kwargs = kwargs
        self.show_total = show_total

    def get_chart(self):
        chart: pygal.Bar = pygal.Bar(legend_at_bottom=True, width=1100, print_values=True, **self.kwargs)
        chart.show_minor_y_labels = False
        chart.style = Style(font_family='Lato')
        chart.x_labels = self.buckets
        chart.title = self.title

        max_y_label = 0
        total = 0

        for series_name, series_items in groupby(self.items, lambda i: i.series):
            count = Counter({i.bucket: i.count for i in series_items})
            values = {b: count.get(b, 0) for b in self.buckets}

            max_y_label = max([max_y_label] + list(values.values()))
            total += sum(values.values())

            print(total)

            chart.add(series_name, values.values(), formatter=self.value_formatter)

        if max_y_label > 0:
            chart.y_labels_major_count = max_y_label + 1

        if self.show_total:
            chart.title += f' (Total = {total})'

        return chart

    def send_as_attachment(self):
        chart = self.get_chart()

        with NamedTemporaryFile() as tmp:
            chart.render_to_png(tmp.name)

            return send_file(
                tmp.name,
                as_attachment=True,
                download_name=f'{self.title}_{datetime.utcnow():%Y%m%d_%H%M%S}.png',
                max_age=0,
                mimetype='image/png',
            )


def grouped_bar_chart(title, details, buckets=None):

    details = sorted(details, key=lambda d: d['group'])

    if buckets is None:
        buckets = sorted({d['category'] for d in details})

    chart = pygal.Bar()
    chart.show_minor_y_labels = False
    chart.style = Style(font_family='Lato')
    chart.x_labels = buckets

    max_y_label = 0
    total = 0

    for group_name, group_details in groupby(details, lambda d: d['group']):
        count = Counter([d['category'] for d in group_details])
        values = {b: count.get(b, 0) for b in buckets}

        max_y_label = max([max_y_label] + list(values.values()))
        total += sum(values.values())

        chart.add(group_name, values.values())

    if max_y_label > 0:
        chart.y_labels_major_count = max_y_label + 1
    
    chart.title = f'{title} (Total = {total})'

    return chart


