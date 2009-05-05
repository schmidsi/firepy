import sys
def func():
    frame = sys._getframe()
    tb = frame.f_back
    f_code = tb.f_code
    print f_code.co_filename, ':', f_code.co_name , tb.f_lineno
    print dir(frame)
    print dir(tb)
    print dir(f_code)

def func2():
    func()

func2()
