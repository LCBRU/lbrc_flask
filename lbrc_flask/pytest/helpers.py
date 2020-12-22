from bs4 import BeautifulSoup
from lbrc_flask.database import db
from flask_login import login_user


def login(client, faker):
    u = faker.user_details()
    db.session.add(u)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True # https://flask-login.readthedocs.org/en/latest/#fresh-logins
    
    # Some stuff is created on first request, so do that
    client.get("/")

    # Login for access to functions directly
    login_user(u)
    
    resp = client.get("/login")
    soup = BeautifulSoup(resp.data, "html.parser")

    crf_token = soup.find(
        "input", {"name": "csrf_token"}, type="hidden", id="csrf_token"
    )

    data = dict(email=u.email, password=u.password)

    if crf_token:
        data["csrf_token"] = crf_token.get("value")

    client.post("/login", data=data, follow_redirects=True)

    return u
