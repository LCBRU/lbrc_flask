from flask import Response


def refresh_response():
    resp = Response("Refresh")
    resp.headers['HX-Refresh'] = 'true'
    return resp


def refresh_results():
    resp = Response('')
    resp.headers['HX-Trigger'] = 'refresh_results'
    return resp


def trigger_response(trigger_name):
    resp = Response('')
    resp.headers['HX-Trigger'] = trigger_name
    return resp
