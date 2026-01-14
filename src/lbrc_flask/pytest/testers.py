import pytest
import http
import csv
from io import StringIO
from itertools import zip_longest
from flask import url_for
from lbrc_flask.pytest.asserts import assert__search_html, assert__search_modal_html, assert_html_page_standards, assert_modal_boilerplate, assert__error__required_field_modal, assert__page_navigation__page, assert__error__string_too_long__modal, assert__modal_cancel, assert__modal_save
from lbrc_flask.pytest.html_content import get_records_found
from lbrc_flask.pytest.helpers import login
from lbrc_flask.model import CommonMixin
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from lbrc_flask.pytest.helpers import login


class ResultSet(CommonMixin):
    def __init__(self, expected_results: list):
        self.expected_results = expected_results
        self.results_count = len(expected_results)

    @property
    def results(self):
        return self.expected_results

    @property
    def effective_result_count(self):
        return self.results_count
            
    def effective_results(self):
        return self.expected_results

    @property
    def page_in_range(self):
        return True


class PagedResultSet(ResultSet):
    # Redefine in instance classes for different page sizes
    PAGE_SIZE = 5
    TEST_PAGE_COUNT = 3

    def __init__(self, page: int, expected_results: list):
        self.page = page
        super().__init__(expected_results)

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

    @property
    def page_count(self):
        return ((self.results_count - 1) // self.page_size) + 1
    
    @property
    def page_in_range(self):
        return 1 <= self.page <= self.page_count

    @property
    def items_on_previous_pages(self):
        return ((self.page - 1) * self.page_size)

    @property
    def effective_result_count(self):
        if self.page < self.page_count:
            return self.page_size
        elif self.page > self.page_count:
            return 0
        else:
            return self.results_count - self.items_on_previous_pages
        
    def effective_results(self):
        return self.expected_results[self.items_on_previous_pages:self.items_on_previous_pages + self.effective_result_count]


class HtmlPageContentAsserter:
    def __init__(self, loggedin_user):
        self.loggedin_user = loggedin_user

    def assert_all(self, resp):
        assert_html_page_standards(resp, self.loggedin_user)


@dataclass
class ModalContentAsserter:
    has_save_button: bool = False
    has_cancel_button: bool = True

    def assert_all(self, resp):
        assert_modal_boilerplate(resp.soup)

        if self.has_save_button:
            assert__modal_save(resp.soup)
        if self.has_cancel_button:
            assert__modal_cancel(resp.soup)


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
    def __init__(self, url: str, paged_result_set: PagedResultSet):
        self.url=url
        self.paged_result_set = paged_result_set

    def assert_all(self, resp):
        print('Expected results', self.paged_result_set.results_count)
        print('Record Found', get_records_found(resp.soup))
        assert self.paged_result_set.results_count == get_records_found(resp.soup)

        self.assert_paginator(resp)
    
    def assert_paginator(self, resp):
        if self.paged_result_set.page_in_range:
            paginator = resp.soup.find('nav', 'pagination')

            if self.paged_result_set.page_count > 1:
                assert paginator is not None
                assert__page_navigation__page(self.url, paginator, self.paged_result_set.page_count, self.paged_result_set.page)
            else:
                assert paginator is None


class RowContentAsserter:
    def __init__(self, result_set: ResultSet):
        self.result_set = result_set

    def row_count(self, resp) -> int:
        return len(self.get_rows(resp))

    def assert_all(self, resp):
        if self.result_set.page_in_range:
            assert self.result_set.effective_result_count == self.row_count(resp)
            self.assert_rows_details(resp)

    def assert_rows_details(self, resp):
        for er, row in zip_longest(self.result_set.effective_results(), self.get_rows(resp)):
            self.assert_row_details(row, er)

    def assert_row_details(self, row, expected_result):
        ...


class CsvDownloadContentAsserter(RowContentAsserter):
    def __init__(self, expected_results: list, expected_headings: list[str]):
        super().__init__(ResultSet(expected_results=expected_results))
        self.expected_headings = expected_headings

    def row_count(self, resp) -> int:
        return len(self.get_rows(resp))

    def assert_all(self, resp):
        self.assert_headers(resp)
        self.assert_rows_details(resp)

    def assert_rows_details(self, resp):
        for er, row in zip_longest(self.result_set.expected_results, self.get_rows(resp)):
            self.assert_row_details(row, er)

    def actual_headers(self, resp) -> list:
        return self.get_rows_including_headers(resp)[0]
    
    def assert_headers(self, resp):
        assert self.actual_headers(resp) == self.expected_headings

    def get_rows_including_headers(self, resp) -> list:
        decoded_content = resp.data.decode("utf-8")
        return list(csv.reader(StringIO(decoded_content), delimiter=","))

    def get_rows(self, resp) -> list:
        headers = self.actual_headers(resp)

        for v in self.get_rows_including_headers(resp)[1:]:
            yield dict(zip(headers, v))


class HtmlListContentAsserter(RowContentAsserter):
    def get_container(self, resp):
        raise NotImplementedError()
    
    @property
    def row_selector(self):
        raise NotImplementedError()
    
    def get_rows(self, resp) -> list:
        container = self.get_container(resp)
        return container.select(self.row_selector)


class TableContentAsserter(HtmlListContentAsserter):
    def get_container(self, resp):
        return resp.soup.find_all('tbody')[0]

    @property
    def row_selector(self):
        return 'tr'


class PanelListContentAsserter(HtmlListContentAsserter):
    def get_container(self, resp):
        return resp.soup.find_all(class_='panel_list')[0]

    @property
    def row_selector(self):
        return 'li'


class FlaskViewTester:
    @classmethod
    def setup_method(cls):
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

    @property
    def request_aserters(self):
        return []

    def login(self, user):
        login(self.client, self.faker, user)

    def url(self, external=True):
        return url_for(self.endpoint, _external=external, **self.parameters)

    def get(self, expected_status_code=http.HTTPStatus.OK):
        print(self.url())
        result = self.client.get(self.url())
        print(result.soup)
        print(result.status_code, expected_status_code)
        assert result.status_code == expected_status_code

        for a in self.request_aserters:
            a.assert_all(result)

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

        print(result.status_code, expected_status_code)
        assert result.status_code == expected_status_code

        for a in self.request_aserters:
            a.assert_all(result)

        return result


class FlaskViewLoggedInTester(FlaskViewTester):
    def user_to_login(self, faker):
        return faker.user().get_in_db()

    @pytest.fixture(autouse=True)
    def set_flask_get_view_tester_fixtures(self, client, faker):
        self.loggedin_user = self.user_to_login(faker)
        login(client, faker, self.loggedin_user)


class ReportsPageTester(FlaskViewLoggedInTester):
    def assert_all(self, resp):
        SearchContentAsserter().assert_all(resp)
        HtmlPageContentAsserter(loggedin_user=self.loggedin_user).assert_all(resp)


class IndexTester(FlaskViewLoggedInTester):
    @property
    def content_asserter(self) -> RowContentAsserter:
        return TableContentAsserter
    
    def assert_all(self, page_count_helper: PagedResultSet, resp):
        PageContentAsserter(
            url=self.url(external=False),
            paged_result_set=page_count_helper,
        ).assert_all(resp)

        self.content_asserter(
            result_set=page_count_helper,
        ).assert_all(resp)

        SearchContentAsserter().assert_all(resp)
        HtmlPageContentAsserter(loggedin_user=self.loggedin_user).assert_all(resp)


class RequiresLoginTester(FlaskViewTester):
    @property
    def request_method(self):
        return self.get
    
    def test__requires_login(self):
        self.assert_response()

    def assert_response(self):
        # This should be a call to assert__redirect, but
        # flask_login or flask_security is adding the
        # endpoint parameters as querystring arguments as well
        # as having them in the `next` parameter  
        response = self.request_method(expected_status_code=http.HTTPStatus.FOUND)

        login_loc = urlparse(url_for('security.login', next=self.url(external=False)))
        resp_loc = urlparse(response.location)

        assert resp_loc.path == login_loc.path
        assert parse_qs(resp_loc.query).get('next') == parse_qs(login_loc.query).get('next')


class RequiresRoleTester(FlaskViewTester):
    @property
    def request_method(self):
        return self.get
    
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
        self.login(self.user_without_required_role)
        self.request_method(expected_status_code=http.HTTPStatus.FORBIDDEN)

    def test__get__logged_in_user_with_required_role__allowed(self):
        self.login(self.user_with_required_role)
        self.request_method()
