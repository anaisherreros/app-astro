from ..charts.calculator import calculate_chart

def get_chart_info(birth_date, birth_time, birth_place):

    if not birth_date or not birth_time or not birth_place:
        return {
            "error": "Missing required data",
            "required": ["birth_date", "birth_time", "birth_place"]
        }

    chart_data = calculate_chart(birth_date, birth_time, birth_place)

    return {
        "message": "Chart calculated successfully",
        "result": chart_data
    }