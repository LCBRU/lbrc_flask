from flask import Response


def refresh_response():
    resp = Response("Refresh")
    resp.headers['HX-Refresh'] = 'true'
    return resp