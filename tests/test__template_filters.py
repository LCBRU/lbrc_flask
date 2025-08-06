import datetime
from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.formatters import format_currency, format_date, format_datetime, format_number, format_yesno, humanize_datetime, humanize_date


def test__yesno_format(client, faker):
    user = login(client, faker)

    resp = client.get(url_for('use_the_template_filters', prev=url_for('search')))

    print(resp.soup)

    assert resp.soup.find('li', id='yesno_format', string='Yes')
    assert resp.soup.find('li', id='datetime_format', string='Wed Dec  5 13:23:34 2007')
    assert resp.soup.find('li', id='date_format', string='05 Dec 2007')
    assert resp.soup.find('li', id='datetime_humanize', string=humanize_datetime(datetime.datetime(2007, 12, 5, 13, 23, 34)))
    assert resp.soup.find('li', id='date_humanize', string=humanize_date(datetime.datetime(2007, 12, 5, 13, 23, 34)))
    assert resp.soup.find('li', id='currency', string='£23.87')
    assert resp.soup.find('li', id='separated_number', string='1,000,765')
    assert resp.soup.find('li', id='blank_if_none__none', string=None)
    assert resp.soup.find('li', id='blank_if_none__not_none', string='Lorem Ipsum')
    assert resp.soup.find('li', id='default_if_none__none', string='On the fence')
    assert resp.soup.find('li', id='default_if_none__not_none', string='Lorem Ipsum')
    assert resp.soup.find('li', id='nbsp', string='Lorem\xa0ipsum\xa0dolor\xa0sit\xa0amet.')
    assert resp.soup.find('li', id='nbsp__none', string=None)
    assert resp.soup.find('li', id='current_year', string=datetime.datetime.now(datetime.UTC).strftime("%Y"))
    assert resp.soup.find('li', id='application_title', string='LBRC Flask')
    assert resp.soup.find('li', id='previous_page', string=url_for('search'))
