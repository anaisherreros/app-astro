import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .interpretation.readings import generate_astrology_reading_with_usage
from .location.place import search_city_suggestions
from .services.chart_service import get_chart_info

logger = logging.getLogger(__name__)


def health(request):
    return JsonResponse({"status": "ok", "app": "astrology"})


@ensure_csrf_cookie
def chart_form(request):
    """
    Vista que solo devuelve la plantilla con el formulario básico.
    No hace cálculos ni valida: eso lo hace el frontend + la API JSON.
    """
    return render(request, "astrology/chart_form.html")


def chart(request):
    """
    Endpoint JSON que recibe los datos por querystring y devuelve el resultado.
    """
    birth_date = request.GET.get("birth_date")
    birth_time = request.GET.get("birth_time")
    birth_place = request.GET.get("birth_place")

    try:
        result = get_chart_info(birth_date, birth_time, birth_place)
        return JsonResponse(result)
    except Exception as e:
        import traceback
        return JsonResponse({
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, status=500)


def city_suggestions(request):
    """
    Endpoint JSON para sugerencias de ciudad en el autocomplete.
    """
    query = request.GET.get("q", "")
    suggestions = search_city_suggestions(query, limit=12)
    return JsonResponse({"results": suggestions})


@csrf_exempt
@require_POST
def interpretation(request):
    """
    POST JSON: { "chart": <dict calculate_chart>, "nombre": "opcional" }
    Devuelve interpretación completa vía Claude + uso de tokens.

    Sin verificación CSRF: el front solo envía JSON y en HTTPS/proxy (Railway)
    el token CSRF fallaba con 403. Este endpoint no cambia estado en BD; el
    riesgo principal es abuso de la API de Anthropic (mitigar con rate limit / auth mas adelante).
    """
    logger.info("interpretation: POST recibido (Content-Length=%s)", request.META.get("CONTENT_LENGTH", "?"))

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.warning("interpretation: cuerpo no es JSON valido")
        return JsonResponse({"error": "JSON invalido"}, status=400)

    chart = body.get("chart")
    if not chart or not isinstance(chart, dict):
        logger.warning("interpretation: falta chart o no es dict (keys body=%s)", list(body.keys()))
        return JsonResponse({"error": "Falta el objeto chart"}, status=400)

    nombre = (body.get("nombre") or "").strip() or None
    if nombre:
        chart = {**chart, "nombre": nombre}

    chart_keys = list(chart.keys())
    aspects_n = len(chart.get("aspects") or [])
    logger.info(
        "interpretation: carta lista (keys=%s, aspectos=%s, nombre=%s)",
        chart_keys,
        aspects_n,
        bool(nombre),
    )

    try:
        text, usage = generate_astrology_reading_with_usage(chart)
        logger.info(
            "interpretation: OK Claude (input_tokens=%s output_tokens=%s chars=%s)",
            usage.input_tokens,
            usage.output_tokens,
            len(text or ""),
        )
        return JsonResponse(
            {
                "interpretation": text,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
            }
        )
    except ValueError as exc:
        logger.error("interpretation: configuracion o API (%s)", exc)
        return JsonResponse({"error": str(exc)}, status=503)
    except Exception as exc:
        import traceback

        tb = traceback.format_exc()
        logger.exception("interpretation: error llamando a Claude")
        return JsonResponse(
            {"error": str(exc), "traceback": tb},
            status=500,
        )