from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, date
from collections import defaultdict


class APIGatewayMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_store = defaultdict(lambda: defaultdict(int))

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        method = request.method

  
        if path == "/api/v1/listings/" and method == "GET":
            today = str(date.today())
            current_count = self.rate_limit_store[client_ip][today]

            if current_count >= 3:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Maximum 3 queries per day.",
                        "limit": 3,
                        "reset": "tomorrow"
                    }
                )

            self.rate_limit_store[client_ip][today] += 1

            old_dates = [d for d in self.rate_limit_store[client_ip] if d != today]
            for d in old_dates:
                del self.rate_limit_store[client_ip][d]

        # Logging
        start_time = datetime.now()
        response = await call_next(request)
        duration = (datetime.now() - start_time).total_seconds()

        print(
            f"[GATEWAY] {method} {path} "
            f"| IP: {client_ip} "
            f"| Status: {response.status_code} "
            f"| Duration: {duration:.3f}s"
        )

        if path == "/api/v1/listings/" and method == "GET":
            today = str(date.today())
            remaining = max(0, 3 - self.rate_limit_store[client_ip][today])
            response.headers["X-RateLimit-Limit"] = "3"
            response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response