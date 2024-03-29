from __future__ import annotations

import asyncio
from io import StringIO
from logging import INFO, Logger, StreamHandler, getLogger
from random import random
from unittest import IsolatedAsyncioTestCase

from parameterized import parameterized_class

from cm_time import timer, timer_wrapped


@parameterized_class(
    ("wait", "wait_after"), [(random() * 0.3, random() * 0.3) for _ in range(4)]
)
class TestCatchTime(IsolatedAsyncioTestCase):
    wait: float
    wait_after: float
    delta: float = 0.1

    async def test_basic_usage(self):
        with timer() as ct:
            await asyncio.sleep(self.wait)

        await asyncio.sleep(self.wait_after)

        self.assertNotEqual(ct.elapsed, None)
        assert ct.elapsed is not None
        self.assertAlmostEqual(ct.elapsed, self.wait, delta=self.delta)

    def test_not_yet(self):
        with timer() as ct:
            self.assertEqual(ct.elapsed, None)

    def get_string_logger(self, name: str = "test_logger") -> tuple[Logger, StringIO]:
        # Create a logger that will write to a string buffer
        logger = getLogger(name)
        logger.setLevel(INFO)
        stream = StringIO()
        handler = StreamHandler(stream)
        logger.addHandler(handler)
        return logger, stream

    async def test_custom_logger(self):
        logger, stream = self.get_string_logger()

        # Use the logger
        with timer(logger=logger, message="{:.3f}"):
            await asyncio.sleep(self.wait)
        await asyncio.sleep(self.wait_after)

        # Check the output
        self.assertAlmostEqual(float(stream.getvalue()), self.wait, delta=self.delta)

    def test_wrapped(self):
        @timer_wrapped()
        def test():
            pass

        logger, stream = self.get_string_logger(test.__module__)

        test()

        self.assertEqual(
            stream.getvalue(),
            "TestCatchTime.test_wrapped.<locals>.test: Elapsed time: 0.000\n",
        )

    def test_wrapped_custom(self):
        logger, stream = self.get_string_logger()

        @timer_wrapped(logger=logger)
        def test():
            pass

        test()

        self.assertEqual(
            stream.getvalue(),
            "TestCatchTime.test_wrapped_custom.<locals>.test: Elapsed time: 0.000\n",
        )

    async def test_wrapped_async(self):
        logger, stream = self.get_string_logger()

        @timer_wrapped(logger=logger, message="{:.3f}")
        async def test():
            await asyncio.sleep(self.wait)

        await test()
        await asyncio.sleep(self.wait_after)

        self.assertAlmostEqual(float(stream.getvalue()), self.wait, delta=self.delta)

    async def test_error(self):
        with self.assertRaises(RuntimeError):
            timer().__exit__(None, None, None)
