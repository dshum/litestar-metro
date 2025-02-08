import logging
import time
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)


@contextmanager
def execution_time():
    begin = time.time()
    yield
    end = time.time()
    logging.info(f"execution time: {end - begin:.3f} sec")


def func1(num: int):
    for i in range(1_000_000):
        result = str(num)[-1] == "8"


def func2(num: int):
    for i in range(1_000_000):
        result = num % 10 == 8


with execution_time():
    func1(108)

with execution_time():
    func2(108)
