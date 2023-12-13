import traceback
import logging
from logging import FileHandler
from flask import current_app, g
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

    query_logger = logging.getLogger('query')

    query_handler = FileHandler(str(log_directory / 'query.log'))
    query_handler.setLevel(logging.INFO)
    query_handler.setFormatter(logging.Formatter('%(message)s\n--------------------------------\n'))

    query_logger.addHandler(query_handler)

    query_logger.info('Q U E R Y   L O G')

    app.logger.info('Flask app created')



def log_exception(e):
    print(traceback.format_exc())
    current_app.logger.error(traceback.format_exc())
    email(
        subject=f'ERROR: {g.get("lbrc_flask_title", "Application")}',
        message=traceback.format_exc(),
        recipients=[current_app.config["ADMIN_EMAIL_ADDRESS"]],
    )


def log_form(form):
    for k, v in form.data.items():
        logging.info(f'{k}: {v}')
