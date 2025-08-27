import pytest
from dataclasses import dataclass
from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__requires_login, assert_html_page_standards, assert__page_navigation, assert__requires_role, assert_modal_boilerplate, assert__error__required_field_modal
from lbrc_flask.pytest.html_content import get_records_found, get_table_row_count
from enum import Enum


class ModelTesterField_DataType(Enum):
    STRING = 1
    TEXT = 2


@dataclass
class ModelTesterField:
    field_name: str
    field_title: str
    data_type: ModelTesterField_DataType
    is_mandatory: bool = False


class ModelTesterFields:
    def __init__(self, fields):
        self.fields = fields
    
    @property
    def mandatory_fields(self):
        return list(filter(lambda x: x.is_mandatory, self.fields))

    @property
    def string_fields(self):
        return list(filter(lambda x: x.data_type == ModelTesterField_DataType.STRING, self.fields))


class FlaskViewTester:
    @property
    def is_modal(self):
        return False

    @property
    def endpoint(self):
        # Test classes must implement an endpoint property that
        # returns an endpoint as used by the Flask url_for function
        # for example, 'ui.index'
        raise NotImplementedError()

    def url(self, external=True, **kwargs):
        return url_for(self.endpoint, _external=external, **kwargs)

    def assert_standards(self, resp):
        if self.is_modal:
            assert_modal_boilerplate(resp.soup)
        else:
            assert_html_page_standards(resp, self.loggedin_user)



class FlaskGetViewTester(FlaskViewTester):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, client, faker, loggedin_user):
        self.client = client
        self.faker = faker
        self.loggedin_user = loggedin_user

    def get(self, parameters=None):
        parameters = parameters or {}

        return self.client.get(self.url(**parameters))
    
    def get_and_assert_standards(self, parameters=None):
        resp = self.get(parameters)
        self.assert_standards(resp)

        return resp


class FlaskPostViewTester(FlaskViewTester):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, client, faker, loggedin_user):
        self.client = client
        self.faker = faker
        self.loggedin_user = loggedin_user

    def assert__error__required_field(self, resp, field_title):
        assert__error__required_field_modal(resp.soup, field_title)

    def get_data_from_object(self, object, skip_fields=None):
        skip_fields = skip_fields or {}

        return {k: v for k, v in object.__dict__.items()
                if not k.startswith('_') and k not in skip_fields}

    def post_object(self, object, parameters=None):
        return self.post(
            data=self.get_data_from_object(object),
            parameters=parameters,
        )

    def post(self, data=None, parameters=None):
        parameters = parameters or {}
        data = data or {}

        return self.client.post(
            self.url(**parameters),
            data=data,
        )


class IndexTester(FlaskGetViewTester):
    # Redefine in instance classes for different page sizes
    PAGE_SIZE = 5

    @staticmethod
    # Pass the redefined PAGE_SIZE as argument to this method
    def page_edges(page_size=PAGE_SIZE, pages=10):
        result = []

        for page in range(pages):
            item_count_for_full_page = page * page_size

            result.extend([item_count_for_full_page, item_count_for_full_page + 1])
        
        result.append(pages * page_size)
        return result

    @property
    def page_size(self):
        return self.PAGE_SIZE

    def get_and_assert_standards(self, expected_count, parameters=None):
        resp = self.get(parameters=parameters)
        self.assert_standards(resp, expected_count, parameters)

        return resp
    
    def assert_standards(self, resp, expected_count, parameters):
        parameters = parameters or {}

        expected_count_on_page = min([expected_count, self.page_size])

        super().assert_standards(resp)

        assert__search_html(resp.soup, clear_url=self.url(**parameters))

        assert expected_count == get_records_found(resp.soup)
        assert expected_count_on_page == get_table_row_count(resp.soup)

        assert__page_navigation(
            client=self.client,
            endpoint=self.endpoint,
            parameters=parameters,
            items=expected_count,
            page_size=self.page_size,
        )

        return resp


class RequiresLoginTester(FlaskViewTester):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, client):
        self.client = client

    def test__get__requires_login(self):
        assert__requires_login(self.client, self.url(external=False))


class RequiresRoleTester(FlaskViewTester):
    @pytest.fixture(autouse=True)
    def _set_fixtures(self, client):
        self.client = client

    def test__get__requires_login(self):
        assert__requires_role(client, _url(external=False))
