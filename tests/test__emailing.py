from lbrc_flask.emailing import email
from unittest.mock import patch


def test__emailing__smtp_set__sends_email(app, client, faker):

    app.config['SMTP_SERVER'] = faker.ipv4_private()

    with patch('lbrc_flask.emailing.mail') as mock_mail:
        email(faker.pystr(min_chars=5, max_chars=10), faker.pystr(min_chars=5, max_chars=10), [faker.safe_email()])

        mock_mail.send.assert_called_once()


def test__emailing__smtp_set__skips(app, client, faker):

    with patch('lbrc_flask.emailing.mail') as mock_mail:
        email(faker.pystr(min_chars=5, max_chars=10), faker.pystr(min_chars=5, max_chars=10), [faker.safe_email()])

        mock_mail.send.mock.assert_not_called()
