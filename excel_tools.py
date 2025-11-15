# excel_tools.py
import pandas as pd
from io import BytesIO
import pandas as pd


def text_to_excel_bytes(text):
    # هر خط: "علیرضا - دوشنبه - 16:00 تا 17:30"
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split('-')]
        if len(parts) >= 3:
            name = parts[0]
            day = parts[1]
            time_part = parts[2]
            times = [t.strip() for t in time_part.split('تا')]
            start = times[0] if times else ''
            end = times[1] if len(times) > 1 else ''
            rows.append({'name': name, 'day': day,
                        'start_time': start, 'end_time': end})
    df = pd.DataFrame(rows)
    bio = BytesIO()
    df.to_excel(bio, index=False, engine='openpyxl')
    bio.seek(0)
    return bio


def excel_bytes_to_text(bytes_data):
    bio = BytesIO(bytes_data)
    df = pd.read_excel(bio, engine='openpyxl')
    lines = []
    for _, r in df.iterrows():
        # Use pandas-safe checks to avoid 'nan' strings
        def cell_val(key, default=''):
            if key in r and not pd.isna(r[key]):
                return str(r[key])
            return default

        name = cell_val('name')
        day = cell_val('day')
        start = cell_val('start_time')
        end = cell_val('end_time')
        lines.append(f"{name} - {day} - {start} تا {end}")
    return "\n".join(lines)
