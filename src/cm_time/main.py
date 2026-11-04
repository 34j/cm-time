from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from contextlib import ContextDecorator
from functools import wraps
from logging import INFO, Logger, getLogger
from time import perf_counter
from types import EllipsisType, TracebackType
from typing import Any, ParamSpec, Self, TypeVar, cast


class Timer(ContextDecorator):
    """Measure the time elapsed in a block of code."""

    _message: str
    _logger: Logger | None
    _level: int
    _elapsed: float | None
    _start_time: float | None

    def __init__(
        self,
        *,
        message: str = "Elapsed time: {:.3f}",
        logger: Logger | None = None,
        level: int = INFO,
    ) -> None:
        """Initialize a timer.

        Parameters
        ----------
        message : str
            Message to log. Must contain a single format specifier
            for the elapsed time in seconds.
        logger : Logger | None, optional
            Logger to use, by default None
        level : int, optional
            Level to log at, by default INFO

        Examples
        --------
        >>> from cm_time import timer
        >>> with timer() as ct:
        ...     pass
        >>> print(ct.elapsed)
        0.0

        """
        self._message = message
        self._logger = logger
        self._level = level
        self._elapsed = None
        self._start_time = None

    def __enter__(self) -> Self:
        """Start timing and return this timer.

        Returns
        -------
        Self
            This timer.

        """
        self._start_time = perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop timing and optionally log the elapsed time.

        Raises
        ------
        RuntimeError
            If the timer was not started.

        """
        del exc_type, exc_value, traceback
        start_time = self._start_time
        if start_time is None:
            raise RuntimeError("Timer was not started")
        self._elapsed = perf_counter() - start_time
        if self._logger is not None:
            self._logger.log(self._level, self._message.format(self._elapsed))

    @property
    def elapsed(self) -> float | None:
        """Return elapsed time in seconds."""
        return self._elapsed


timer = Timer

_TParams = ParamSpec("_TParams")
_TResult = TypeVar("_TResult")
_FUNC_PLACEHOLDER = "{func}"


def timer_wrapped(
    *,
    message: str = "{func}: Elapsed time: {:.3f}",
    logger: Logger | EllipsisType | None = ...,
    level: int = INFO,
) -> Callable[[Callable[_TParams, _TResult]], Callable[_TParams, _TResult]]:
    """Create a decorator that measures function execution time.

    Asynchronous functions are supported.

    Parameters
    ----------
    message : str, optional
        Message to log. Must contain a single format specifier
        for the elapsed time, by default "Elapsed time: {:.3f}"
    logger : Logger | None, optional
        Logger to use, by default None. If ... (default), use the
        logger for the decorated function's module.
    level : int, optional
        Level to log at, by default INFO

    Returns
    -------
    Callable[[Callable[_TParams, _TResult]], Callable[_TParams, _TResult]]
        A decorator that wraps a function.

    """

    def inner(
        func: Callable[_TParams, _TResult | Awaitable[_TResult]],
    ) -> Callable[_TParams, _TResult | Awaitable[_TResult]]:
        func_name = getattr(func, "__qualname__", type(func).__qualname__)
        module_name = getattr(func, "__module__", type(func).__module__)
        replaced_message = message.replace(_FUNC_PLACEHOLDER, func_name)
        if isinstance(logger, EllipsisType):
            logger_: Logger | None = getLogger(module_name)
        else:
            logger_ = logger
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper_async(
                *args: _TParams.args,
                **kwargs: _TParams.kwargs,
            ) -> _TResult:
                with timer(message=replaced_message, logger=logger_, level=level):
                    return await func(*args, **kwargs)

            return wrapper_async

        @wraps(func)
        def wrapper(*args: _TParams.args, **kwargs: _TParams.kwargs) -> _TResult:
            with timer(message=replaced_message, logger=logger_, level=level):
                return cast("_TResult", func(*args, **kwargs))

        return wrapper

    return cast("Any", inner)
