import simplejson as json


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


class FirePHP(object):
    """Core module that generates FirePHP JSON notation."""
    LEVELMAP = {'DEBUG': 'LOG', 'WARNING': 'WARN', 'CRITICAL': 'ERROR'}

    @classmethod
    def log_level(cls, python_log_level):
        """Translate python log level to FirePHP's."""
        return cls.LEVELMAP.get(python_log_level, python_log_level)

    @classmethod
    def exception(cls, record):
        """Translate exc_info into FirePHP JSON notation."""
        assert record.exc_info
        exc_info = record.exc_info
        exc_type, exc_value, exc_tb = exc_info
        frames = _filter_traceback(_extract_traceback(exc_tb))
        return [{"Type": 'EXCEPTION',
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
                 } for frame in frames]))}]

    @classmethod
    def log(cls, record):
        """Translate log record into FirePHP JSON."""
        level = cls.log_level(record.levelname)
        return [
            {"Type": level,
             "File": record.pathname,
             "Line": record.lineno},
            record.getMessage()]

    @classmethod
    def table(cls, table_, label=None):
        """Generates FirePHP table JSON."""
        if not label:
            label = ""
        return [
            {"Type":"TABLE",
             "Label": label,
             "File":"a.py",
             "Line":23},
             table_,
            ]

    @classmethod
    def base_headers(cls):
        """Base FirePHP JSON protocol headers."""
        return [
            ('X-Wf-Protocol-1',
             'http://meta.wildfirehq.org/Protocol/JsonStream/0.2'),
            ('X-Wf-1-Plugin-1',
             'http://meta.firephp.org/Wildfire/Plugin/FirePHP/Library-FirePHPCore/0.2.0'),
            ('X-Wf-1-Structure-1',
             'http://meta.firephp.org/Wildfire/Structure/FirePHP/FirebugConsole/0.1'),
            ]

    @classmethod
    def generate_headers(cls, logs):
        def encode_robust(obj):
            return repr(obj)
        index = 0
        for i, log in enumerate(logs):
            code = json.dumps(log, default=encode_robust)
            yield ('X-Wf-1-1-1-%d' % i, '%d|%s|' % (len(code), code))
            index = i
        yield ('X-Wf-1-Index', str(index))
