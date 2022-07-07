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
        name_msg, inplace_msg, args_msg, kwargs_msg = map(lambda msg: msg if len(msg) <= Pipe._MAX_LENGTH else msg[:Pipe._MAX_LENGTH-3] + '...', (name_msg, inplace_msg, args_msg, kwargs_msg))
        Pipe._logger.debug(f'{name_msg} was called{inplace_msg}with args [{args_msg}] and kwargs {{{kwargs_msg}}}')
        return func(*args, **kwargs)
    return lambda_

def _lambdify(func: _Callable[_P, _T], inplace_func: _Callable[..., _Any] | None, loggable: bool) -> _Callable[_P, _T]:
    """Convert the function to a named lambda function."""

    if inplace_func is not None:
        def lambda_(*args: _P.args, **kwargs: _P.kwargs):
            func(*args, **kwargs)
            return inplace_func(*args) # not actually sure what is going on here
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
        f = lambda value, *args, **kwargs: getattr(value, attr)(*args, **kwargs) if callable(getattr(value, attr)) else getattr(value, attr)
        f.__name__ = 'THIS.' + attr
        return _lambdify(f, inplace_func=None, loggable=False)

    def __getitem__(self, item: _Any) -> _Any:
        f = lambda value: value[item]
        f.__name__ = 'THIS[' + str(item) + ']'
        return _lambdify(f, inplace_func=None, loggable=False)

THIS = _THIS()
    
class Pipe:
    """Class for beginning pipes."""
    
    _logger = _logging.getLogger()
    _MAX_LENGTH = float("inf")
    
    @classmethod
    def push(cls, value: _Any) -> "PipeInput":
        """Push a specific value into the pipe."""
        return PipeInput(value)
    
    @classmethod
    def open(cls, name: str="<pyper3.Pipe>") -> "PipeOpening":
        """Open a pipe that accepts a certain input. Optionally, name it."""
        return PipeOpening(name, lambda value: value)
    
    @classmethod
    def join(cls, *funcs: _Callable[[_Any], _Any], name: str="<pyper3.Pipe>", inplace: bool=False, loggable: bool=True) -> _Callable[[_Any], _Any]:
        """
        Join several univariate functions.
        
        Parameters
        ----------
        *funcs: Callable[..., Any]
            The functions to be piped.
        name: str, default="<pyper3.Pipe>"
            The name of the pipe.
        inplace: bool, default=False
            Whether or not the function should return the original object.
        loggable: bool, default=True
            Whether or not the function should be loggable if logging is enabled.
            
        Notes
        -----
        When `inplace`, the pipe returns the original object and not a copy. The function is applied first, then the object is returned.
        """
        
        if len(funcs) < 1:
            raise ValueError(f"There must be at least one function to join: funcs={funcs}")
        
        opened_pipe = Pipe.open(name)
        for func in funcs:
            opened_pipe = opened_pipe.pipe(func, loggable=loggable)()
        closed_pipe = opened_pipe.close()
        
        inplace_func = (lambda value: value) if inplace else None
        return _lambdify(closed_pipe, inplace_func, loggable=loggable)
    
    @classmethod
    def setup_logging(cls, name: str, level: int=_logging.DEBUG, fmt: str='%(name)s/%(levelname)s: %(message)s', max_length: int | float | None =float("inf")) -> None:
        """
        Enable logging.
        
        Parameters
        ----------
        name: str
            Name of the logger.
        level: int, default=logging.DEBUG
            What level to set the logger to. All pipe logs are `logging.DEBUG` level.
        fmt: str, default='%(name)s/%(levelname)s: %(message)s'
            See `logging` for how `logging.Formatter` works.
        max_length: int | float | None, default=float("inf")
            The max length of each part of a logging message, i.e. name, inplace, args, kwargs. Must be at least 3.
        """
        cls._logger = _logging.getLogger(name)
        cls._logger.setLevel(level)

        handler = _logging.StreamHandler()
        handler.setFormatter(_logging.Formatter(fmt))
        cls._logger.addHandler(handler)
        
        if max_length < 3 or (isinstance(max_length, float) and max_length != float("inf")):
            raise ValueError(f"Parameter max_length should be an integer that is at least 3, but got {max_length} instead.")
        if max_length is None:
            max_length = float("inf")
        cls._MAX_LENGTH = max_length
        
class PipeInput:
    """Pipes with inputs specified. Generally, avoid instantiating this class directly."""
    
    def __init__(self, value) -> None:
        """Create a `PipeInput` with a certain value."""
        self.value = value

    def pipe(self, func: _Callable[..., _Any], *, inplace: bool=False, loggable: bool=True) -> "PipeOutput":
        """
        Apply a function.
        
        Parameters
        ----------
        func: Callable[..., Any]
            The function to be piped.
        inplace: bool, default=False
            Whether or not the function should return the original object.
        loggable: bool, default=True
            Whether or not the function should be loggable if logging is enabled.
            
        Notes
        -----
        When `inplace`, the pipe returns the original object and not a copy. The function is applied first, then the object is returned.
        """
        inplace_func = (lambda *args: self.value) if inplace else None
        return PipeOutput(_lambdify(func, inplace_func=inplace_func, loggable=loggable), self.value)
    
    def pop(self) -> _Any:
        """Retrieve the resulting value."""
        return self.value
    
class PipeOutput:
    """Pipes where the inputs are applied to the functions. Generally, avoid using this class directly."""
    
    def __init__(self, func: _Callable[..., _Any], input: _Any) -> None:
        """Create a `PipeOutput` with on a certain function and its input."""
        self.func = func
        self.input = input
    
    def __call__(self, *args: _Any, **kwargs: _Any) -> "PipeInput":
        """
        Specify the arguments of the piped function.
        
        Notes
        -----
        THIS cannot be used within expressions, including starred expressions. However, it can be used to substitute a positional or keyword argument. If THIS is not explicitly given, it is assumed to be the first positional argument.
        """
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
    """Pipes without inputs specified. Generally, avoid instantiating this class directly."""
    
    def __init__(self, name: str, func: _Callable[..., _Any]) -> None:
        """Create a `PipeOpening` with a name and function."""
        self.name = name
        self.func = func
        
    def pipe(self, func: _Callable[..., _Any], *, inplace: bool=False, loggable: bool=True) -> "PipeJoiner":
        """
        Apply a function.
        
        Parameters
        ----------
        func: Callable[..., Any]
            The function to be piped.
        inplace: bool, default=False
            Whether or not the function should return the original object.
        loggable: bool, default=True
            Whether or not the function should be loggable if logging is enabled.
            
        Notes
        -----
        When `inplace`, the pipe returns the original object and not a copy. The function is applied first, then the object is returned.
        """
        return PipeJoiner(self.name, self.func, func, inplace, loggable)
    
    def close(self) -> _Callable[[_Any], _Any]:
        """Get the resulting univariate function."""
        self.func.__name__ = self.name
        return self.func
    
class PipeJoiner:
    """Pipes where the nonspecified inputs would be applied to the functions. Generally, avoid using this class directly."""
    
    def __init__(self, name: str, prev_func: _Callable[..., _Any], func: _Callable[..., _Any], inplace: bool, loggable: bool) -> None:
        """Create a `PipeJoiner` with a name between two functions."""
        self.name = name
        self.prev_func = prev_func
        self.func = func
        if loggable:
            self.func = _add_logging(self.func, inplace)
        self.inplace = inplace
        
    def __call__(self, *args: _Any, **kwargs: _Any) -> "PipeOpening":
        """
        Specify the arguments of the piped function.
        
        Notes
        -----
        THIS cannot be used within expressions, including starred expressions. However, it can be used to substitute a positional or keyword argument. If THIS is not explicitly given, it is assumed to be the first positional argument.
        """
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
            
        inplace_func = (lambda value: self.prev_func(value)) if self.inplace else None

        return PipeOpening(self.name, _lambdify(f, inplace_func=inplace_func, loggable=False))