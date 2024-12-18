from mimetypes import guess_type
from pathlib import Path
from flask_mail import Mail, Message
from flask import current_app, render_template


mail = Mail()


def init_mail(app):
    mail.init_app(app)


def email(subject, message, recipients, html_template=None, attachements: list[Path]=None, **kwargs):
    attachements = attachements or []

    if len(recipients) < 1:
        current_app.logger.info('Skipping email with no recipients')
        return

    if current_app.config["SMTP_SERVER"] is not None:

        msg: Message = Message(
            subject=subject,
            recipients=recipients,
            body=message,
            reply_to=current_app.config.get("MAIL_REPLY_TO", None),
        )

        if html_template is not None:
            msg.html = render_template(html_template, **kwargs)

        for a in attachements:
            absolute_path = Path(current_app.root_path) / a
            msg.attach(absolute_path.name, guess_type(absolute_path)[0], absolute_path.read_bytes())

        current_app.logger.info('Sending from to {}'.format(current_app.config.get("MAIL_DEFAULT_SENDER", None)))
        current_app.logger.info('With reply to of {}'.format(current_app.config.get("MAIL_REPLY_TO", None)))
        current_app.logger.info('Sending email to {}'.format(recipients))

        mail.send(msg)
    else:
        current_app.logger.info('Skipping email to {}'.format(recipients))
