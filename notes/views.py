import json

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Note


@require_GET
def healthz(request):
    """Liveness: process is up."""
    return JsonResponse({'status': 'ok'})


@require_GET
def readyz(request):
    """Readiness: database is reachable."""
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ready'})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def notes(request):
    if request.method == 'GET':
        data = list(Note.objects.values('id', 'title', 'body')[:100])
        return JsonResponse({'results': data})
    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid json'}, status=400)
    title = (payload.get('title') or '').strip()
    if not title:
        return JsonResponse({'error': 'title is required'}, status=400)
    note = Note.objects.create(title=title[:200], body=payload.get('body', ''))
    return JsonResponse({'id': note.id, 'title': note.title}, status=201)
