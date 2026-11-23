import logging
import time

request_logger = logging.getLogger("sites_cms.request")

STATUS_CHECK_PATH = "/_status/check"


class NoIndexMiddleware:
    """Ask search engines not to index anything served from here.

    Readers see content on the websites. This service has no public pages.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Robots-Tag"] = "noindex"
        return response


class RequestLogMiddleware:
    """Log one line per request. Used in production only."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.monotonic()
        response = self.get_response(request)
        # The platform calls the health check every few seconds.
        if request.path != STATUS_CHECK_PATH:
            request_logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000),
                },
            )
        return response
