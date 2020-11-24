import datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
