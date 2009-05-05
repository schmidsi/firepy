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

from django.db import connection
import logging
import cgi
import simplejson as json

LEVELMAP = {'DEBUG': 'LOG', 'WARNING': 'WARN', 'CRITICAL': 'ERROR'}

def _extract_traceback(tb):
    frames = []
    while tb:
        tb_frame = tb.tb_frame
        f_locals = tb_frame.f_locals
        f_code = tb_frame.f_code
        frames.append({
            'filename': f_code.co_filename,
            'lineno': tb.tb_lineno,
            'locals': f_locals,
            'name': f_code.co_name,
            'args': [
                #f_code.co_varnames[i] for i in range(f_code.co_argcount)
                f_locals.get(f_code.co_varnames[i]) for i in range(f_code.co_argcount)
            ],
            'hide': tb_frame.f_locals.get('__traceback_hide__')
        })
        tb = tb.tb_next
    return frames

def _filter_traceback(frames):
    hidden = False
    retval = []
    for idx, frame in enumerate(frames):
        hide = frame['hide']
        if hide in ('before', 'before_and_this'):
            del retval[:]
            hidden = False
            if hide == 'before_and_this':
                continue
        elif hide in ('reset', 'reset_and_this'):
            hidden = False
            if hide == 'reset_and_this':
                continue
        elif hide in ('after', 'after_and_this'):
            hidden = True
            if hide == 'after_and_this':
                continue
        elif hidden:
            continue
        if not hide:
            retval.append(frame)
    return retval

class FirePHPHandler(logging.Handler):
    logs = []
    def emit(self, record):
        level = LEVELMAP.get(record.levelname, record.levelname)

        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            frames = _filter_traceback(_extract_traceback(exc_tb))
            FirePHPHandler.logs.append([
                   {"Type": 'EXCEPTION',
                    "File": record.pathname,
                    "Line": record.lineno},
                   {'Type': 'throw',
                    'Class': exc_type.__name__,
                    'Message': record.getMessage(),
                    'File': frames[-1]['filename'],
                    'Line': frames[-1]['lineno'],
                    'Function': frames[-1]['name'],
                    'Trace': list(reversed([{
                        'function': frame['name'],
                        'args': frame['args'],
                        'line': frame['lineno'],
                        'file': frame['filename']
                    } for frame in frames]))}
            ])

        else:
            FirePHPHandler.logs.append([
                {"Type": level,
                 "File": record.pathname,
                 "Line": record.lineno},
                record.getMessage()])


class FireMiddleware():
    def __init__(self):
        firephp = FirePHPHandler()
        firephp.setLevel(logging.DEBUG)
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(firephp)

    def process_request(self, request):
        FirePHPHandler.logs = []

    def process_response(self, request, response):
        time = 0.0
        for q in connection.queries:
            time += float(q['time'])
        query_info = [["SQL Statement","Time"]]
        query_info += [[query['sql'],
                 query['time']] for query in connection.queries]

        FirePHPHandler.logs.append([
            {"Type":"TABLE",
             "Label":"%d SQL queries took %f seconds" % (len(connection.queries), time),
             "File":"a.py",
             "Line":23},
             query_info,
            ])
        response['X-Wf-Protocol-1'] = 'http://meta.wildfirehq.org/Protocol/JsonStream/0.2'
        response['X-Wf-1-Plugin-1'] = 'http://meta.firephp.org/Wildfire/Plugin/FirePHP/Library-FirePHPCore/0.2.0'
        response['X-Wf-1-Structure-1'] = 'http://meta.firephp.org/Wildfire/Structure/FirePHP/FirebugConsole/0.1'

        def encode_robust(obj):
            return repr(obj)
        for i, log in enumerate(FirePHPHandler.logs):
            code = json.dumps(log, default=encode_robust)
            response['X-Wf-1-1-1-%d' % i] = '%d|%s|' % (len(code), code)
        #response['X-Wf-1-Index'] = '1'
        return response
