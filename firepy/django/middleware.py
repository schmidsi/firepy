# The MIT License
# 
# Copyright (c) 2009 Sung-jin Hong <serialx@serialx.net>
# Many code here derived from:
# http://code.cmlenz.net/diva/browser/trunk/diva/ext/firephp.py
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging

from django.db import connection
from django.conf import settings
import simplejson as json

from firepy.loghandler import FirePHPHandler
from firepy.firephp import FirePHP


class FirePHPMiddleware():
    """FirePHP middleware for Django."""

    def __init__(self):
        # Set the FirePHP log handler to the root logger.
        firephp = FirePHPHandler()
        firephp.setLevel(logging.DEBUG)
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(firephp)

    def process_request(self, request):
        # Reset the log buffer.
        FirePHPHandler.logs = []

    def process_response(self, request, response):
        # Ignore the static media file requests
        if settings.MEDIA_URL and request.META['PATH_INFO'].startswith(settings.MEDIA_URL):
            return response
        # Calculate db times
        time = 0.0
        for q in connection.queries:
            time += float(q['time'])

        # Generate db times table
        query_info = [["SQL Statement","Time"]]
        query_info += [[query['sql'], query['time']]
                       for query in connection.queries]
        label = "%d SQL queries took %f seconds" % \
                (len(connection.queries), time)
        FirePHPHandler.logs.append(FirePHP.table(query_info, label))

        # Set base FirePHP JSON protocol headers
        headers = FirePHP.base_headers()
        for key, value in headers:
            response[key] = value

        # Translate the JSON message to headers
        for key, value in FirePHP.generate_headers(FirePHPHandler.logs):
            response[key] = value

        return response
