import datetime
from dateutil.relativedelta import relativedelta
from faker.providers import BaseProvider
from lbrc_flask.security import Role, User
from lbrc_flask.forms.dynamic import FieldGroup, Field, FieldType
from lbrc_flask.database import db
from random import randint, choice, randrange
from lbrc_flask.validators import (
    is_invalid_nhs_number,
    calculate_nhs_number_checksum,
)


class LbrcFlaskFakerProvider(BaseProvider):
    def user_details(self):
        u = User(
            first_name=self.generator.first_name(),
            last_name=self.generator.last_name(),
            username=self.generator.pystr(min_chars=5, max_chars=10),
            email=self.generator.email(),
            active=True,
        )
        return u

    def get_test_user(self, is_admin=False, rolename=None):
        user = self.user_details()

        if is_admin:
            user.roles.append(Role.get_admin())
        
        if rolename:
            user.roles.append(Role.query.filter(Role.name == rolename).one())

        db.session.add(user)
        db.session.commit()

        return user

    def role_details(self):
        return Role(
            name=self.generator.first_name(),
        )

    def get_test_role(self):
        role = self.role_details()

        db.session.add(role)
        db.session.commit()

        return role

    def nhs_number(self):
        while True:  
            number = str(randint(100_000_000, 999_999_999))
            whole_num = f'{number}{calculate_nhs_number_checksum(number)}'

            if(not is_invalid_nhs_number(whole_num)):  
                return whole_num

    def invalid_nhs_number(self):
        return 'ABC'

    def uhl_system_number(self):
        prefix = choice(['S', 'R', 'F', 'G', 'U', 'LB', 'RTD'])
        return f'{prefix}{randint(1_000_000, 9_999_999)}'

    def invalid_uhl_system_number(self):
        return 'ABC'

    def gp_practice_code(self):
        prefix = choice(['ABCDEFGHIJKLMNOPQRSTUVWXYZ'])
        return f'{prefix}{randint(10_000, 99_999)}'

    def person_details(self):
        if not randint(0, 1):
            return self.female_person_details()
        else:
            return self.male_person_details()

    def female_person_details(self):
        return {
            **{
                'family_name': self.generator.last_name_female(),
                'given_name': self.generator.first_name_female(),
                'middle_name': self.generator.first_name_female(),
                'gender': 'F',
                'title': self.generator.prefix_female(),
            },
            **self._generic_person_details(),
        }

    def male_person_details(self):
        return {
            **{
                'family_name': self.generator.last_name_male(),
                'given_name': self.generator.first_name_male(),
                'middle_name': self.generator.first_name_male(),
                'gender': 'M',
                'title': self.generator.prefix_male(),
            },
            **self._generic_person_details(),
        }

    def _generic_person_details(self):

        today = datetime.date.today()
        dob = self._random_date(today - relativedelta(years=75), today - relativedelta(years=40))

        if randint(0, 10):
            dod = None
            is_deceased = False
        else:
            dod = self._random_date(dob, today)
            is_deceased = True

        return {
            'date_of_birth': dob,
            'date_of_death': dod,
            'is_deceased': is_deceased,
            'address': self.generator.address(),
            'current_gp_practice_code': self.gp_practice_code(),
            'nhs_number': self.generator.nhs_number(),
            'uhl_system_number': self.generator.uhl_system_number(),
            'postcode': self.generator.postcode(),
        }
    
    def _random_date(self, start_date, end_date):
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = randrange(days_between_dates)
        return start_date + datetime.timedelta(days=random_number_of_days)


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
