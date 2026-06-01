import json
import logging
import time
from typing import Callable
from fastapi import Request


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(message)s")
    # these are noisy
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)


def json_log(**fields) -> None:
    # Ensure timestamp and level exist
    record = {"ts": time.strftime('%Y-%m-%dT%H:%M:%S%z'), **fields}
    print(json.dumps(record, ensure_ascii=False), flush=True)


async def request_logger_middleware(request: Request, call_next: Callable):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)
        json_log(level="INFO", msg="request", path=str(request.url.path), method=request.method,
                 status=response.status_code, latency_ms=latency_ms)
        return response
    except Exception as exc:  # pragma: no cover - behavior observed in integration
        latency_ms = int((time.perf_counter() - start) * 1000)
        json_log(level="ERROR", msg="unhandled_error", path=str(request.url.path), method=request.method,
                 status=500, latency_ms=latency_ms, error=str(exc))
        raise
