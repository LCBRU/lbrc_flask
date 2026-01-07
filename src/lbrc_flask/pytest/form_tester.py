from dataclasses import dataclass, field
from lbrc_flask.pytest.asserts import assert__input_checkbox, assert__input_date, assert__input_radio, assert__input_text, assert__input_textarea, assert__search_html, assert_csrf_token


@dataclass(kw_only=True)
class FormTesterField:
    field_name: str
    field_title: str
    is_mandatory: bool = False

    def assert_input(self):
        raise NotImplementedError

    @property
    def is_mandatory_add(self):
        return self.is_mandatory

    @property
    def is_mandatory_edit(self):
        return self.is_mandatory


@dataclass(kw_only=True)
class FormTesterTextField(FormTesterField):
    def assert_input(self, soup):
        assert__input_text(soup, self.field_name)


@dataclass(kw_only=True)
class FormTesterSearchField:
    has_clear: bool = True

    @property
    def field_name(self):
        return 'search'

    def assert_input(self, soup):
        assert__search_html(soup, has_clear=self.has_clear)

@dataclass(kw_only=True)
class FormTesterTextAreaField(FormTesterField):
    def assert_input(self, soup):
        assert__input_textarea(soup, self.field_name)


@dataclass(kw_only=True)
class FormTesterDateField(FormTesterField):
    def assert_input(self, soup):
        assert__input_date(soup, self.field_name)


@dataclass(kw_only=True)
class FormTesterRadioField(FormTesterField):
    options: dict[str: str] = field(default_factory=dict)

    def assert_input(self, soup):
        assert__input_radio(soup, self.field_name, self.options)

    @property
    def is_mandatory_edit(self):
        return False


@dataclass(kw_only=True)
class FormTesterCheckboxField(FormTesterField):
    def assert_input(self, soup):
        assert__input_checkbox(soup, self.field_name)

    @property
    def is_mandatory_edit(self):
        return False


class FormTester:
    def __init__(self, fields: list[FormTesterField], has_csrf=False):
        self.fields: dict[str, FormTesterField] = {f.field_name: f for f in fields}
        self.has_csrf = has_csrf
    
    @property
    def mandatory_fields_add(self):
        return list(filter(lambda x: x.is_mandatory_add, self.fields.values()))

    @property
    def mandatory_fields_edit(self):
        return list(filter(lambda x: x.is_mandatory_edit, self.fields.values()))

    @property
    def string_fields(self):
        return list(filter(lambda x: isinstance(x, FormTesterTextField), self.fields.values()))

    def assert_inputs(self, soup):
        for f in self.fields.values():
            f.assert_input(soup)

    def assert_all(self, resp):
        if self.has_csrf:
            assert_csrf_token(resp.soup)
        self.assert_inputs(resp.soup)


