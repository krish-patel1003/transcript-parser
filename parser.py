
import re
from typing import Any, Dict, List, Tuple
from validation_helpers import (
    _prep_lines,
    _is_term_header,
    _is_beginning_record_header,
    _is_course_table_header,
    _is_totals_header,
    _is_career_totals_header,
)
from parsing_helpers import (
    _parse_totals_line, 
    _parse_career_totals_line, 
    _is_course_code_line, 
    _parse_course
)


def parse_transcript_text(raw_text: str) -> Dict[str, Any]:
    """
    Parse extracted transcript text (like pypdf's page.extract_text()) into a structured dict.
    """

    lines = _prep_lines(raw_text)

    out: Dict[str, Any] = {
        "student": {"name": None, "student_id": None, "print_date": None},
        "terms": [],
        "career_totals": {},
        "raw": {"warnings": []},
    }

    i = 0
    n = len(lines)

    # ----------------------------
    # 1) HEADER
    # ----------------------------
    while i < n:
        line = lines[i]

        if _is_beginning_record_header(line) or _is_term_header(line):
            break

        m = re.match(r"^Name:\s*(.+)$", line)
        if m:
            out["student"]["name"] = m.group(1).strip()

        m = re.match(r"^Student ID:\s*(\d+)$", line)
        if m:
            out["student"]["student_id"] = m.group(1)

        m = re.match(r"^Print Date:\s*(\d{2}/\d{2}/\d{4})$", line)
        if m:
            out["student"]["print_date"] = m.group(1)

        i += 1

    # Advance past "Beginning of ... Record"
    while (
        i < n
        and not _is_beginning_record_header(lines[i])
        and not _is_term_header(lines[i])
    ):
        i += 1

    if i < n and _is_beginning_record_header(lines[i]):
        i += 1

    # ----------------------------
    # 2) TERMS
    # ----------------------------
    while i < n:
        line = lines[i]

        if _is_career_totals_header(line):
            break

        if not _is_term_header(line):
            i += 1
            continue

        term_obj: Dict[str, Any] = {
            "term": line,
            "program": None,
            "plan": None,
            "courses": [],
            "totals": {},
        }
        i += 1

        # Program / Plan
        while i < n:
            line = lines[i]
            if line.startswith("Program:"):
                term_obj["program"] = line.replace("Program:", "", 1).strip()
                i += 1
                continue
            if line.startswith("Plan:"):
                term_obj["plan"] = line.replace("Plan:", "", 1).strip()
                i += 1
                continue
            break

        # Course table header
        while i < n and not _is_course_table_header(lines[i]):
            if _is_term_header(lines[i]) or _is_career_totals_header(lines[i]):
                break
            i += 1

        if i < n and _is_course_table_header(lines[i]):
            i += 1

        # Courses
        while i < n:
            line = lines[i]

            if _is_totals_header(line):
                break
            if _is_term_header(line) or _is_career_totals_header(line):
                break

            if _is_course_code_line(line):
                course, i = _parse_course(lines, i, out["raw"]["warnings"])
                term_obj["courses"].append(course)
                continue

            i += 1

        # Totals blocks
        while i < n and _is_totals_header(lines[i]):
            i += 1
            while i < n:
                line = lines[i]

                if _is_totals_header(line):
                    break
                if _is_term_header(line) or _is_career_totals_header(line):
                    break

                parsed = _parse_totals_line(line)
                if parsed:
                    key, payload = parsed
                    term_obj["totals"][key] = payload

                i += 1

        out["terms"].append(term_obj)

    # ----------------------------
    # 3) CAREER TOTALS
    # ----------------------------
    if i < n and _is_career_totals_header(lines[i]):
        i += 1
        while i < n:
            line = lines[i]

            if line.startswith("End of"):
                break

            parsed = _parse_career_totals_line(line)
            if parsed:
                key, payload = parsed
                out["career_totals"][key] = payload

            i += 1

    return out
