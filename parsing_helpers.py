
import re
from typing import Any, Dict, List, Optional, Tuple
from validation_helpers import _is_term_header, _is_totals_header, _is_career_totals_header

_COURSE_START_RE = re.compile(r"^([A-Z]{4})\s+(\d{3})\s+(.+)$")
def _is_course_code_line(line: str) -> bool:
    return bool(_COURSE_START_RE.match(line))

_NUMERIC_TAIL_RE = re.compile(
    r"""
    (?P<title>.*?)
    \s+
    (?P<attempted>\d+\.\d{3})
    \s+
    (?P<earned>\d+\.\d{3})
    (?:\s+(?P<grade>[A-F][+-]?))?
    (?:\s+(?P<points>\d+\.\d{3}))?
    $
    """,
    re.VERBOSE,
)


_NUMERIC_LINE_RE = re.compile(
    r"^(?P<attempted>\d+\.\d{3})\s+"
    r"(?P<earned>\d+\.\d{3})"
    r"(?:\s+(?P<grade>[A-F][+-]?))?"
    r"(?:\s+(?P<points>\d+\.\d{3}))?$"
)

def _parse_course(
    lines: List[str], i: int, warnings: List[str]
) -> Tuple[Dict[str, Any], int]:

    m = _COURSE_START_RE.match(lines[i])
    subject, number, rest = m.groups()

    title_parts = []
    attempted = earned = grade = points = None

    # --------------------------------
    # Case 1: numeric tail on SAME line
    # --------------------------------
    tail_match = _NUMERIC_TAIL_RE.match(rest)
    if tail_match:
        title_parts.append(tail_match.group("title").strip())
        attempted = float(tail_match.group("attempted"))
        earned = float(tail_match.group("earned"))
        grade = tail_match.group("grade")
        pts = tail_match.group("points")
        points = float(pts) if pts else None
        i += 1

    else:
        # --------------------------------
        # Case 2: title spans multiple lines
        # --------------------------------
        title_parts.append(rest.strip())
        i += 1

        while i < len(lines):
            line = lines[i]

            if (
                _is_totals_header(line)
                or _is_term_header(line)
                or _is_career_totals_header(line)
            ):
                warnings.append(f"Course {subject} {number}: terminated early.")
                break

            if _is_course_code_line(line):
                warnings.append(f"Course {subject} {number}: next course before numeric line.")
                break

            # numeric-only line
            numeric_match = _NUMERIC_LINE_RE.match(line)
            if numeric_match:
                attempted = float(numeric_match.group("attempted"))
                earned = float(numeric_match.group("earned"))
                grade = numeric_match.group("grade")
                pts = numeric_match.group("points")
                points = float(pts) if pts else None
                i += 1
                break

            title_parts.append(line)
            i += 1

        if attempted is None:
            warnings.append(f"Course {subject} {number}: missing numeric data.")

    return {
        "code": f"{subject} {number}",
        "title": " ".join(title_parts),
        "attempted_units": attempted,
        "earned_units": earned,
        "grade": grade,
        "points": points,
    }, i


def _parse_totals_line(line: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    tail = re.search(r"(\d+\.\d{3})\s+(\d+\.\d{3})\s+(\d+\.\d{3})\s+(\d+\.\d{3})$", line)
    if not tail:
        return None

    attempted, earned, gpa_units, points = map(float, tail.groups())
    gpa_match = re.search(r"\bGPA\b[: ]+(\d+\.\d{3})", line)
    gpa = float(gpa_match.group(1)) if gpa_match else None

    if line.startswith("Term GPA"):
        key = "term"
    elif line.startswith("Combined GPA"):
        key = "combined"
    elif line.startswith("Cum GPA"):
        key = "cumulative"
    elif line.startswith("Transfer Cum GPA"):
        key = "transfer_cumulative"
    elif line.startswith("Combined Cum GPA"):
        key = "combined_cumulative"
    else:
        return None

    return key, {
        "gpa": gpa,
        "attempted": attempted,
        "earned": earned,
        "gpa_units": gpa_units,
        "points": points,
        "raw_line": line,
    }


def _parse_career_totals_line(line: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    return _parse_totals_line(line)