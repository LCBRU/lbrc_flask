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

    def field_group_details(self):
        return FieldGroup(
            name=self.generator.pystr(min_chars=5, max_chars=10),
        )

    def field_details(self):
        return Field(
            field_group=self.field_group_details(),
            order=1,
            field_type=FieldType.get_boolean(),
            field_name=self.generator.pystr(min_chars=5, max_chars=10),
        )
