import sys
sys.path.append('..')
import pyper3
sys.path.remove('..')

from operator import neg, add, sub

def test_implicit_only():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .push(a)
        .pipe(neg)()
        .pop()
    )
    
    assert b == -3 - 4j
    
def test_implicit_other():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .push(a)
        .pipe(add)(5)
        .pop()
    )
    
    assert b == 8 + 4j
    
def test_implicit_both():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .push(a)
        .pipe(neg)()
        .pipe(add)(5)
        .pop()
    )
    
    assert b == 2 - 4j
    
def test_explicit_arg():
    
    a = 3 + 4j

    b = (
        pyper3.Pipe
        .push(a)
        .pipe(sub)(5, pyper3.THIS)
        .pop()
    )
    
    assert b == 2 - 4j
    
def test_explicit_kwarg():
    
    arr = [2, 3, 1]

    b = (
        pyper3.Pipe
        .push(neg)
        .pipe(sorted)(arr, key=pyper3.THIS)
        .pop()
    )
    
    assert b == [3, 2, 1]
    
def test_attribute_success():
    
    a = 3 + 4j
    
    b = (
        pyper3.Pipe
        .push(a)
        .pipe(pyper3.THIS.real)()
        .pop()
    )
    
    return b == 3.0

def test_attribute_failure():
    
    a = 3 + 4j
    
    try:
        b = (
            pyper3.Pipe
            .push(a)
            .pipe(pyper3.THIS.real)(None)
            .pop()
        )
        assert False
    except Exception:
        assert True

def test_method_none():
    
    a = 3 + 4j
    
    b = (
        pyper3.Pipe
        .push(a)
        .pipe(pyper3.THIS.conjugate)()
        .pop()
    )
    
    return b == 3 - 4j

def test_method_args():
    
    arr = [2, 3, 1]
    
    b = (
        pyper3.Pipe
        .push(arr)
        .pipe(pyper3.THIS.append)(4)
        .pop()
    )
    
    assert arr == [2, 3, 1, 4]
    assert b is None
    
def test_method_kwargs():
    
    arr = [2, 3, 1]
    
    b = (
        pyper3.Pipe
        .push(arr)
        .pipe(pyper3.THIS.sort)(reverse=True)
        .pop()
    )
    
    assert arr == [3, 2, 1]
    assert b is None