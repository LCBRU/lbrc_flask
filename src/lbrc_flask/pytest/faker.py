import datetime
import io
from openpyxl import Workbook
from dateutil.relativedelta import relativedelta
from faker.providers import BaseProvider
from lbrc_flask.security import Role, User
from lbrc_flask.forms.dynamic import FieldGroup, Field, FieldType
from lbrc_flask.database import db
from random import randint, choice, randrange, choices, sample
from lbrc_flask.validators import (
    is_invalid_nhs_number,
    calculate_nhs_number_checksum,
)
from lbrc_flask.string_functions import camel_case_split
from sqlalchemy import select, func
from faker import Faker


class FakeCreator():
    @property
    def cls(self):
        raise NotImplementedError

    def __init__(self, provider):
        self.provider = provider
        # The line below causes unique to fail because a
        # different faker is created each time, despite being for the
        # same generator.  Use singleton instead?
        self.faker = Faker("en_GB", generator=provider.generator)

    def get(self, **kwargs):
        return None

    def get_in_db(self, **kwargs):
        x = self.get(**kwargs)

        db.session.add(x)
        db.session.commit()

        return x
    
    def count_in_db(self):
        return db.session.execute(select(func.count(self.cls.id))).scalar()

    def get_list_in_db(self, item_count, **kwargs):
        results = []

        for _ in range(item_count):
            result = self.get(**kwargs)
            results.append(result)
            db.session.add(result)
            db.session.commit()

        return results

    def choice_from_db(self, **kwargs):
        return choice(list(db.session.execute(select(self.cls)).scalars()))

    def choices_from_db(self, k=1, **kwargs):
        return sample(list(db.session.execute(select(self.cls)).scalars()), k)

    def get_value_or_get(self, source, key, from_db=False):
        if key in source:
            return source[key]
        elif from_db:
            return self.choice_from_db()
        else:
            return self.get()

    def get_value_or_default(self, source, key, default=None):
        if key in source:
            return source[key]
        else:
            return default
    

class LookupFakeCreator(FakeCreator):
    def __init__(self, provider, cls):
        self.cls = cls
        super().__init__(provider)

    def get(self, **kwargs):
        result = self.cls(
            name=kwargs.get('name', self.faker.pystr(min_chars=1, max_chars=100))
        )

        return result

    @staticmethod    
    def class_name_for_class(cls):
        parts = camel_case_split(cls.__name__)
        return ' '.join([p.lower() for p in parts])

    def class_name(self):
        return LookupFakeCreator.class_name_for_class(self.cls)

    def lookup_name(self, i):
        return f"{self.class_name().title()} {i}"

    def get_n_in_db(self, n):
        result = []

        for i in range(1, n+1):
            result.append(self.get_in_db(name=self.lookup_name(i)))

        return result


class LookupProvider(BaseProvider):
    LOOKUPS = []

    class CreatorProviderMethod():
        def __init__(self, cls):
            self.cls = cls
        
        def __call__(self, *args, **kwds):
            return LookupFakeCreator(self, self.cls)

        def method_name(self):
            return self().class_name().replace(' ', '_')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creators = {}

        for L in self.LOOKUPS:
            cp = self.CreatorProviderMethod(L)
            setattr(self, cp.method_name(), cp)
            self.creators[L] = cp()

    def create_standard_lookups(self):
        result = {}

        for L in self.LOOKUPS:
            creator = LookupFakeCreator(self, L)
            result[creator.class_name()] = creator.get_n_in_db(5)
        
        return result
    
    def lookup_creator(self, cls):
        return self.creators[cls]

    def lookup_all(self, cls):
        return list(db.session.execute(select(cls)).scalars())

    def lookup_select_choices(self, cls):
        lookups = db.session.execute(
            select(cls).order_by(cls.name)
        ).scalars()
        return [('0', '')] + [(str(l.id), l.name) for l in lookups]


class LbrcFlaskFakerProvider(BaseProvider):
    def __init__(self, *args, **kwargs):
        self.user_class = User
        super().__init__(*args, **kwargs)
    
    def set_userclass(self, user_class):
        self.user_class = user_class

    def user_details(self):
        u = self.user_class(
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
        prefix = choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return f'{prefix}{randint(10_000, 99_999)}'

    def orcid(self):
        return f'{randint(0, 9_999):04d}-{randint(0, 9_999):04d}-{randint(0, 9_999):04d}-{randint(0, 9_999):04d}'

    def local_rec_number(self):
        midfix = ''.join(choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        return f'{randint(0, 99):02d}/{midfix}/{randint(0, 9_999):04d}'

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


class FakeXlsxWorksheet:
    def __init__(self, name, headers, data, headers_on_row=1):
        self.name = name
        self.headers = headers
        self.data = data
        self.headers_on_row = headers_on_row

    def create_worksheet(self, workbook: Workbook):
        if self.name is None:
            ws1 = workbook.active
        else:
            ws1 = workbook.create_sheet(self.name)

        for _ in range(1, self.headers_on_row):
            ws1.append([])

        ws1.append(list(self.headers))

        for d in self.data:
            row = []
            for h in self.headers:
                row.append(d.get(h.lower(), ''))
            ws1.append(row)


class FakeXlsxFile():
    def __init__(self, filename: str, worksheets: list[FakeXlsxWorksheet]):
        self.filename = filename
        self.worksheets: list[FakeXlsxWorksheet] = worksheets

    def get_iostream(self):
        workbook= Workbook()

        for ws in self.worksheets:
            ws.create_worksheet(workbook)

        result = io.BytesIO()
        workbook.save(result)

        return result.getvalue()


class LbrcFileProvider(BaseProvider):
    def xlsx(self, headers, data, filename=None, worksheet=None, headers_on_row=1):
        headers = list(headers)
        filename = filename or self.generator.file_name(extension='xlsx')

        if worksheet is None:
            worksheet = FakeXlsxWorksheet(
                name=None,
                headers=headers,
                data=data,
                headers_on_row=headers_on_row,
            )

        return FakeXlsxFile(
            filename=filename,
            worksheets=[worksheet],
        )

    def data_from_definition(self, columns_definition: dict, rows=10):
        data = []
        for _ in range(rows):
            row = {}
            for h, definition in columns_definition.items():
                if definition['type'] == 'int':
                    row[h] = self.generator.pyint()
                elif definition['type'] == 'str':
                    min_length = definition.get('min_length', 1)
                    max_length = definition.get('max_length', 10)
                    row[h] = self.generator.pystr(min_chars=min_length, max_chars=max_length)
                elif definition['type'] == 'date':
                    row[h] = self.generator.date()
                        
            data.append(row)

        return data


class UserCreator(FakeCreator):
    cls = User

    def get(self, **kwargs):
        if (first_name := kwargs.get('first_name')) is None:
            first_name = self.faker.first_name()

        if (last_name := kwargs.get('last_name')) is None:
            last_name = self.faker.last_name()

        if (username := kwargs.get('username')) is None:
            username = self.faker.pystr(min_chars=5, max_chars=10).lower()

        if (email := kwargs.get('email')) is None:
            email = self.faker.unique.email()

        if (active := kwargs.get('active')) is None:
            active = True

        return self.cls(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            active=active,
        )


class UserProvider(BaseProvider):
    def user(self):
        return UserCreator(self)


class RoleCreator(FakeCreator):
    cls = Role

    def get(self, **kwargs):
        if (name := kwargs.get('name')) is None:
            name = self.faker.pystr(min_chars=5, max_chars=10).lower()

        return Role(
            name=name,
        )


class RoleProvider(BaseProvider):
    def role(self):
        return RoleCreator(self)


class FieldGroupCreator(FakeCreator):
    cls = FieldGroup

    def get(self, **kwargs):
        if (name := kwargs.get('name')) is None:
            name = self.faker.pystr(min_chars=5, max_chars=10).upper()

        return FieldGroup(name=name.upper())


class FieldCreator(FakeCreator):
    cls = Field

    def get(self, **kwargs):        
        if (field_group := kwargs.get('field_group')) is None:
            field_group = self.faker.field_group().get()

        if (field_type := kwargs.get('field_type')) is None:
            field_type = choice(FieldType.all_field_types())

        if (field_name := kwargs.get('field_name')) is None:
            field_name = self.faker.sentence(nb_words=randint(1, 5)).rstrip('.').title()

        if (allowed_file_extensions := kwargs.get('allowed_file_extensions')) is None:
            allowed_file_extensions = self.faker.file_extension()

        if (required := kwargs.get('required')) is None:
            required = False

        if (reportable := kwargs.get('reportable')) is None:
            reportable = choice([True, False, False, False, False, False])

        f = Field(
            field_group=field_group,
            field_type=field_type,
            field_name=field_name,
            allowed_file_extensions=allowed_file_extensions,
            required=required,
            reportable=reportable,
        )

        if (order := kwargs.get('order')) is not None:
            f.order = order
        else:
            f.order = 1

        if (choices := kwargs.get('choices')) is not None:
            f.choices = choices

        if (max_length := kwargs.get('max_length')) is not None:
            f.max_length = max_length

        if (allowed_file_extensions := kwargs.get('allowed_file_extensions')) is not None:
            f.allowed_file_extensions = allowed_file_extensions

        return f


class FieldsProvider(BaseProvider):
    def field(self):
        return FieldCreator(self)

    def field_group(self):
        return FieldGroupCreator(self)


