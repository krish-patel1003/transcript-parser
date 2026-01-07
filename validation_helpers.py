import re
from typing import Any, Dict, List, Tuple

def _prep_lines(raw_text: str) -> List[str]:
    lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return [" ".join(ln.strip().split()) for ln in lines if ln.strip()]


_TERM_RE = re.compile(r"^(Fall|Spring|Summer)\s+\d{4}$")
def _is_term_header(line: str) -> bool:
    return bool(_TERM_RE.match(line))


def _is_beginning_record_header(line: str) -> bool:
    return line.startswith("Beginning of") and line.endswith("Record")


def _is_course_table_header(line: str) -> bool:
    return (
        line.startswith("Course Description")
        and "Attempted" in line
        and "Earned" in line
        and "Grade" in line
    )


def _is_totals_header(line: str) -> bool:
    return (
        line.startswith("Attempted Earned")
        and "GPA" in line
        and "Units" in line
        and "Points" in line
    )


def _is_career_totals_header(line: str) -> bool:
    return line.endswith("Career Totals")
