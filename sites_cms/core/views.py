from django.conf import settings
from django.db import DatabaseError, connection
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def status_check(request):
    """Tell the platform whether this unit can serve requests.

    Answers 200 with the running commit when the database is reachable and
    503 when it is not. Needs no login.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse(
            {"status": "error", "database": "unreachable"}, status=503
        )
    return JsonResponse({"status": "ok", "commit": settings.COMMIT_ID})


@require_GET
def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /\n", content_type="text/plain"
    )
