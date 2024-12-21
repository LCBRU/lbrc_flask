from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import groupby, zip_longest
from tempfile import NamedTemporaryFile

import pygal
from flask import send_file
from pygal.style import Style


@dataclass
class BarChartItem:
    series: str
    bucket: str
    count: int = 1


@dataclass
class SeriesConfig:
    name: str
    color: str = None


def default_series_colors():
    return Style().colors


class BarChart:
    def __init__(self,
                 title: str,
                 items: list[BarChartItem],
                 buckets: list[str]=None,
                 series_config: list[SeriesConfig]=None,
                 **kwargs) -> None:
        self.title: str = title
        self.items: list[BarChartItem] = sorted(items, key=lambda i: (i.series, i.bucket))
        self.buckets: list[str] = buckets or sorted({i.bucket for i in self.items})
        self.value_formatter : function = None
        self.kwargs = kwargs
        self.series_config: list[SeriesConfig] = series_config or []
        self.used_series_config: dict[str, SeriesConfig] = {
            sc.name: sc for sc in self.series_config if sc.name in {i.series for i in self.items}
        }

    def get_chart(self):
        chart: pygal.Bar = pygal.Bar(
            legend_at_bottom=True,
            width=1100,
            height=400,
            print_values=True,
            **self.kwargs,
        )
        chart.show_minor_y_labels = False
        chart.style = self.get_style()
        chart.title = self.title

        if len(self.buckets) > 1:
            chart.x_labels = self.buckets

        max_y_label = max([i.count for i in self.items], default=0)

        for series_name, series_items in groupby(self.items, lambda i: i.series):
            series_items = list(series_items)

            values = {l.bucket: l.count for l in series_items}

            all_values = {b:
                          {'value': values.get(b, 0)}
                          for b in self.buckets}

            chart.add(
                # {
                #     'title': series_name,
                #     'xlink': 'http://google.com',
                #     'style': 'fill: red',
                # },
                series_name,
                all_values.values(),
                formatter=self.value_formatter,
            )

        if max_y_label > 0:
            chart.y_labels_major_count = max_y_label + 1

        return chart
    
    def get_style(self):
        style = Style(
            font_family='Lato',
            no_data_font_size=30,
        )

        custom_cols = [sc.color for sc in self.used_series_config.values()]
        default_cols = [c for c in default_series_colors() if c not in custom_cols]

        cols = []
        for custom, default in zip_longest(custom_cols, default_cols):
            cols.append(custom or default)

        style.colors = cols

        return style

    def send_as_attachment(self):
        chart = self.get_chart()

        with NamedTemporaryFile() as tmp:
            chart.render_to_png(tmp.name)

            return send_file(
                tmp.name,
                as_attachment=True,
                download_name=f'{self.title}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.png',
                max_age=0,
                mimetype='image/png',
            )

    def send_svg(self):
        chart = self.get_chart()

        with NamedTemporaryFile() as tmp:
            tmp.write(chart.render())
            tmp.flush()

            return send_file(
                tmp.name,
                download_name=f'{self.title}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.svg',
                max_age=0,
                mimetype='image/svg+xml',
            )

    def send(self):
        chart = self.get_chart()

        with NamedTemporaryFile() as tmp:
            tmp.write(chart.render_to_png())
            tmp.flush()

            return send_file(
                tmp.name,
                download_name=f'{self.title}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.png',
                max_age=0,
                mimetype='image/png',
            )

    def send_table(self):
        chart = self.get_chart()
        return chart.render_table(transpose=True)


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


