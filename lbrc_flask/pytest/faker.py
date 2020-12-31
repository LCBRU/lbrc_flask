from faker.providers import BaseProvider
from lbrc_flask.security import User
from lbrc_flask.forms.dynamic import FieldGroup, Field, FieldType


class LbrcFlaskFakerProvider(BaseProvider):
    def user_details(self):
        u = User(
            first_name=self.generator.first_name(),
            last_name=self.generator.last_name(),
            email=self.generator.email(),
            active=True,
        )
        return u


class LbrcDynaicFormFakerProvider(BaseProvider):

    def field_group_details(self, name=None):
        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=10)

        return FieldGroup(
            name=name,
        )

    def field_details(self, field_group=None, field_type=None, order=None, name=None, choices=None):
        if field_group is None:
            field_group = self.field_group_details()

        if field_type is None:
            field_type = FieldType.get_boolean()

        if order is None:
            order = 1

        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=10)

        return Field(
            field_group=field_group,
            order=order,
            field_type=field_type,
            field_name=name,
            choices=choices,
        )
