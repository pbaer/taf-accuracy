import calendar
import os
from metar_taf_parser.parser.parser import MetarParser
from metar_taf_parser.parser.parser import TAFParser

def load_metar_taf_file(year, month, file_path):
    num_days = calendar.monthrange(year, month)[1]
    parsed_objects_by_day = {}
    for i in range(1, num_days + 1):
        day = f"{i:02}"
        parsed_objects_by_day[day] = {}
        parsed_objects_by_day[day]["metars"] = [[] for _ in range(24)]
        parsed_objects_by_day[day]["tafs"] = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#") or set(line) == {"#"}:
            i += 1
            continue

        if "METAR" in line or "SPECI" in line:
            if line.endswith("NIL="):
                i += 1
                continue
            prefix_format = "YYYYMMDDHHmm METAR "
            metar_str = line[len(prefix_format):].rstrip("=")
            try:
                parsed_metar = MetarParser().parse(metar_str)
                assert parsed_metar.message == metar_str
                day = f"{parsed_metar.day:02}"
                hour = parsed_metar.time.hour
                if not any(metar.message == parsed_metar.message for metar in parsed_objects_by_day[day]["metars"][hour]):
                    parsed_objects_by_day[day]["metars"][hour].append(parsed_metar)
            except Exception as e:
                print(f"Error parsing METAR line: {line}\n{e}")
        else:
            taf_lines = [line]
            while not line.endswith("="):
                i += 1
                line = lines[i].strip()
                taf_lines.append(line)
            taf_str = " ".join(taf_lines)
            
            prefix_format = "YYYYMMDDHHmm "
            taf_str = taf_str[len(prefix_format):].rstrip("=")
            if not taf_str.startswith("TAF"):
                taf_str = "TAF " + taf_str

            try:
                parsed_taf = TAFParser().parse(taf_str)
                assert parsed_taf.message == taf_str
                day = f"{parsed_taf.day:02}"
                if not any(taf.message == parsed_taf.message for taf in parsed_objects_by_day[day]["tafs"]):
                    parsed_objects_by_day[day]["tafs"].append(parsed_taf)
            except Exception as e:
                print(f"Error parsing TAF lines: {taf_str}\n{e}")
        i += 1

    return parsed_objects_by_day

def load_all_metar_taf_files(root_folder):
    parsed_objects = {}
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".txt"):
                print(f"Parsing {file}...")
                file_path = os.path.join(root, file)
                parts = file_path.split(os.sep)
                icao = parts[-2]
                year, month = parts[-1].split('_')
                month = month.split('.')[0]

                if icao not in parsed_objects:
                    parsed_objects[icao] = {}
                if year not in parsed_objects[icao]:
                    parsed_objects[icao][year] = {}
                if month not in parsed_objects[icao][year]:
                    parsed_objects[icao][year][month] = []

                parsed_objects_by_day = load_metar_taf_file(int(year), int(month), file_path)
                parsed_objects[icao][year][month] = parsed_objects_by_day

    return parsed_objects

def validate(parsed_objects):
    total_days = 0
    total_hours = 0
    missing_taf_days = 0
    missing_metar_hours = 0
    for icao, _ in parsed_objects.items():
        for year in range(2010, 2025):
            for month in range(1, 13):
                num_days = calendar.monthrange(int(year), int(month))[1]
                for i in range(1, num_days + 1):
                    day = f"{i:02}"
                    total_days += 1
                    month_item = parsed_objects[icao][f"{year}"][f"{month:02}"]
                    if len(month_item[day]["tafs"]) < 4:
                        missing_taf_days += 1
                    for _, metars in enumerate(month_item[day]["metars"]):
                        total_hours += 1
                        if len(metars) == 0:
                            missing_metar_hours += 1
    print(f"Percentage of missing TAF days: {missing_taf_days / total_days * 100:.2f}%")
    print(f"Percentage of missing METAR hours: {missing_metar_hours / total_hours * 100:.2f}%")

parsed_objects = load_all_metar_taf_files('raw_data')
print("Successfully parsed all files")
validate(parsed_objects)
print("Validation complete")