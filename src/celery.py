from celery import Celery

celery = Celery()

class Config():
    def __init__(self, app):
        self.broker_url = app.config["BROKER_URL"]
        self.result_backend = app.config["CELERY_RESULT_BACKEND"]
        self.task_default_rate_limit = app.config["CELERY_RATE_LIMIT"]
        self.worker_redirect_stdouts_level = app.config["CELERY_REDIRECT_STDOUTS_LEVEL"]
        self.task_default_queue = app.config["CELERY_DEFAULT_QUEUE"]



def init_celery(app, title):
    global celery

    celery.config_from_object(Config(app))

    class ContextTask(celery.Task):
        rate_limit = app.config['CELERY_RATE_LIMIT']
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
