import sys

sys.path.append('..')
import pyper3
sys.path.remove('..')

from operator import neg, add, sub

def setup_logging():
    import logging

    TAG = "test_logs"
    pyper3.Pipe.setup_logging(TAG)
    fp = "tests/logs.txt"
    handler = logging.FileHandler(fp, mode="w")
    handler.setFormatter(logging.Formatter('%(name)s/%(levelname)s: %(message)s'))
    pyper3.Pipe._logger.handlers[0] = handler
    
    return fp

def delete_logging():
    import os
    
    fp = "tests/logs.txt"
    os.remove(fp)

def test_push():
    
    fp = setup_logging()
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .push(a)
        .pipe(neg)()
        .pop()
    )
    
    assert b == -3 - 4j
    
    with open(fp) as f:
        assert f.read() == r'test_logs/DEBUG: neg was called with args [(3+4j)] and kwargs {}' + '\n'
        
    delete_logging()
        
def test_open():
    
    fp = setup_logging()
    
    a = 3 + 4j

    p1 = (
        pyper3.Pipe
        .open()
        .pipe(neg)()
        .close()
    )
    
    p2 = (
        pyper3.Pipe
        .open()
        .pipe(add)(2)
        .close()
    )
    
    c = p2(a)
    b = p1(a)
    
    assert b == -3 - 4j
    assert c == 5 + 4j
    
    with open(fp) as f:
        assert f.read() ==  r'test_logs/DEBUG: add was called with args [(3+4j), 2] and kwargs {}' + '\n' + r'test_logs/DEBUG: neg was called with args [(3+4j)] and kwargs {}' + '\n'
    
    delete_logging()
    
def test_join():
    
    fp = setup_logging()
    
    reverse_sort = (
        pyper3.Pipe
        .open("named_pipe")
        .pipe(pyper3.THIS.sort, inplace=True)(reverse=True)
        .close()
    )
    
    pipeline = pyper3.Pipe.join(pyper3.THIS.copy, reverse_sort, name="outermost_pipe")
    
    arr = [2, 3, 1]
    b = pipeline(arr)
    
    assert b == [3, 2, 1]
    assert arr == [2, 3, 1]
    
    with open(fp) as f:
        assert f.read() == r'test_logs/DEBUG: outermost_pipe was called with args [[2, 3, 1]] and kwargs {}' + '\n' + r'test_logs/DEBUG: THIS.copy was called with args [[2, 3, 1]] and kwargs {}' + '\n' + r'test_logs/DEBUG: named_pipe was called with args [[2, 3, 1]] and kwargs {}' + '\n' + r'test_logs/DEBUG: THIS.sort was called inplace with args [[2, 3, 1]] and kwargs {reverse=True}' + '\n'
        
    delete_logging()