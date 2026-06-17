import traceback
import logging
from logging import FileHandler
from flask import current_app, g, request, has_request_context
from lbrc_flask.emailing import email
from pathlib import Path
from rich.logging import RichHandler


def init_logging(app):
    print('LOG LEVEL = {}'.format(app.config["LOG_LEVEL"]))

    logging.basicConfig(
        level=app.config['LOG_LEVEL'], format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
    )

    log_directory = Path(app.config["LOG_DIRECTORY"])

    info_handler = FileHandler(str(log_directory / 'info.log'))
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    app.logger.addHandler(info_handler)

    error_handler = FileHandler(str(log_directory / 'error.log'))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    app.logger.addHandler(error_handler)

    query_handler = FileHandler(str(log_directory / 'query.log'))
    query_handler.setLevel(logging.INFO)
    query_handler.setFormatter(logging.Formatter('%(message)s\n--------------------------------\n'))

    if app.config['QUERY_LOG']:
        logging.getLogger('sqlalchemy.engine').propagate = False
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        logging.getLogger('sqlalchemy.engine').addHandler(query_handler)

    app.logger.info('Flask app created')


def log_exception(e):
    tb = traceback.format_exc()
    print(tb)
    current_app.logger.error(tb)

    if has_request_context():
        message_template = 'lbrc/email/exception/txt.txt'
        html_template = 'lbrc/email/exception/html.html'
    else:
        message_template = 'lbrc/email/exception/txt_norequest.txt'
        html_template = 'lbrc/email/exception/html_norequest.html'

    try:
        email(
            subject=f'ERROR: {g.get("lbrc_flask_title", "Application")}',
            message_template=message_template,
            html_template=html_template,
            recipients=[current_app.config["ADMIN_EMAIL_ADDRESS"]],
            traceback=tb,
            request=request,
        )
    except Exception as e:
        print('*-'*40)
        print("Error emailing in Exception processing")
        print('*-'*40)
        print(traceback.format_exc())
        current_app.logger.error("Error emailing in Exception processing")
        current_app.logger.error(traceback.format_exc())


def log_form(form):
    for k, v in form.data.items():
        logging.info(f'{k}: {v}')
