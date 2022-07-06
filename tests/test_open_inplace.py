import sys
sys.path.append('..')
import pyper3
sys.path.remove('..')

from operator import neg, add, sub

def test_implicit_only():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .open()
        .pipe(neg, inplace=True)()
        .close()
    )(a)
    
    assert b == a
    
def test_implicit_other():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .open()
        .pipe(add, inplace=True)(5)
        .close()
    )(a)
    
    assert b == a
    
def test_implicit_both():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .open()
        .pipe(neg, inplace=True)()
        .pipe(add)(5)
        .close()
    )(a)
    
    assert b == a + 5
    
def test_explicit_arg():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .open()
        .pipe(sub, inplace=True)(5, pyper3.THIS)
        .close()
    )(a)
    
    assert b == a
    
def test_explicit_kwarg():
    
    arr = [2, 3, 1]

    b = (
        pyper3.Pipe
        .open()
        .pipe(sorted, inplace=True)(arr, key=pyper3.THIS)
        .close()
    )(neg)
    
    assert b == neg
    
def test_attribute_success():
    
    a = 3 + 4j
    
    b = (
        pyper3.Pipe
        .open()
        .pipe(pyper3.THIS.real, inplace=True)()
        .close()
    )(a)
    
    return b == a

def test_attribute_failure():
    
    a = 3 + 4j
    
    try:
        b = (
            pyper3.Pipe
            .open()
            .pipe(pyper3.THIS.real, inplace=True)()
            .close()
        )(a)
        assert False
    except Exception:
        assert True

def test_method_none():
    
    a = 3 + 4j
    
    b = (
        pyper3.Pipe
        .open()
        .pipe(pyper3.THIS.conjugate, inplace=True)()
        .close()
    )(a)
    
    return b == a

def test_method_args():
    
    arr = [2, 3, 1]
    
    b = (
        pyper3.Pipe
        .open()
        .pipe(pyper3.THIS.append, inplace=True)(4)
        .close()
    )(arr)
    
    assert arr == [2, 3, 1, 4]
    assert b is arr
    
def test_method_kwargs():
    
    arr = [2, 3, 1]
    
    b = (
        pyper3.Pipe
        .open()
        .pipe(pyper3.THIS.sort, inplace=True)(reverse=True)
        .close()
    )(arr)
    
    assert arr == [3, 2, 1]
    assert b is arr