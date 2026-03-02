import urllib
from flask import request


def all_args():
    result = {
        **{k: v for k, v in request.view_args.items() if v},
        **{k: v for k, v in request.args.items() if v},
        **{k: v for k, v in request.form.items() if v},
    }

    if request.data and request.json:
        result.update(
            {k: v for k, v in request.json.items() if v},
        )
    
    return result


def get_value_from_all_arguments(name):
    return all_args().get(name)


def add_parameters_to_url(url, parameters):
    url_parts = urllib.parse.urlparse(url)

    newq = []
    if len(url_parts.query) > 0:
        newq.append(url_parts.query)
    
    if len(parameters) > 0:
        newq.append(urllib.parse.urlencode(parameters))
    
    url_parts = url_parts._replace(query = '&'.join(newq))

    return urllib.parse.urlunparse(url_parts)
