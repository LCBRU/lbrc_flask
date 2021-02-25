import traceback
import logging
from logging import FileHandler
from flask import current_app
from lbrc_flask.emailing import email


def init_logging(app):
    info_handler = FileHandler('info.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    app.logger.addHandler(info_handler)

    error_handler = FileHandler('error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    app.logger.addHandler(error_handler)

    app.logger.info('Flask app created')

    print(f'LOG LEVEL = {app.config["LOG_LEVEL"]}')
    
    app.logger.setLevel(app.config['LOG_LEVEL'])


def log_exception(e):
    print(traceback.format_exc())
    current_app.logger.error(traceback.format_exc())
    email(
        subject=current_app.config["ERROR_EMAIL_SUBJECT"],
        message=traceback.format_exc(),
        recipients=[current_app.config["ADMIN_EMAIL_ADDRESS"]],
    )
