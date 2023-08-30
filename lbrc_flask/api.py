from functools import wraps
import uuid
from lbrc_flask.database import db, GUID
from flask import request, abort

def get_api_key():
    if not request.args.get('api_key'):
        return None

    api_key = request.args.get('api_key')

    return ApiKey.query.filter_by(key=uuid.UUID(api_key)).one_or_none()


class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(GUID, nullable=False, default=uuid.uuid4)
    name = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'API Key: {self.name}'


def validate_api_key():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = get_api_key()

            print(api_key)
            if not api_key:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function
    return decorator