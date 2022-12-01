import asyncio
from io import StringIO
from logging import INFO, Logger, StreamHandler, getLogger
from random import random
from unittest import IsolatedAsyncioTestCase

from parameterized import parameterized_class

from cm_timer import timer, timer_wrapped


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

    def get_string_logger(self) -> tuple[Logger, StringIO]:
        # Create a logger that will write to a string buffer
        logger = getLogger("test_logger")
        logger.setLevel(INFO)
        stream = StringIO()
        handler = StreamHandler(stream)
        logger.addHandler(handler)
        return logger, stream

    async def test_logger(self):
        logger, stream = self.get_string_logger()

        # Use the logger
        with timer(logger=logger, message="{:.3f}"):
            await asyncio.sleep(self.wait)
        await asyncio.sleep(self.wait_after)

        # Check the output
        self.assertAlmostEqual(float(stream.getvalue()), self.wait, delta=self.delta)

    def test_wrapped(self):
        logger, stream = self.get_string_logger()

        @timer_wrapped(logger=logger)
        def test():
            pass

        test()

        self.assertEqual(stream.getvalue(), "Elapsed time: 0.000\n")

    async def test_wrapped_async(self):
        logger, stream = self.get_string_logger()

        @timer_wrapped(logger=logger, message="{:.3f}")
        async def test():
            await asyncio.sleep(self.wait)

        await test()
        await asyncio.sleep(self.wait_after)

        self.assertAlmostEqual(float(stream.getvalue()), self.wait, delta=self.delta)
