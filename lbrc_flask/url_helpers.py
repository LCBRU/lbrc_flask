from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
from collections import OrderedDict


def update_querystring(url, updates):
    urlparts = urlparse(url)
    qsd = OrderedDict(sorted({q[0]: q[1] for q in parse_qsl(urlparts.query)}.items()))
    qsd.update(updates)
    urlparts = urlparts._replace(query=urlencode(qsd))
    return urlunparse(urlparts)
