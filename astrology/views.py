from django.http import JsonResponse
from pathlib import Path
import json
import time

from .services.chart_service import get_chart_info


def health(request):
    return JsonResponse({"status": "ok", "app": "astrology"})


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