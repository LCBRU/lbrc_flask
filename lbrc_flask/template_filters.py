from datetime import datetime
from flask import g
from .formatters import format_currency, format_date, format_datetime, format_number, format_yesno


def init_template_filters(app):
    @app.template_filter("yes_no")
    def yesno_format(value):
        return format_yesno(value)

    @app.template_filter("datetime_format")
    def datetime_format(value):
        return format_datetime(value)

    @app.template_filter("date_format")
    def date_format(value):
        return format_date(value)

    @app.template_filter("currency")
    def currency_format(value):
        return format_currency(value)

    @app.template_filter("separated_number")
    def number_format(value):
        return format_number(value)

    @app.template_filter("title_case")
    def title_case(value):
        return value.title()

    @app.template_filter("blank_if_none")
    def blank_if_none(value):
        return value or ""

    @app.template_filter("default_if_none")
    def default_if_none(value, default):
        return value or default

    @app.template_filter("nbsp")
    def nbsp(value):
        if value:
            return value.replace(' ', '\xa0')
        else:
            return ""

    @app.context_processor
    def inject_now():
        if 'lbrc_flask_title' in g:
            app_name = g.lbrc_flask_title
        else:
            app_name = 'Application'

        return {
            'current_year': datetime.utcnow().strftime("%Y"),
            'application_title': app_name
        }
