# -*- coding: utf-8 -*-
import os

from flask import abort, jsonify, make_response, request
from functools import wraps


def apikey_required(f):

    @wraps(f)
    def decorated_function(*args, **kws):
        api_key = request.headers.get('Authorization', '12323')

        if api_key != 'Api-Key {}'.format(os.environ.get('API_KEY', '12323')):
            abort(make_response(jsonify(message='Unauthorized'), 401))

        return f(*args, **kws)

    return decorated_function
