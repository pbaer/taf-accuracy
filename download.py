import requests
import os
import re
import calendar
import time

# Download historical METAR and TAF data for a given ICAO airport identifier, year, and month
# An example URL is: https://www.ogimet.com/display_metars2.php?lang=en&lugar=kpae&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=2011&mes=02&day=14&hora=16&anof=2011&mesf=02&dayf=20&horaf=16&minf=59&send=send
# The METAR and TAF data is contained within a single set of <pre> </pre> tags in the respose.
# The data between these tags is extracted and saved to a file with path raw_data/<airport ICAO identifier>/YYYY_MM.txt (the month for which the data is downloaded)
def download_historical_data(icao, year, month):
    # Determine the last day of the month
    last_day = calendar.monthrange(year, month)[1]

    # Build query parameters for the request
    params = {
        'lang': 'en',
        'lugar': icao,
        'tipo': 'ALL',
        'ord': 'REV',
        'nil': 'SI',
        'fmt': 'txt',
        'ano': year,
        'mes': f"{month:02}",
        'day': '01',
        'hora': '00',
        'anof': year,
        'mesf': f"{month:02}",
        'dayf': f"{last_day:02}",
        'horaf': '23',
        'minf': '59',
        'send': 'send'
    }

    url = "https://www.ogimet.com/display_metars2.php"
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Extract the text within the <pre> tags
    match = re.search(r"<pre[^>]*>(.*?)</pre>", response.text, re.DOTALL)
    if not match:
        raise ValueError("Unable to locate METAR/TAF data in the response.")
    data = match.group(1).strip()

    # Determine output file path and ensure directory exists
    directory = os.path.join("raw_data", icao)
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{year}_{month:02}.txt")

    # Save the extracted data into the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)

    return file_path

# Download for the selected airport and date range
icao = 'KCLM'
for year in range(2010, 2025):
    for month in range(1, 13):
        print(f'Downloading data for {icao} {year}-{month:02}')
        download_historical_data(icao, year, month)
        print('Sleeping...')
        time.sleep(60)