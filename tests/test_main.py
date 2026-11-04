from __future__ import annotations

import asyncio
from io import StringIO
from logging import INFO, Logger, StreamHandler, getLogger

import pytest

from cm_time import timer, timer_wrapped


@pytest.mark.parametrize(("wait", "wait_after"), [(0.01, 0.01), (0.02, 0.01)])
def test_basic_usage(wait: float, wait_after: float) -> None:
    with timer() as context_timer:
        asyncio.run(asyncio.sleep(wait))

    asyncio.run(asyncio.sleep(wait_after))

    assert context_timer.elapsed is not None
    assert context_timer.elapsed == pytest.approx(wait, abs=0.1)


def test_not_yet() -> None:
    with timer() as context_timer:
        assert context_timer.elapsed is None


def _get_string_logger(name: str = "test_logger") -> tuple[Logger, StringIO]:
    logger = getLogger(name)
    logger.setLevel(INFO)
    stream = StringIO()
    logger.addHandler(StreamHandler(stream))
    return logger, stream


def test_custom_logger() -> None:
    logger, stream = _get_string_logger()

    with timer(logger=logger, message="{:.3f}"):
        asyncio.run(asyncio.sleep(0.01))

    assert float(stream.getvalue()) == pytest.approx(0.01, abs=0.1)


def test_wrapped() -> None:
    _logger, stream = _get_string_logger(__name__)

    @timer_wrapped()
    def wrapped() -> None:
        pass

    wrapped()

    assert stream.getvalue().endswith("test_wrapped.<locals>.wrapped: Elapsed time: 0.000\n")


def test_wrapped_custom() -> None:
    logger, stream = _get_string_logger()

    @timer_wrapped(logger=logger)
    def wrapped() -> None:
        pass

    wrapped()

    assert stream.getvalue().endswith("test_wrapped_custom.<locals>.wrapped: Elapsed time: 0.000\n")


def test_wrapped_async() -> None:
    logger, stream = _get_string_logger()

    @timer_wrapped(logger=logger, message="{:.3f}")
    async def wrapped() -> None:
        await asyncio.sleep(0.01)

    asyncio.run(wrapped())

    assert float(stream.getvalue()) == pytest.approx(0.01, abs=0.1)


def test_error() -> None:
    with pytest.raises(RuntimeError, match="Timer was not started"):
        timer().__exit__(None, None, None)
