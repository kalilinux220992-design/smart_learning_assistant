import json
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


def _add_cors_headers(response, request):
    origin = request.headers.get('Origin') or request.headers.get('origin')
    if origin:
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def _resolve_path(root_path, target_path):
    root = Path(root_path).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if not target_path:
        return root

    candidate = Path(target_path)
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        return root
    return candidate


def home(request):
    stats_file = getattr(settings, 'WATCH_STATS_FILE', settings.BASE_DIR / 'watch_stats.json')
    today_key = datetime.now().strftime('%Y-%m-%d')
    watch_categories = {}
    try:
        with Path(stats_file).open('r', encoding='utf-8') as handle:
            watch_categories = json.load(handle).get(today_key, {}).get('categories', {})
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return render(request, 'index.html', {'watch_categories': watch_categories})


@csrf_exempt
def watch_stats_api(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        return _add_cors_headers(response, request)

    if request.method != 'POST':
        response = JsonResponse({'error': 'Method not allowed'}, status=405)
        return _add_cors_headers(response, request)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    stats_file = getattr(settings, 'WATCH_STATS_FILE', settings.BASE_DIR / 'watch_stats.json')
    stats_path = Path(stats_file)

    today_key = datetime.now().strftime('%Y-%m-%d')
    existing = {}
    if stats_path.exists():
        with stats_path.open('r', encoding='utf-8') as handle:
            existing = json.load(handle)

    today_stats = existing.setdefault(today_key, {'total_seconds': 0, 'categories': {}})
    today_stats['total_seconds'] = int(today_stats.get('total_seconds', 0)) + int(payload.get('total_seconds', 0))
    categories = today_stats.setdefault('categories', {})
    for name, seconds in payload.get('categories', {}).items():
        categories[name] = int(categories.get(name, 0)) + int(seconds)

    existing[today_key] = today_stats

    with stats_path.open('w', encoding='utf-8') as handle:
        json.dump(existing, handle, indent=2)

    response = JsonResponse({'status': 'ok', 'stats': today_stats, 'date': today_key})
    return _add_cors_headers(response, request)


def watch_stats_page(request):
    stats_file = getattr(settings, 'WATCH_STATS_FILE', settings.BASE_DIR / 'watch_stats.json')
    stats_path = Path(stats_file)

    stats = {}
    if stats_path.exists():
        with stats_path.open('r', encoding='utf-8') as handle:
            stats = json.load(handle)

    today_key = datetime.now().strftime('%Y-%m-%d')
    today_stats = stats.get(today_key, {'total_seconds': 0, 'categories': {}})
    recorded_categories = today_stats.get('categories', {})
    category_names = ['coding', 'lectures', 'news', 'entertainment', 'other']
    categories = {
        name: int(recorded_categories.get(name, 0))
        for name in category_names
    }
    for name, seconds in recorded_categories.items():
        if name not in categories:
            categories[name] = int(seconds)
    category_stats = []
    for name, seconds in categories.items():
        minutes = round(int(seconds) / 60, 1)
        bar_height = min(100, round((minutes / 500) * 100, 2)) if minutes > 0 else 0
        category_stats.append({
            'name': name,
            'seconds': int(seconds),
            'minutes': minutes,
            'bar_height': bar_height,
        })

    total_minutes = round(int(today_stats.get('total_seconds', 0)) / 60, 1)
    response = render(request, 'watch_stats.html', {
        'date': today_key,
        'total_seconds': today_stats.get('total_seconds', 0),
        'total_minutes': total_minutes,
        'categories': categories,
        'category_stats': category_stats,
    })
    return response


def clear_today_watch_stats(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    stats_file = getattr(settings, 'WATCH_STATS_FILE', settings.BASE_DIR / 'watch_stats.json')
    stats_path = Path(stats_file)
    today_key = datetime.now().strftime('%Y-%m-%d')

    if stats_path.exists():
        with stats_path.open('r', encoding='utf-8') as handle:
            stats = json.load(handle)
        stats.pop(today_key, None)
        with stats_path.open('w', encoding='utf-8') as handle:
            json.dump(stats, handle, indent=2)

    reset_file = Path(getattr(settings, 'WATCH_STATS_RESET_FILE', settings.BASE_DIR / 'watch_stats_reset.txt'))
    reset_file.write_text(datetime.now().isoformat(), encoding='utf-8')

    return redirect('watch_stats_page')


def watch_stats_reset_token(request):
    if request.method != 'GET':
        response = JsonResponse({'error': 'Method not allowed'}, status=405)
        return _add_cors_headers(response, request)

    reset_file = Path(getattr(settings, 'WATCH_STATS_RESET_FILE', settings.BASE_DIR / 'watch_stats_reset.txt'))
    token = reset_file.read_text(encoding='utf-8') if reset_file.exists() else ''
    response = JsonResponse({'reset_token': token})
    return _add_cors_headers(response, request)


def attendance_page(request):
    return render(request, 'attendance.html')


def favicon(request):
    return HttpResponse(status=204)
