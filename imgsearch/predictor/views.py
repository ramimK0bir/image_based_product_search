import time
from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from PIL import Image
from io import BytesIO
import requests
from utlities.text_classifier import predict


def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR")


def check_rate_limit(request):
    if request.session.get("user_role") == "admin":
        return True, None

    ip = get_client_ip(request)
    cache_key = f"rl:{ip}"
    now = time.time()
    limit = getattr(settings, "RATE_LIMIT", 10)
    period = getattr(settings, "RATE_PERIOD", 3600)

    history = cache.get(cache_key, [])
    history = [t for t in history if now - t < period]

    if len(history) >= limit:
        wait = int(period - (now - history[0]))
        mins, secs = divmod(wait, 60)
        msg = f"Rate limit exceeded. Try again in {mins}m {secs}s." if mins else f"Rate limit exceeded. Try again in {secs}s."
        return False, msg

    history.append(now)
    cache.set(cache_key, history, period)
    return True, None


def index(request):
    # hardcoded admin session grant — no login, just visit /?admin_secret=<value>
    secret = request.GET.get("admin_secret")
    if secret and secret == getattr(settings, "ADMIN_SECRET", ""):
        request.session["user_role"] = "admin"

    if request.method == "POST":
        url = request.POST.get("url", "").strip()

        if url:
            try:
                resp = requests.get(url, timeout=10)
                img = Image.open(BytesIO(resp.content))
            except Exception as e:
                return JsonResponse({"error": f"Could not fetch image: {e}"}, status=400)
        elif "image" in request.FILES:
            try:
                img = Image.open(request.FILES["image"])
            except Exception as e:
                return JsonResponse({"error": f"Invalid image: {e}"}, status=400)
        else:
            return JsonResponse({"error": "No image provided."}, status=400)

        allowed, wait_msg = check_rate_limit(request)
        if not allowed:
            return JsonResponse({"error": wait_msg}, status=429)

        results = predict(img)
        data = [
            {
                "label": label,
                "confidence": conf,
                "search_url": f"https://www.google.com/search?q={label.replace(' ', '+')}",
            }
            for label, conf in results
        ]
        return JsonResponse({"results": data})

    return render(request, "predictor/index.html")
