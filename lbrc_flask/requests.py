import urllib
from flask import request


def get_value_from_all_arguments(name):
    all_args = {**request.view_args, **request.args, **request.form}

    if request.data and request.json:
        all_args.update(request.json)

    return all_args.get(name)


def add_parameters_to_url(url, parameters):
    url_parts = urllib.parse.urlparse(url)

    newq = []
    if len(url_parts.query) > 0:
        newq.append(url_parts.query)
    
    if len(parameters) > 0:
        newq.append(urllib.parse.urlencode(parameters))
    
    url_parts = url_parts._replace(query = '&'.join(newq))

    return urllib.parse.urlunparse(url_parts)


