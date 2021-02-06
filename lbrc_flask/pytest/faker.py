import re
from faker.providers import BaseProvider
from lbrc_flask.security import Role, User
from lbrc_flask.forms.dynamic import FieldGroup, Field, FieldType
from lbrc_flask.database import db


class LbrcFlaskFakerProvider(BaseProvider):
    def user_details(self):
        u = User(
            first_name=self.generator.first_name(),
            last_name=self.generator.last_name(),
            email=self.generator.email(),
            active=True,
        )
        return u

    def get_test_user(self, is_admin=False):
        user = self.user_details()

        if is_admin:
            user.roles.append(Role.get_admin())

        db.session.add(user)
        db.session.commit()

        return user


class LbrcDynaicFormFakerProvider(BaseProvider):

    def field_group_details(self, name=None):
        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=10)

        return FieldGroup(
            name=name,
        )

    def field_details(self, field_group=None, field_type=None, order=None, name=None, choices=None, required=None):
        if field_group is None:
            field_group = self.field_group_details()

        if field_type is None:
            field_type = FieldType.get_boolean()

        if order is None:
            order = 1

        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=10)

        result = Field(
            field_group=field_group,
            order=order,
            field_type=field_type,
            field_name=name,
            choices=choices,
        )

        if required is not None:
            result.required = required

        return result

    def get_test_field(self, **kwargs):
        result = self.field_details(**kwargs)

        db.session.add(result)
        db.session.commit()

        return result

    def get_test_field_group(self, **kwargs):
        result = self.field_group_details(**kwargs)

        db.session.add(result)
        db.session.commit()

        return result
