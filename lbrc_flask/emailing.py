from flask_mail import Mail, Message
from flask import current_app, render_template


mail = Mail()


def init_mail(app):
    mail.init_app(app)


def email(subject, message, recipients, html_template=None, **kwargs):
    if current_app.config["SMTP_SERVER"] is not None:

        msg = Message(
            subject=subject,
            recipients=recipients,
            body=message,
            reply_to=current_app.config.get("MAIL_REPLY_TO", None),
        )

        if html_template is not None:
            msg.html = render_template(html_template, **kwargs)

        current_app.logger.info('Sending email to {}'.format(recipients))

        mail.send(msg)
    else:
        current_app.logger.info('Skipping email to {}'.format(recipients))
