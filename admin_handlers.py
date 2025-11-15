# admin_handlers.py
from excel_tools import text_to_excel_bytes, excel_bytes_to_text
import database
import re
import uuid
import logging

logger = logging.getLogger(__name__)


def parse_and_add_students_from_text(text):
    # متن چند خطی: هر خط "علیرضا - دوشنبه - 16:00 تا 17:30 - STU1001"
    added = []
    line_re = re.compile(
        r"^(?P<name>[^-]+)-\s*(?P<day>[^-]+)-\s*(?P<time>[^-]+)(?:-\s*(?P<code>\S+))?$")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = line_re.match(line)
        if not m:
            logger.warning("Could not parse line: %s", line)
            continue
        name = m.group('name').strip()
        day = m.group('day').strip()
        time_part = m.group('time').strip()
        code = m.group('code') if m.group(
            'code') else f"STU{uuid.uuid4().hex[:6].upper()}"
        times = [t.strip()
                 for t in re.split(r"\bتا\b|to|-", time_part) if t.strip()]
        start = times[0] if times else ''
        end = times[1] if len(times) > 1 else ''
        try:
            database.add_student(code, name, day, start, end, level="beginner")
            added.append((code, name))
        except Exception as e:
            logger.exception("Error adding student %s (%s): %s", name, code, e)
    return added


def text_to_excel_file(text):
    return text_to_excel_bytes(text)


def excel_bytes_to_text_wrap(bytes_data):
    return excel_bytes_to_text(bytes_data)
