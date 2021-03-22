from flask_mail import Mail, Message
from flask import current_app


mail = Mail()


def init_mail(app):
    mail.init_app(app)


def email(subject, message, recipients):
    if current_app.config["SMTP_SERVER"] is not None:
        msg = Message(subject=subject, recipients=recipients, body=message)

        current_app.logger.info('Sending email to {}'.format(recipients))

        mail.send(msg)
    else:
        current_app.logger.info('Skipping email to {}'.format(recipients))
