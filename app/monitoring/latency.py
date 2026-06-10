import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def measure_latency() -> Iterator[dict[str, float]]:
    payload = {"elapsed_ms": 0.0}
    start = time.perf_counter()
    try:
        yield payload
    finally:
        payload["elapsed_ms"] = (time.perf_counter() - start) * 1000
