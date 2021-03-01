import urllib
from flask import request


def get_value_from_all_arguments(name):
    all_args = {**request.view_args, **request.args, **request.form}

    if request.json:
        all_args.update(request.json)

    return all_args.get(name)


def add_parameters_to_url(url, parameters):
    url_parts = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qs(url_parts.query)
    q.update(parameters)
    url_parts = url_parts._replace(query = urllib.parse.urlencode(q))

    return urllib.parse.urlunparse(url_parts)


