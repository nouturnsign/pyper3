import functools as _functools
import logging as _logging
from typing import (Any as _Any,
                    Callable as _Callable, 
                    ParamSpec as _ParamSpec,
                    TypeVar as _TypeVar, 
                    )

_T = _TypeVar('_T')
_P = _ParamSpec('_P')

def _add_logging(func: _Callable[_P, _T], inplace: bool) -> _Callable[_P, _T]:
    """A type-safe decorator to add logging to a function."""
    
    def lambda_(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        name_msg = "<functools.partial>" if isinstance(func, _functools.partial) else func.__name__
        inplace_msg = ' inplace ' if inplace else ' '
        args_msg = ', '.join(map(repr, args))
        kwargs_msg = ', '.join(map(lambda item: str(item[0]) + '=' + repr(item[1]), kwargs.items()))
        Pipe.logger.debug(f'{name_msg} was called{inplace_msg}with args [{args_msg}] and kwargs {{{kwargs_msg}}}')
        return func(*args, **kwargs)
    return lambda_

def _lambdify(func: _Callable[_P, _T], inplace_func: _Callable[..., _Any] | None, loggable: bool=True) -> _Callable[_P, _T]:
    """Convert the function to a named lambda function."""

    if inplace_func is not None:
        def lambda_(*args: _P.args, **kwargs: _P.kwargs):
            func(*args, **kwargs)
            return inplace_func(*args) # no **kwargs since it's just arg[0], I'm not sure why this works atm
    else:
        lambda_ = func
    
    if loggable:
        try:    
            lambda_ = _functools.update_wrapper(lambda_, func)
        except (AttributeError, TypeError):
            pass
        inplace = inplace_func is not None
        lambda_ = _add_logging(lambda_, inplace)
    
    return lambda_

class _THIS: 
    """Type of `THIS` placeholder."""
    
    def __init__(self) -> None:
        pass

    def __getattr__(self, attr: str) -> _Any:
        # f = lambda value, *args, **kwargs: getattr(value, attr) if len(args) == 0 and len(kwargs) == 0 and not callable(getattr(value, attr)) else getattr(value, attr)(*args, **kwargs)
        f = lambda value, *args, **kwargs: getattr(value, attr)(*args, **kwargs) if callable(getattr(value, attr)) else getattr(value, attr)
        f.__name__ = 'THIS.' + attr
        return _lambdify(f, inplace_func=None, loggable=False)

    def __getitem__(self, item: _Any) -> _Any:
        f = lambda value: value[item]
        f.__name__ = 'THIS[' + str(item) + ']'
        return _lambdify(f, inplace_func=None, loggable=False)

THIS = _THIS()
    
class Pipe:
    """API for beginning pipes."""
    
    logger = _logging.getLogger()
    
    @classmethod
    def push(cls, value: _Any) -> "PipeInput":
        """Push a specific value into the pipe."""
        return PipeInput(value)
    
    @classmethod
    def open(cls, name: str="<pyper3.Pipe>") -> "PipeOpening":
        """Open a pipe that accepts a certain input."""
        return PipeOpening(name, lambda value: value)
    
    @classmethod
    def join(cls, *funcs: _Callable[[_Any], _Any], inplace: bool=False, loggable: bool=True) -> _Callable[[_Any], _Any]:
        """Join several univariate functions."""
        
        if len(funcs) < 1:
            raise ValueError(f"There must be at least one function to join: funcs={funcs}")
        
        opened_pipe = Pipe.open()
        for func in funcs:
            opened_pipe = opened_pipe.pipe(func)()
        closed_pipe = opened_pipe.close()
        if not loggable:
            closed_pipe = closed_pipe
            
        return _lambdify(closed_pipe, (lambda *args: args[0]) if inplace else None, loggable=False)
    
    @classmethod
    def setup_logging(cls, name: str, level: int=_logging.DEBUG, fmt: str='%(name)s/%(levelname)s: %(message)s') -> None:
        """Enable logging."""
        cls.logger = _logging.getLogger(name)
        cls.logger.setLevel(level)

        handler = _logging.StreamHandler()
        handler.setFormatter(_logging.Formatter(fmt))
        cls.logger.addHandler(handler)
        
class PipeInput:
    """Pipes with inputs specified. Generally, avoid using this class directly."""
    
    def __init__(self, value) -> None:
        """Create a `PipeInput` with a certain value."""
        self.value = value

    def pipe(self, func: _Callable[..., _Any], inplace: bool=False) -> "PipeOutput":
        """Apply a function, returning the original input when `inplace=True`."""
        inplace_func = (lambda *args: self.value) if inplace else None
        return PipeOutput(_lambdify(func, inplace_func=inplace_func), self.value)
    
    def pop(self) -> _Any:
        """Retrieve the new value."""
        return self.value
    
class PipeOutput:
    """Pipes where the inputs are applied to the functions. Generally, avoid using this class directly."""
    
    def __init__(self, func: _Callable[..., _Any], input: _Any) -> None:
        self.func = func
        self.input = input
    
    def __call__(self, *args: _Any, **kwargs: _Any) -> "PipeInput":
        """Apply a function, returning the original input when `inplace=True`."""
        args = list(args)
        if THIS in args:
            args[args.index(THIS)] = self.input
        elif THIS in kwargs.values():
            for var, value in kwargs.items():
                if THIS == value:
                    kwargs[var] = self.input
                    break
        else:
            args.insert(0, self.input)
        return PipeInput(self.func(*args, **kwargs))
    
class PipeOpening:
    """Pipes without inputs specified. Generally, avoid using this class directly."""
    
    def __init__(self, name: str, func: _Callable[..., _Any]) -> None:
        self.name = name
        self.func = func
        
    def pipe(self, func: _Callable[..., _Any], inplace: bool=False) -> "PipeJoiner":
        """Apply a function, returning the original input when `inplace=True`."""
        return PipeJoiner(self.name, self.func, func, inplace)
    
    def close(self) -> _Callable[[_Any], _Any]:
        """Get the resulting univariate function."""
        self.func.__name__ = self.name
        return self.func
    
class PipeJoiner:
    """Pipes where the nonspecified inputs would be applied to the functions. Generally, avoid using this class directly."""
    
    def __init__(self, name: str, prev_func: _Callable[..., _Any], func: _Callable[..., _Any], inplace: bool=False) -> None:
        self.name = name
        self.prev_func = prev_func
        self.func = _add_logging(func, inplace)
        self.inplace = inplace
        
    def __call__(self, *args: _Any, **kwargs: _Any) -> "PipeOpening":
        """Apply a function, returning the original input when `inplace=True`."""
        args = list(args)
        if THIS in args:
            item = args.index(THIS)
            args[item] = self.prev_func
            f = lambda value: self.func(*args[:item], args[item](value), *args[item+1:], **kwargs)
        elif THIS in kwargs.values():
            for var, value in kwargs.items():
                if THIS == value:
                    item = var
                    break
            f = lambda value: self.func(*args, **(kwargs | {item:self.prev_func(value)}))
        else:
            f = lambda value: self.func(self.prev_func(value), *args, **kwargs)

        # I'm not sure why this works atm for explicit args and kwargs
        inplace_func = (lambda value: value) if self.inplace else None

        return PipeOpening(self.name, _lambdify(f, inplace_func=inplace_func, loggable=False))