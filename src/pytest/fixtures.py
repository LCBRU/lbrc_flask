import datetime
import json
from lbrc_flask.requests import get_value_from_all_arguments
from lbrc_flask.forms import DataListField, FlashingForm, SearchForm
from lbrc_flask.forms.dynamic import Field, FieldGroup, FormBuilder, init_dynamic_forms
import pytest
from flask import Response, Flask, Blueprint, render_template_string, url_for, redirect, request, abort
from flask.testing import FlaskClient
from flask_login import login_required
from faker import Faker
from bs4 import BeautifulSoup
from ..database import db
from ..config import BaseTestConfig
from ..json import DateTimeEncoder
from .. import init_lbrc_flask
from ..security import current_user_id, init_security, User, Role
from .faker import LbrcFlaskFakerProvider, LbrcDynaicFormFakerProvider
from unittest.mock import patch


class CustomResponse(Response):
    def __init__(self, baseObject):
        self.__class__ = type(
            baseObject.__class__.__name__, (self.__class__, baseObject.__class__), {}
        )
        self.__dict__ = baseObject.__dict__
        self._soup = None

    def get_json(self):
        return json.loads(self.get_data().decode("utf8"))

    @property
    def soup(self):
        if not self._soup:
            self._soup = BeautifulSoup(self.data, "html.parser")

        return self._soup


class CustomClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        super(CustomClient, self).__init__(*args, **kwargs)

    def post_json(self, *args, **kwargs):

        kwargs["data"] = json.dumps(kwargs.get("data"), cls=DateTimeEncoder)
        kwargs["content_type"] = "application/json"

        return CustomResponse(super(CustomClient, self).post(*args, **kwargs))

    def get(self, *args, **kwargs):
        return CustomResponse(super(CustomClient, self).get(*args, **kwargs))

    def post(self, *args, **kwargs):
        return CustomResponse(super(CustomClient, self).post(*args, **kwargs))


@pytest.fixture(scope="function")
def initialised_app(request, app):
    app_crsf = request.node.get_closest_marker("app_crsf")
    if app_crsf is not None:
        app.config['WTF_CSRF_ENABLED'] = app_crsf.args[0]

    app.test_client_class = CustomClient
    context = app.test_request_context()
    context.push()
    db.create_all()

    yield app

    db.session.close()
    context.pop()


@pytest.fixture(scope="function")
def client(initialised_app):
    client = initialised_app.test_client()
    client.get('/') # Allow initialisation on first request

    yield client


@pytest.fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(LbrcFlaskFakerProvider)
    result.add_provider(LbrcDynaicFormFakerProvider)

    yield result


@pytest.fixture(scope="function")
def ldap_initialize():
    with patch('lbrc_flask.security.ldap.initialize') as mock:
        yield mock
