import pytest
import http
import csv
from io import StringIO
from itertools import zip_longest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__search_modal_html, assert__requires_login, assert_html_page_standards, assert__page_navigation, assert_modal_boilerplate, assert__error__required_field_modal, assert_csrf_token, assert__page_navigation__page, assert__error__string_too_long__modal
from lbrc_flask.pytest.html_content import get_records_found
from lbrc_flask.pytest.helpers import login
from enum import Enum
from lbrc_flask.model import CommonMixin


class PageCountHelper(CommonMixin):
    # Redefine in instance classes for different page sizes
    PAGE_SIZE = 5
    TEST_PAGE_COUNT = 3

    @staticmethod
    # Pass the redefined PAGE_SIZE as argument to this method
    def test_current_pages(test_page_count=TEST_PAGE_COUNT):
        return range(1, test_page_count+1)

    @staticmethod
    # Pass the redefined PAGE_SIZE as argument to this method
    def test_page_edges(page_size=PAGE_SIZE, test_page_count=TEST_PAGE_COUNT):
        result = []

        for page in range(test_page_count):
            item_count_for_full_page = page * page_size

            result.extend([item_count_for_full_page, item_count_for_full_page + 1])
        
        result.append(test_page_count * page_size)

        return result

    @property
    def page_size(self):
        return self.PAGE_SIZE

    def __init__(self, page: int, results_count: int):
        self.page = page
        self.results_count = results_count

    @property
    def page_count(self):
        return ((self.results_count - 1) // self.page_size) + 1

    @property
    def items_on_previous_pages(self):
        return ((self.page - 1) * self.page_size)

    @property
    def expected_results_on_current_page(self):
        if self.page < self.page_count:
            return self.page_size
        elif self.page > self.page_count:
            return 0
        else:
            return self.results_count - self.items_on_previous_pages
        
    def get_current_page_from_results(self, results: list):
        return results[self.items_on_previous_pages:self.items_on_previous_pages + self.expected_results_on_current_page]


class HtmlPageContentAsserter:
    def __init__(self, loggedin_user):
        self.loggedin_user = loggedin_user

    def assert_all(self, resp):
        assert_html_page_standards(resp, self.loggedin_user)


class ModalContentAsserter:
    def assert_all(self, resp):
        assert_modal_boilerplate(resp.soup)


class ModalFormErrorContentAsserter:
    def assert_missing_required_field(self, resp, field_title):
        assert__error__required_field_modal(resp.soup, field_title)

    def assert__error__string_too_long(self, resp, field_title):
        assert__error__string_too_long__modal(resp.soup, field_title)


class SearchContentAsserter:
    def assert_all(self, resp):
        assert__search_html(resp.soup)


class SearchModalContentAsserter:
    def assert_all(self, resp):
        assert__search_modal_html(resp.soup)


class PageContentAsserter:
    def __init__(self, url: str, page_count_helper: PageCountHelper):
        self.url=url
        self.page_count_helper = page_count_helper

    def assert_all(self, resp):
        assert self.page_count_helper.results_count == get_records_found(resp.soup)

        self.assert_paginator(resp)
    
    def assert_paginator(self, resp):
        if self.page_count_helper.page > self.page_count_helper.page_count:
            # No point checking paginator if current page is out of range
            return

        paginator = resp.soup.find('nav', 'pagination')

        if self.page_count_helper.page_count > 1:
            assert paginator is not None
            assert__page_navigation__page(self.url, paginator, self.page_count_helper.page_count, self.page_count_helper.page)
        else:
            assert paginator is None


class RowContentAsserter:
    def __init__(self, expected_results: list, page_count_helper: PageCountHelper):
        self.page_count_helper = page_count_helper
        self.expected_results = expected_results

    def row_count(self, resp) -> int:
        return len(self.get_rows(resp))

    def assert_all(self, resp):
        if self.page_count_helper.page > self.page_count_helper.page_count:
            # No point checking rows if current page is out of range
            return

        assert self.page_count_helper.expected_results_on_current_page == self.row_count(resp)
        self.assert_rows_details(resp)

    def assert_rows_details(self, resp):
        for er, row in zip_longest(self.expected_results, self.get_rows(resp)):
            self.assert_row_details(row, er)

    def assert_row_details(self, row, expected_result):
        ...


class CsvDownloadContentAsserter(RowContentAsserter):
    def __init__(self, expected_results: list, expected_headings: list[str]):
        super().__init__(expected_results, len(expected_results))
        self.expected_headings = expected_headings

    def row_count(self, resp) -> int:
        return len(self.get_rows(resp))

    def assert_all(self, resp):
        self.assert_headers(resp)
        self.assert_rows_details(resp)

    def assert_rows_details(self, resp):
        for er, row in zip_longest(self.expected_results, self.get_rows(resp)):
            self.assert_row_details(row, er)

    def assert_headers(self, resp):
        assert self.get_rows_including_headers(resp)[0] == self.expected_headings

    def get_rows_including_headers(self, resp) -> list:
        decoded_content = resp.data.decode("utf-8")
        return list(csv.reader(StringIO(decoded_content), delimiter=","))

    def get_rows(self, resp) -> list:
        return self.get_rows_including_headers(resp)[1:]


class TableContentAsserter(RowContentAsserter):
    def get_rows(self, resp) -> list:
        tbody = resp.soup.find_all('tbody')[0]
        return tbody.find_all('tr')


class PanelListContentAsserter(RowContentAsserter):
    def get_rows(self, resp) -> list:
        panel_list = resp.soup.find_all(class_='panel_list')[0]
        return panel_list.find_all('li')


class FlaskViewTester:
    @classmethod
    def setup_class(cls):
        cls.parameters = {}
    
    @pytest.fixture(autouse=True)
    def set_flask_view_tester_fixtures(self, client, faker):
        self.client = client
        self.faker = faker

    @property
    def endpoint(self):
        # Test classes must implement an endpoint property that
        # returns an endpoint as used by the Flask url_for function
        # for example, 'ui.index'
        raise NotImplementedError()

    def url(self, external=True):
        return url_for(self.endpoint, _external=external, **self.parameters)

    def get(self, expected_status_code=http.HTTPStatus.OK):
        result = self.client.get(self.url())
        assert result.status_code == expected_status_code
        return result

    def get_data_from_object(self, object):
        return {k: v for k, v in object.__dict__.items() if not k.startswith('_')}

    def post_object(self, object, expected_status_code=http.HTTPStatus.OK):
        return self.post(data=self.get_data_from_object(object), expected_status_code=expected_status_code)

    def post(self, data=None, expected_status_code=http.HTTPStatus.OK):
        data = data or {}

        result = self.client.post(
            self.url(),
            data=data,
        )

        assert result.status_code == expected_status_code

        return result


class FlaskViewLoggedInTester(FlaskViewTester):
    @pytest.fixture(autouse=True)
    def set_flask_get_view_tester_fixtures(self, loggedin_user):
        self.loggedin_user = loggedin_user


class RequiresLoginGetTester(FlaskViewTester):
    def test__get__requires_login(self):
        assert__requires_login(self.client, self.url(external=False))


class RequiresLoginPostTester(FlaskViewTester):
    def test__get__requires_login(self):
        assert__requires_login(self.client, self.url(external=False), post=True)


class RequiresRoleTester(FlaskViewTester):
    @property
    def user_with_required_role(self):
        # Test classes must implement an user_with_required_role property that
        # returns a user with the required rights
        raise NotImplementedError()

    @property
    def user_without_required_role(self):
        # Test classes must implement an user_with_required_role property that
        # returns a user without the required rights
        raise NotImplementedError()

    def test__get__logged_in_user_without_required_role__permission_denied(self):
        login(self.client, self.faker, self.user_without_required_role)
        self.get(http.HTTPStatus.FORBIDDEN)

    def test__get__logged_in_user_with_required_role__allowed(self):
        login(self.client, self.faker, self.user_with_required_role)
        self.get()



