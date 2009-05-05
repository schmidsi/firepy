# The MIT License
# 
# Copyright (c) 2009 Sung-jin Hong <serialx@serialx.net>
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

from django.contrib.auth.models import User
from django.http import HttpResponse

def a(a, b, c):
    raise ValueError("asexception!!")

def fire(request):
    logging.debug([1, {"asdf":(123, 2, "3")}, "3"])
    logging.debug("debug")
    logging.info("info")
    logging.warn("warn %d", 2)
    logging.error("error")
    logging.critical("critical")
    ab = User.objects.filter(username="serialx").all()
    for i in ab:
        print i
    ab = User.objects.all()
    for i in ab:
        print i
    try:
        a(1, 2, "3")
    except:
        logging.exception("sdf!!!")

    response = HttpResponse("hello world!")
    return response
