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

## Improvements
**Less Code = More Better**
### SqlAlchemy Aware Forms
#### Problem
WTForms have no knowledge of SqlAlchemy objects.  This becomes especially troublesome
when you deal with relationships because you have to convert back and forth between
db.Model objects and interger IDs individually or as lists.  This means that you have
to write code such as this:
```python
form = FolderEditForm(data={
    'id': folder.id,
    'author_access': folder.author_access,
    'name': folder.name,
    'description': folder.description,
    'autofill_year': folder.autofill_year,
    'excluded_acknowledgement_statuses': [s.id for s in folder.excluded_acknowledgement_statuses],
})
```
when an object contains a relationship to one or more other objects.  But if it doesn't
then you can write the much simpler:
```python
form = FolderEditForm(obj=folder)
```
And then when getting data out of the form you end up writing something like:
```python
item.excluded_acknowledgement_statuses = {db.session.get(NihrAcknowledgement, n) for n in self.excluded_acknowledgement_statuses.data}
```
Which is not too bad, I suppose.  Definitely going from object yo form is the pain point because
it forces you to change all the other fields as well.
#### Solution
There are several solutions to this:
1. Customise the `SelectField` and `SelectMultipleField` classes to recognise db.Models
2. [WTForms-Alchemy](https://wtforms-alchemy.readthedocs.io/en/latest/):  seems full featured, can solve the problem above, and can also dynamically create forms from db.Models.
3. Use [WTForms-SQLAlchemy](https://github.com/pallets-eco/wtforms-sqlalchemy/tree/main): from
what I can see this does not solve the above problem, but does do the dynamically create forms
from db.Model thing.  **However**, this is maintained by *Pallets* (the Flask people) who also
(now) maintain [WTForms](https://github.com/pallets-eco/wtforms?tab=readme-ov-file).  So, maybe
this will be improved over time and eventually become the de facto solution.
### Better Selects and Multi-Selects
#### Current Position
Currently, we have 2 solutions for select type input:
1. The standard HTML select
2. The [Select2](https://select2.org/) javascript pluigin, which creates a nice UI for
multiselects and also allows option searching.
#### Problem One
Drop down / select type inputs are not very user friendly (see, [here](https://joshwayne.com/posts/the-problem-with-dropdowns/) or just Google it - I did read a good article on this, but
I can't find it now).
#### Problem Two
- [Select2](https://select2.org/) uses JQuery and is the only reason that JQuery is included in our
application.  So removing it is a good idea.
- [Select2](https://select2.org/) does not match our theme exactly.  It's close enough, but
not 100% the same.  It is also very difficult theme. 
#### Solution
1. Create better UI for small select lists:
 - switched for yes / no
 - Suttin cool for tri-states!
 - Radio buttons or checkboxes for short lists of options
2. Design a better multi-select
3. Design a better searchable list
### Automatic Audit
#### Problem
The first step of auditing is recording when a record was saved and who saved it.  For this
reason we have the `AuditMixin` class that can be added as a base class along with `db.Model`
(Python allow multiple inheritance).  However, the idiot that wrote it (that is, me) did
not just create a custom version of `db.Model` with this stuff in it.  And include the
`CommonMixin`, because you might as well.
#### Solution
Do that thing what I should have already done.
#### Drawbacks
I can see from my own code that some models do not inherit from `AuditMixin` and so new columns
will have to be added to those tables.  The columns don't allow nulls (and nor should they), so
added the columns will have to be done in 3 steps:
1. Add the columns allowing nulls
2. Provide suitable values for missing data.  Probably the current date and time for the datetime
columns and 'historic import' or some such for the name of the user that made the change.
3. Alter the columns to not allow nulls.
#### Next Steps
Once all the models have basic information about when they changed and who done it, the next
step will be to come up with a solution for saving historic audit information.  This could be:
1. Database triggers - and is there a way to get Alembic to create them?
2. Hooking into SqlAlchemy shenanigans
### Better Icons
#### Problem
The icon set that we use (FontAwesome) is a bit limited.
#### Solution
Use [Nerd Fonts Aggregated Icons](https://www.nerdfonts.com/)
### Smaller Search Forms
#### Problem
The search form at the top of index pages can get quite large, which hides the important
content of the page.
#### Solution
There are a few options:
1. Put the search form in a concertino panel
2. Dropdown list of search fields and dynamic entry
3. Some way to pick what you want to search (but not a drop down) and the enter the value
All of these options will probably need a way to show what filters are currently in place
and let users delete theme.  Something like a list of buttons with an X on them.
### Editable LBRC Flask Library
#### Problem
You used to be able to include the requirements in the `requirements.txt`
file with a `-e` flag that made them editable.  That is now deprecated.
This means that you have to have the requirement as a separate project
and release it everytime you make a little change.  This slows down the
process considerably.
#### Solution
I dunno.  There must be a solution to this.  I don't know why they had
to deprecate the old version.