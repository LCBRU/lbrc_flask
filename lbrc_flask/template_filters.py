import json
import calendar
from datetime import datetime
from flask import g, request, current_app
from markdown import markdown
from .formatters import format_currency, format_date, format_datetime, format_month, format_number, format_yesno, humanize_datetime, humanize_date
from markupsafe import Markup


def init_template_filters(app):
    @app.template_filter("yes_no")
    def yesno_format(value):
        return format_yesno(value)

    @app.template_filter("datetime_format")
    def datetime_format(value):
        return format_datetime(value)

    @app.template_filter("month_name")
    def month_name(value):
        return calendar.month_name[value]

    @app.template_filter("date_format")
    def date_format(value):
        return format_date(value)

    @app.template_filter("month_format")
    def month_format(value):
        return format_month(value)

    @app.template_filter("datetime_humanize")
    def datetime_humanize(value):
        return humanize_datetime(value)

    @app.template_filter("date_humanize")
    def date_humanize(value):
        return humanize_date(value)

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

    @app.template_filter("markdown")
    def markdown_template(value):
        if value:
            return Markup(markdown(value))
        else:
            return ''

    @app.template_filter("nbsp")
    def nbsp(value):
        if value:
            return value.replace(' ', '\xa0')
        else:
            return ""

    @app.template_filter("pre")
    def pre(value):
        if value:
            return Markup(f'<PRE>{value}</PRE>')
        else:
            return ""

    @app.template_filter("br")
    def br(value):
        if value:
            return Markup(value.replace('\n', '<BR/>'))
        else:
            return ""

    @app.template_filter("paragraphs")
    def br(value):
        if value:
            return Markup('\n'.join([f'<p>{p}</p>' for p in value.splitlines()]))
        else:
            return ""

    @app.template_filter("jsonify")
    def br(value):
        if value:
            return Markup(json.dumps(value))
        else:
            return ""

    @app.template_filter("dict_data_fields")
    def dict_data_fields(value):
        if value:
            return {k: v for k, v in value.items() if k.startswith('data-')}
        else:
            return dict()

    @app.context_processor
    def inject_studd():
        if 'lbrc_flask_title' in g:
            app_name = g.lbrc_flask_title
        else:
            app_name = 'Application'

        try:
            prev = request.args.get('prev', '')
        except:
            # Eat errors because it is possible that we are running outside
            # of a request context - i.e., if we're doing templating from
            # celery.
            prev = ''

        return {
            'current_date': datetime.utcnow().strftime("%c"),
            'current_year': datetime.utcnow().strftime("%Y"),
            'organisation_name': current_app.config["ORGANISATION_NAME"],
            'application_title': app_name,
            'previous_page': prev,
            'admin_email_address': current_app.config["ADMIN_EMAIL_ADDRESS"],
        }
