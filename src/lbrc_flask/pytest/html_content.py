import re
from lbrc_flask.validators import is_integer


def get_records_found(soup):
    pagination_summary = soup.find(class_="pagination_summary")

    count = re.findall("(\d+) found", pagination_summary.get_text())
    
    if count:
        if is_integer(count[0]):
            return int(count[0])


def get_table_rows_found(soup):
    tbody = soup.find_all('tbody')[0]
    trs = tbody.find_all('tr')

    return len(trs)
