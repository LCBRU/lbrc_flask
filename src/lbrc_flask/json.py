import datetime
import json
import jsonschema
from functools import wraps
from flask import current_app, request, jsonify


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                jsonschema.validate(request.json, schema)
            except jsonschema.ValidationError as e:
                current_app.logger.info(f'JSON Validation errors: {e.message}')
                return jsonify(e.message), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator
