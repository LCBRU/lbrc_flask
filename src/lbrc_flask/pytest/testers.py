import pytest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__requires_login
from lbrc_flask.pytest.html_content import get_records_found, get_table_row_count
from lbrc_flask.pytest.asserts import assert_html_page_standards, assert__page_navigation, assert__requires_role, assert_modal_boilerplate


class FlaskViewTester:
    @property
    def endpoint(self):
        # Test classes must implement an endpoint property that
        # returns an endpoint as used by the Flask url_for function
        # for example, 'ui.index'
        raise NotImplementedError()

    def url(self, external=True, **kwargs):
        return url_for(self.endpoint, _external=external, **kwargs)


class FlaskGetViewTester(FlaskViewTester):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, client, faker, loggedin_user):
        self.client = client
        self.faker = faker
        self.loggedin_user = loggedin_user

    def get(self, parameters=None):
        parameters = parameters or {}

        return self.client.get(self.url(**parameters))
    
    def get_page_and_assert_standards(self, parameters=None):
        resp = self.get(parameters)

        assert_html_page_standards(resp, self.loggedin_user)

        return resp

    def get_modal_and_assert_standards(self, parameters=None):
        resp = self.get(parameters)

        assert_modal_boilerplate(resp.soup)

        return resp


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

    def get_index_and_assert_standards(self, expected_count, parameters=None):
        parameters = parameters or {}
        url = self.url(**parameters)
        expected_count_on_page = min([expected_count, self.page_size])

        resp = self.get_page_and_assert_standards(parameters=parameters)

        assert__search_html(resp.soup, clear_url=url)

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
