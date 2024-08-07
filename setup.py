#!/usr/bin/env python

from distutils.core import setup

setup(name='lbrc_flask',
      version='1.0',
      description='NIHR Leicester BRC Flask Components and Theme',
      author='Richard Bramley',
      author_email='rabramley@gmail.com',
      url='https://github.com/LCBRU/lbrc_flask/',
      packages=['lbrc_flask'],
      include_package_data=True,
      install_requires=[
            'Flask',
            'flask_mail',
            'flask_admin',
            'flask_sqlalchemy',
            'flask_api',
            'flask_weasyprint',
            'python-dotenv',
            'email_validator',
            'markdown',
            'arrow',
            'python-ldap',
            'bcrypt',
            'markdown',
            'openpyxl',
            'pygal',
            'xlrd',
            'chardet',
            'rich',
            'jsonschema',
            'pytz',
      ],
)