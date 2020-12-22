def assert_html_standards(soup):
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


def assert_csrf_token(soup):
    assert (
        soup.find("input", {"name": "csrf_token"}, type="hidden", id="csrf_token") is not None
    )


def assert_basic_navigation(soup, user):
    soup.nav is not None
    soup.nav.find("a", href="/") is not None
    soup.nav.find("a", string=user.full_name) is not None
    soup.nav.find("a", string=user.full_name) is not None
    soup.nav.find("a", href="/change") is not None
    soup.nav.find("a", href="/logout") is not None
