import datetime
from lbrc_flask.pytest.faker import FieldGroupProvider, FieldProvider, RoleProvider, UserProvider
from lbrc_flask.requests import get_value_from_all_arguments
from lbrc_flask.forms import DataListField, FlashingForm, SearchForm, FileField, Unique
from lbrc_flask.forms.dynamic import Field, FieldGroup, FormBuilder, create_field_types, init_dynamic_forms
import pytest
from flask import Flask, Blueprint, render_template_string, url_for, redirect, request, abort
from flask_login import login_required
from lbrc_flask.config import BaseTestConfig
from lbrc_flask import init_lbrc_flask
from lbrc_flask.database import db
from lbrc_flask.security import current_user_id, init_security, User, Role, system_user_id, get_user_from_username, get_admin_user, get_users_for_role, add_user_to_role, must_be_admin
from wtforms import StringField
from lbrc_flask.pytest.fixtures import *
from lbrc_flask.export import excel_download, csv_download, pdf_download
from lbrc_flask.json import validate_json
from lbrc_flask.security import init_roles, init_users
from sqlalchemy import select


class TestForm(FlashingForm):
    name_options = DataListField()
    name = StringField('Name')
    last_name = StringField(
        'last_name',
        validators=[Unique(User, User.last_name)],
    )
    upload = FileField(
        'Participant File',
        accept=[
            '.cdr',
            '.png',
            '.csv',
        ],
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name_options.choices = ['One', 'Two', 'Tree']


@pytest.fixture(scope="function", autouse=True)
def standard_lookups(client, faker):
    return create_field_types()


@pytest.fixture(scope="function", autouse=True)
def init_security_stuff(client, faker):
    init_roles([])
    init_users()


@pytest.fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(RoleProvider)
    result.add_provider(UserProvider)
    result.add_provider(FieldProvider)
    result.add_provider(FieldGroupProvider)

    yield result


@pytest.fixture(scope="function")
def app():
    app = Flask(__name__)
    app.config.from_object(BaseTestConfig)
    ui_blueprint = Blueprint("ui", __name__)


    @ui_blueprint.route('/')
    @login_required
    def index():
        return render_template_string('''
            {% extends "lbrc/page.html" %}
            
            {% block page_content %}
                <nav class="main_menu">
                    <div class="container">
                    <menu>
                        <li><a href="{{url_for('ui.index')}}">Home</a></li>
                    </menu>
                    <menu>
                        {% if current_user.is_admin %}
                        <li>
                            <a>Admin</a>
                            <menu>
                            <li><a href="{{url_for('admin.index')}}">Maintenance</a></li>
                            <li><a href="{{url_for('ui.refresh_file_size')}}">Refresh File Size</a></li>
                            </menu>
                        </li>
                        {% endif %}
                        <li>
                        <a>{{ current_user.full_name }}</a>
                        <menu>
                            {% if not current_user.ldap_user %}
                                <li><a href="{{ url_for_security('change_password') }}">Change Password</a></li>
                            {% endif %}
                            <li><a href="{{ url_for_security('logout') }}">Log Out</a></li>
                        </menu>
                        </li>
                    </menu>
                    </div>
                </nav>
            {% endblock %}
        ''')

    with app.app_context():
        init_lbrc_flask(app, title='LBRC Flask')
        init_security(app, user_class=User, role_class=Role)
        init_dynamic_forms(app)
        app.register_blueprint(ui_blueprint)

    @app.route('/form/<int:field_group_id>', methods=["GET", "POST"])
    def form(field_group_id):

        fg = db.get_or_404(FieldGroup, field_group_id)
        fb = FormBuilder(field_group=fg)

        form = fb.get_form()()

        if form.validate_on_submit():
            return redirect(url_for("ui.index"))

        return render_template_string('''
        
        {% extends "lbrc/page.html" %}
        {% from "lbrc/form_macros.html" import render_form_fields %}

        {% block page_content %}

            <form>
                <fieldset>
                    {{ render_form_fields(form) }}
                </fieldset>
            </form>

        {% endblock %}

        ''', form=form)

    @app.route('/search/', methods=["GET", "POST"])
    def search():
        search_form = SearchForm()

        return render_template_string('''
        
        {% extends "lbrc/page.html" %}
        {% from "lbrc/form_macros.html" import render_form_fields %}

        {% block page_content %}
            <form action="{{ url_for('search') }}" method="GET" enctype="multipart/form-data">
                <fieldset>
                    {{ render_form_fields(search_form) }}
                </fieldset>    
            </form>    
        {% endblock %}

        ''', search_form=search_form)

    @app.route('/test_form/', methods=["GET", "POST"])
    def test_form():
        form = TestForm()
        has_a_name=''
        not_exists=''
        valid=False

        if form.validate_on_submit():
            valid=True
            has_a_name = form.has_value("name")
            not_exists = form.has_value("not_exists")

        return render_template_string('''
        
        {% extends "lbrc/page.html" %}
        {% from "lbrc/form_macros.html" import render_form_fields, render_button_bar %}

        {% block page_content %}

            <h1 id="has_a_name">{{has_a_name}}</h1>
            <h1 id="not_exists">{{not_exists}}</h1>
            <h1 id="valid">{{valid}}</h1>

            <form action="test_form" method="POST" enctype="multipart/form-data">
            <fieldset>
                {{ render_form_fields(form) }}

                {{ render_button_bar(cancel_url=request.full_path, submit_label="Save") }}
            </fieldset>
        </form>

        {% endblock %}

        ''', form=form, has_a_name=has_a_name, not_exists=not_exists, valid=valid)

    @app.route('/pages_of_fields/', methods=["GET", "POST"])
    def pages_of_fields():
        search_form = SearchForm(formdata=request.args)

        items = db.paginate(select(Field))

        return render_template_string('''
        
        {% extends "lbrc/page.html" %}
        {% from "lbrc/form_macros.html" import render_form_fields %}
        {% from "lbrc/pagination.html" import render_pagination %}

        {% block page_content %}
            <form action="{{ url_for('search') }}" method="GET" enctype="multipart/form-data">
                <fieldset>
                    {{ render_form_fields(search_form) }}
                </fieldset>    
            </form>    

            {{ render_pagination(items, 'pages_of_fields', form=search_form) }}

        {% endblock %}

        ''', items=items, search_form=search_form)

    @app.route('/json', methods=["GET", "POST"])
    @login_required
    @validate_json({
        'type': 'object',
        'properties': {
            'string': {'type': 'string'},
            'integer': {'type': 'integer'},
            'datetime': {'type': 'string', 'format': 'date-time'},
            'date': {'type': 'string', 'format': 'date'},
        },
        "required": ["string", "integer"]
    })
    def json():
        print('*******    HELLO        ****')
        return {'result': request.get_json()['integer']}

    @app.route('/json_requests/<string:field_name>', methods=["GET", "POST"])
    @login_required
    def json_requests(field_name):
        return {'result': get_value_from_all_arguments(field_name)}

    @app.route('/user_id', methods=["GET", "POST"])
    @login_required
    def user_id():
        return {'result': current_user_id()}

    @app.route('/system_user_id', methods=["GET", "POST"])
    def get_system_user_id():
        return {'result': system_user_id()}

    @app.route('/user_id_for_username/<string:username>', methods=["GET", "POST"])
    def user_id_for_username(username):
        return {'result': get_user_from_username(username).id}

    @app.route('/admin_user_id', methods=["GET", "POST"])
    def admin_user_id():
        return {'result': get_admin_user().id}

    @app.route('/users_for_role/<string:rolename>', methods=["GET", "POST"])
    def users_for_role(rolename):
        return {'result': ','.join([str(u.id) for u in get_users_for_role(rolename)])}

    @app.route('/add_username_to_rolename/<string:rolename>/<string:username>', methods=["GET", "POST"])
    def add_username_to_rolename(rolename, username):
        add_user_to_role(username=username, role_name=rolename)
        return {'result': ''}

    @app.route('/must_be_an_admin', methods=["GET", "POST"])
    @must_be_admin()
    def must_be_an_admin():
        return {'result': ''}

    @app.route('/give_me_error/<int:error_code>', methods=["GET", "POST"])
    @login_required
    def give_me_error(error_code):
        abort(error_code)

    @app.route('/use_the_template_filters')
    @login_required
    def use_the_template_filters():
        return render_template_string('''
        
            <ul>
                <li id='yesno_format'>{{ True | yes_no }}</li>
                <li id='datetime_format'>{{ date | datetime_format }}</li>
                <li id='date_format'>{{ date | date_format }}</li>
                <li id='datetime_humanize'>{{ date | datetime_humanize }}</li>
                <li id='date_humanize'>{{ date | date_humanize }}</li>
                <li id='currency'>{{ 23.87 | currency }}</li>
                <li id='separated_number'>{{ 1_000_765 | separated_number }}</li>
                <li id='title_case'>{{ 'this is only in lowercase' | title_case }}</li>
                <li id='blank_if_none__none'>{{ None | blank_if_none }}</li>
                <li id='blank_if_none__not_none'>{{ 'Lorem Ipsum' | blank_if_none }}</li>
                <li id='default_if_none__none'>{{ None | default_if_none('On the fence') }}</li>
                <li id='default_if_none__not_none'>{{ 'Lorem Ipsum' | default_if_none('On the fence') }}</li>
                <li id='nbsp'>{{ 'Lorem ipsum dolor sit amet.' | nbsp }}</li>
                <li id='nbsp__none'>{{ None | nbsp }}</li>
                <li id='current_year'>{{ current_year }}</li>
                <li id='application_title'>{{ application_title }}</li>
                <li id='previous_page'>{{ previous_page }}</li>
            </ul>

        ''', date=datetime.datetime(2007, 12, 5, 13, 23, 34))


    @app.route('/get_with_login')
    @login_required
    def get_with_login():
        return render_template_string('{% extends "lbrc_flask/page.html" %}')

    @app.route('/get_without_login')
    def get_without_login():
        return render_template_string('{% extends "lbrc_flask/page.html" %}')

    @app.route('/post_with_login', methods=["POST"])
    @login_required
    def post_with_login():
        return render_template_string('{% extends "lbrc_flask/page.html" %}')

    @app.route('/post_without_login', methods=["POST"])
    def post_without_login():
        return redirect(url_for("ui.index"))

    @app.route('/excel', methods=["GET"])
    def get_excel():
        return excel_download(
            'ExcelTest',
            ['fred','mary','ed'],
            [{
                'fred': 'soup',
                'mary': 'fish',
                'ed': '2000-01-02',
            }],
        )

    @app.route('/csv', methods=["GET"])
    def get_csv():
        return csv_download(
            'CsvTest',
            ['fred','mary','ed'],
            [{
                'fred': 'soup',
                'mary': 'fish',
                'ed': '2000-01-02',
            }],
        )

    @app.route('/pdf', methods=["GET"])
    def get_pdf():
        return pdf_download('lbrc_flask/404.html', title=f'PDF Test')

    return app
