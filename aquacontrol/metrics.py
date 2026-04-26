import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

start_time = time.time()
request_counts = defaultdict(int)
status_codes = defaultdict(int)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_counts["total"] += 1
        response = await call_next(request)
        status_codes[response.status_code] += 1
        return response

def get_metrics(version: str) -> dict:
    uptime_seconds = time.time() - start_time
    return {
        "version": version,
        "start_time": start_time,
        "uptime_seconds": round(uptime_seconds, 2),
        "total_requests": request_counts.get("total", 0),
        "status_codes": dict(status_codes),
        "timestamp": time.time()
    }