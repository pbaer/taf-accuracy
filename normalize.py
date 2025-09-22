import datetime
from metar_taf_parser.parser.parser import Metar
from metar_taf_parser.parser.parser import TAF

def compute_ceiling(clouds: list):
    for cloud in clouds:
        if cloud.quantity.name in ["BKN", "OVC"]:
            return int(cloud.height)
    return None

def convert_visibility(visibility: str):
    if visibility == "":
        return -1
    if visibility.endswith("m"):
        return float(visibility[:-1]) / 1609.344
    if visibility == "M1/4SM":
        return 0.25
    if visibility.endswith("SM"):
        visibility = visibility[:-2]
    if " " in visibility:
        parts = visibility.split(" ")
        return float(parts[0]) + float(parts[2]) / 10
    if "/" in visibility:
        parts = visibility.split("/")
        return float(parts[0]) / float(parts[1])
    return float(visibility)

def normalize_metar(icao, year, month, day, metar: Metar):
    return {
        "icao": icao,
        "time_year": year,
        "time_month": month,
        "time_day": day,
        "time_hour": metar.time.hour,
        "time_minutes": metar.time.minute,
        "wind_degrees": None if metar.wind is None else metar.wind.degrees,
        "wind_speed": None if metar.wind is None else metar.wind.speed,
        "wind_gust": None if metar.wind is None else metar.wind.gust,
        "visibility": "" if metar.visibility is None else metar.visibility.distance,
        "ceiling": compute_ceiling(metar.clouds),
        "weather_conditions": len(metar.weather_conditions) > 0
    }

def generate_metar_stats(normalized_metars: list):
    stats = {
        "wind_degrees": {},
        "wind_speed": {},
        "wind_gust": {},
        "visibility": {},
        "ceiling": {},
        "weather_conditions": {}
    }
    for metar in normalized_metars:
        for key in stats.keys():
            if key.startswith("time_"):
                continue
            if metar[key] not in stats[key]:
                stats[key][metar[key]] = 0
            stats[key][metar[key]] += 1
    for key in stats.keys():
        stats[key] = sorted(stats[key].items(), key=lambda x: x[0] if x[0] is not None else 0)
        
    return stats

# Given a parsed TAF object from parse.py, produce a simplified representation as follows:
# - Calculate unique, non-overlapping time ranges for each TAF's validity period
# - For each such time range, determine the following weather parameters:
#  - Wind direction (degrees), speed (knots), max gust (knots)
#  - Visibility (in floating point statute miles, capped at 6.0)
#  - Ceiling (in feet, capped at 5000 AGL)
#  - Precipitation (boolean - just yes/no)
def normalize_taf(taf: TAF):
    # todo
    return
