from __future__ import annotations

import inspect
import sys
from contextlib import ContextDecorator
from functools import wraps
from logging import INFO, Logger, getLogger
from time import perf_counter
from typing import Awaitable, Callable, TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec  # nosec

    EllipsisType = type(Ellipsis)  # nosec
else:
    from types import EllipsisType  # nosec
    from typing import ParamSpec  # nosec


class timer(ContextDecorator):
    _message: str
    _logger: Logger | None
    _level: int
    _elapsed: float | None
    _start_time: float | None
    """A context manager that measures the time elapsed in a block of code."""

    def __init__(
        self,
        *,
        message: str = "Elapsed time: {:.3f}",
        logger: Logger | None = None,
        level: int = INFO,
    ) -> None:
        """A context manager that measures the time elapsed in a block of code.

        Parameters
        ----------
        message : str
            Message to log. Must contain a single format specifier
            for the elapsed time in seconds. optional
        logger : Logger | None, optional
            Logger to use, by default None
        level : int, optional
            Level to log at, by default INFO

        Examples
        --------
        >>> from cm_time import timer
        >>> with timer() as ct:
        >>>     pass
        >>> print(ct.elapsed)
        Output:
        Elapsed time: 0.000
        0.0
        """
        self._message = message
        self._logger = logger
        self._level = level
        self._elapsed = None
        self._start_time = None

    def __enter__(self) -> timer:
        self._start_time = perf_counter()
        return self

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: object | None,
    ) -> None:
        if self._start_time is None:
            raise RuntimeError("Timer was not started")
        assert self._start_time is not None  # nosec
        self._elapsed = perf_counter() - self._start_time
        if self._logger is not None:
            self._logger.log(self._level, self._message.format(self._elapsed))

    @property
    def elapsed(self) -> float | None:
        """Elapsed time in seconds."""
        return self._elapsed


_TParams = ParamSpec("_TParams")
_TResult = TypeVar("_TResult")


def timer_wrapped(
    *,
    message: str = "{func}: Elapsed time: {:.3f}",
    logger: Logger | EllipsisType | None = ...,
    level: int = INFO,
) -> Callable[
    [Callable[_TParams, _TResult]],
    Callable[_TParams, _TResult],
]:
    """A decorator that measures the time elapsed in a block of code.
    Asynchronous functions are supported.

    Parameters
    ----------
    message : str, optional
        Message to log. Must contain a single format specifier
        for the elapsed time, by default "Elapsed time: {:.3f}"
    logger : Logger | None, optional
        Logger to use, by default None
        If ... (default), use getLogger(func.__module__)
    level : int, optional
        Level to log at, by default INFO

    Returns
    -------
    Callable[[Callable[_TParams, _TResult]], Callable[_TParams, _TResult]]
        Wrapped function.
    """

    def inner(
        func: Callable[_TParams, _TResult | Awaitable[_TResult]],
    ) -> Callable[_TParams, _TResult | Awaitable[_TResult]]:
        replaced_message = message.replace("{func}", func.__qualname__)
        if isinstance(logger, EllipsisType):
            logger_: Logger | None = getLogger(func.__module__)
        else:
            logger_ = logger
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper_async(
                *args: _TParams.args, **kwargs: _TParams.kwargs
            ) -> _TResult:
                with timer(message=replaced_message, logger=logger_, level=level):
                    return await func(*args, **kwargs)  # type: ignore

            return wrapper_async
        else:

            @wraps(func)
            def wrapper(*args: _TParams.args, **kwargs: _TParams.kwargs) -> _TResult:
                with timer(message=replaced_message, logger=logger_, level=level):
                    return func(*args, **kwargs)  # type: ignore

            return wrapper

    return inner  # type: ignore
