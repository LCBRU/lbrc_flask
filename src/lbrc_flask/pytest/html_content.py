import re
from lbrc_flask.validators import is_integer


def get_records_found(soup):
    pagination_summary = soup.find(class_="pagination_summary")

    count = re.findall(r"(\d+) found", pagination_summary.get_text())
    
    if count:
        if is_integer(count[0]):
            return int(count[0])
    
    return 0
