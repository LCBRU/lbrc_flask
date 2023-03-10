# lbrc_flask

Library of utils for NIHR Leicester Biomedical Research Centre.  Including:

- WTForms extensions for error messages and dynamic forms.
- Testing
  - NHS fake data
  - Asserting BRC web standards
  - Flask fixtures
  - Helper
- Security
 - BRC standard login screens
 - LDAP integration
 - Standard BRC user and role models and database migrations
- BRC Theme HTML, CSS and images
- Javascript for forms, AJAX and dynamic HTML
- Flask
 - Application initialisation
 - Configuration
 - Admin screens
 - Template filters
 - Email helpers
 - HTTP Request and Response helpers
 - URL helpers
- Asynchronous tasks with Celery
- Sqlalchemy setup
- Data
 - Export or import from Excel or CSV
 - Validators, parsers and converters
 - String functions
 - JSON parsing
 - Logging
 - Charting

## Usage

To use this in library in your application include it in your requirements.txt file
```
-e git+https://github.com/LCBRU/lbrc_flask.git@main#egg=lbrc_flask
```

## Testing

To test this library you need to first set up a virtual env and install the requirements
```bash
# Create virtual environment
python3 -m venv venv
# Activate virtual environment
source ./venv/bin/activate
# Install requirements
pip install -r requirements-dev.txt
```
Then copy the `example.env` file to `.env`.

Then run:
```bash
pytest
```
