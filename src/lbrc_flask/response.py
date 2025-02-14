from flask import Response

REFRESH_RESULTS_TRIGGER = 'refresh_results'
REFRESH_DETAILS_TRIGGER = 'refreshDetails'


def refresh_response():
    resp = Response("Refresh")
    resp.headers['HX-Refresh'] = 'true'
    return resp


def refresh_results():
    resp = Response('')
    resp.headers['HX-Trigger'] = REFRESH_RESULTS_TRIGGER
    return resp


def refresh_details():
    resp = Response('')
    resp.headers['HX-Trigger'] = REFRESH_DETAILS_TRIGGER
    return resp


def trigger_response(trigger_name):
    resp = Response('')
    resp.headers['HX-Trigger'] = trigger_name
    return resp
