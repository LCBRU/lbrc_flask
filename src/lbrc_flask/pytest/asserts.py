import http
import re
from urllib.parse import urlparse, parse_qs
from flask import url_for
from lbrc_flask.url_helpers import update_querystring


def _assert_html_standards(soup):
    assert soup.html is not None
    assert soup.html["lang"] == "en"
    assert soup.head is not None
    assert (
        soup.find(
            lambda tag: tag.name == "meta"
            and tag.has_attr("charset")
            and tag["charset"] == "utf-8"
        )
        is not None
    )
    assert soup.title is not None
    assert soup.body is not None


def _assert_csrf_token(soup):
    assert (
        soup.find("input", {"name": "csrf_token"}, type="hidden", id="csrf_token") is not None
    )


def _assert_modal_boilerplate(soup):
    modal = soup.find(class_="modal") 
    assert modal is not None
    assert modal.find(class_="modal-underlay") is not None
    assert modal.find(class_="modal-content container") is not None


def _assert_basic_navigation(soup, user):
    assert soup.nav is not None
    assert soup.nav.find("a", href="/") is not None
    assert soup.nav.find("a", string=user.full_name) is not None
    if not (user.ldap_user or False):
        assert soup.nav.find("a", href="/change") is not None
    assert soup.nav.find("a", href="/logout") is not None


def assert__error__message(soup, message):
    error_list = soup.find("ul", class_="errors")
    errors = "\n".join([d.text for d in error_list.find_all("li")])
    rx = re.compile(message, re.IGNORECASE)
    assert rx.search(errors) is not None


def assert__error__required_field(soup, field_name):
    assert__error__message(soup, "Error in the {} field - This field is required.".format(field_name))


def assert__modal_create_button(soup, text=None, url=None, class_=None):
    params = {}

    if text:
        params['string'] = text

    if class_:
        params['class_'] = class_

    assert__modal_button(soup.find('a', **params), url)


def assert__modal_button(button, url):
    assert button is not None
    assert button.attrs['hx-get'] == url
    assert button.attrs['hx-target'] == "body"
    assert button.attrs['hx-swap'] == "beforeend"
    assert button.attrs['href'] == "javascript:;"


def assert__htmx_post_button(soup, text, url, has_confirm=True):
    button = soup.find('a', string=text)
    assert button is not None
    assert button.attrs['hx-post'] == url

    if has_confirm:
        assert 'hx-confirm' in button.attrs

    assert button.attrs['href'] == "javascript:;"


def assert__modal_cancel(soup):
    button = soup.find('a', string='Cancel')
    assert button is not None
    assert button.attrs['href'] == "javascript:;"


def assert__modal_save(soup):
    button = soup.find('button', string='Save', type='submit')
    assert button is not None


def assert__formaction_button(soup, text, url, method=None):
    button = soup.find('button', string=text)
    assert button is not None
    assert button.attrs['formaction'] == url

    if method:
        assert button.attrs['formmethod'] == method


def assert__redirect(response, endpoint=None, url=None, **kwargs):
    assert response.status_code == http.HTTPStatus.FOUND

    if endpoint:
        if urlparse(response.location).netloc:
            url = url_for(endpoint, _external=True, **kwargs)
        else:
            url = url_for(endpoint, _external=False, **kwargs)

    url_loc = urlparse(url)
    resp_loc = urlparse(response.location)
    
    print(f'{resp_loc=} {url_loc=}')

    if url:
        print(f'{response.location=} {url=}')
        assert resp_loc.path == url_loc.path


def assert__refresh_response(response):
    assert response.status_code == http.HTTPStatus.OK
    assert 'HX-Refresh' in response.headers
    assert response.headers['HX-Refresh'] == 'true'


def assert__requires_login(client, url, post=False):
    if post:
        response = client.post(url)
    else:
        response = client.get(url)

    # This should be a call to assert__redirect, but
    # flask_login or flask_security is adding the
    # endpoint parameters as querystring arguments as well
    # as having them in the `next` parameter  
    assert response.status_code == http.HTTPStatus.FOUND

    login_loc = urlparse(url_for('security.login', next=url))
    resp_loc = urlparse(response.location)

    print(f"{resp_loc.path=}, {login_loc.path=}")
    assert resp_loc.path == login_loc.path
    print(f"{parse_qs(resp_loc.query).get('next')=}, {parse_qs(login_loc.query).get('next')=}")
    assert parse_qs(resp_loc.query).get('next') == parse_qs(login_loc.query).get('next')


def assert__requires_role(client, url, post=False):
    if post:
        resp = client.post(url)
    else:
        resp = client.get(url)

    assert resp.status_code == http.HTTPStatus.FORBIDDEN



def assert__search_html(soup, clear_url):
    assert soup.find('input', id="search") is not None
    assert soup.find('a', string="Clear Search", href='?') is not None
    assert soup.find('button', type="submit", string="Search") is not None


def assert__select(soup, id, options, multiselect=False):
    select = soup.find('select', id=id)
    assert select is not None
    if multiselect:
        assert 'multiple' in select.attrs
    else:
        assert 'multiple' not in select.attrs

    found_options = [(o.attrs['value'], o.text) for o in select.find_all('option')]

    assert found_options == options


def assert__yesno_select(soup, id):
    select = soup.find('select', id=id)
    assert select is not None

    found_options = [(o.attrs['value'], o.text) for o in select.find_all('option')]

    assert found_options == [('', ''), ('True', 'Yes'), ('False', 'No')]


def assert__input_date(soup, id):
    control = soup.find('input', id=id)
    assert control is not None
    assert control.attrs['type'] == "date"


def assert__input_number(soup, id):
    control = soup.find('input', id=id)
    assert control is not None
    assert control.attrs['type'] == "number"


def assert__input_text(soup, id):
    control = soup.find('input', id=id)
    assert control is not None
    assert control.attrs['type'] == "text"


def assert__input_file(soup, id):
    control = soup.find('input', id=id)
    assert control is not None
    assert control.attrs['type'] == "file"


def assert__input_checkbox(soup, id):
    control = soup.find('input', id=id)
    assert control is not None
    assert control.attrs['type'] == "checkbox"


def assert__input_textarea(soup, id):
    control = soup.find('textarea', id=id)
    assert control is not None


def get_and_assert_standards(client, url, user, has_form=False, has_navigation=True):
    resp = client.get(url)

    _assert_html_standards(resp.soup)

    if has_navigation:
        _assert_basic_navigation(resp.soup, user)

    if has_form:
        _assert_csrf_token(resp.soup)

    return resp


def get_and_assert_standards_modal(client, url, user, has_form=False, has_navigation=True):
    resp = client.get(url)

    _assert_modal_boilerplate(resp.soup)

    if has_form:
        _assert_csrf_token(resp.soup)

    return resp


def assert__page_navigation(client, endpoint, parameters, items, page_size=5, form=None):
    page_count = ((items - 1) // page_size) + 1

    if form is not None:
        form_fields = filter(lambda x: x.name not in ['page', 'csrf_token'] and x.data, form)
        params = {**parameters, **{f.name: f.data for f in form_fields}}
    else:
        params = {**parameters}

    url = url_for(endpoint, **params)

    if page_count > 1:
        assert__page_navigation__pages(url, client, page_count, form)
    else:
        resp = client.get(url)
        paginator = resp.soup.find('nav', 'pagination')
        assert paginator is None


def assert__page_navigation__pages(url, client, page_count, form):
    for current_page in range(1, page_count + 1):
        resp = client.get(update_querystring(url, {'page': current_page}))
        paginator = resp.soup.find('nav', 'pagination')

        assert__page_navigation__page(url, paginator, page_count, current_page)


def assert__page_navigation__page(url, paginator, page_count, current_page):
    assert paginator is not None

    assert__page_navigation__link_exists(paginator, 'Previous', url, current_page - 1, current_page, page_count)
    assert__page_navigation__link_exists(paginator, 'Next', url, current_page + 1, current_page, page_count)

    assert__page_navigation__link_exists(paginator, 1, url, 1, current_page, page_count)
    assert__page_navigation__link_exists(paginator, page_count, url, page_count, current_page, page_count)

    for page in range(max(current_page - 2, 2), min(current_page + 3, page_count - 1)):
        assert__page_navigation__link_exists(paginator, page, url, page, current_page, page_count)


def assert__page_navigation__link_exists(paginator, string, url, page, current_page, page_count):
    if page == current_page:
        assert paginator.find('span', string=string) is not None
        return

    link = paginator.find('a', string=string)

    assert link is not None

    if 0 < page <= page_count:
        assert__urls_the_same(update_querystring(url, {'page': page}), link['href'])
    else:
        assert 'href' not in link


def assert__urls_the_same(url1, url2):
    assert update_querystring(url1, {}) == update_querystring(url2, {})


def assert__flash_messages_contains_error(client):
    with client.session_transaction() as session:
        return dict(session['_flashes']).get('error') is not None

