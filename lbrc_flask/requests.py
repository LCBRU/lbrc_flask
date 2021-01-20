from flask import request


def get_value_from_all_arguments(name):
    all_args = {**request.view_args, **request.args, **request.form}

    if request.json:
        all_args.update(request.json)

    return all_args.get(name)
