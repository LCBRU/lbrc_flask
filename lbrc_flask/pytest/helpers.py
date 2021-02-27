from bs4 import BeautifulSoup
from lbrc_flask.database import db
from flask_login import login_user
from flask_security.utils import _datastore, url_for_security


def login(client, faker, user=None):
    if user is None:
        user = faker.user_details()

    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True # https://flask-login.readthedocs.org/en/latest/#fresh-logins
    
    # Some stuff is created on first request, so do that
    client.get("/")

    # Login for access to functions directly
    login_user(user)
    
    resp = client.get("/login")
    soup = BeautifulSoup(resp.data, "html.parser")

    crf_token = soup.find(
        "input", {"name": "csrf_token"}, type="hidden", id="csrf_token"
    )

    data = dict(email=user.email, password=user.password)

    if crf_token:
        data["csrf_token"] = crf_token.get("value")

    resp = client.post("/login", data=data, follow_redirects=True)

    return _datastore.find_user(email=user.email)


def logout(client):
    client.get(url_for_security('logout'))