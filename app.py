import streamlit as st
import json
import pandas as pd
from pypdf import PdfReader

from parser import parse_transcript_text


# ============================
# Streamlit App Config
# ============================

st.set_page_config(
    page_title="Transcript Parser",
    layout="wide",
)

st.title("📄 Transcript Parser")
st.write("Upload a transcript PDF, parse it, and inspect the extracted data.")

# ============================
# File Upload
# ============================

uploaded_file = st.file_uploader(
    "Upload transcript PDF",
    type=["pdf"],
    accept_multiple_files=False,
)

raw_text = None
parsed = None

# ============================
# Extract PDF Text
# ============================

if uploaded_file is not None:
    st.success("PDF uploaded successfully")

    try:
        reader = PdfReader(uploaded_file)
        raw_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

        with st.expander("🔍 Raw Extracted Text"):
            st.text(raw_text)

    except Exception as e:
        st.error(f"Failed to read PDF: {e}")

# ============================
# Parse Button
# ============================

if raw_text and st.button("🚀 Parse Transcript"):
    try:
        parsed = parse_transcript_text(raw_text)
        st.success("Parsing completed successfully")

    except Exception as e:
        st.error(f"Parsing failed: {e}")

# ============================
# Data Viewing
# ============================

if parsed:
    tabs = st.tabs([
        "📦 Parsed JSON",
        "📚 Courses",
        "📊 Term Totals",
        "🎓 Career Totals",
        "⚠️ Warnings",
    ])

    # ----------------------------
    # JSON View
    # ----------------------------
    with tabs[0]:
        st.json(parsed)

    # ----------------------------
    # Courses DataFrame
    # ----------------------------
    with tabs[1]:
        rows = []
        student = parsed.get("student", {})

        for term in parsed.get("terms", []):
            for course in term.get("courses", []):
                rows.append({
                    "student_name": student.get("name"),
                    "student_id": student.get("student_id"),
                    "term": term.get("term"),
                    "program": term.get("program"),
                    "plan": term.get("plan"),
                    "course_code": course.get("code"),
                    "course_title": course.get("title"),
                    "attempted_units": course.get("attempted_units"),
                    "earned_units": course.get("earned_units"),
                    "grade": course.get("grade"),
                    "points": course.get("points"),
                })

        if rows:
            df_courses = pd.DataFrame(rows)
            st.dataframe(df_courses, use_container_width=True)
        else:
            st.info("No course data found")

    # ----------------------------
    # Term Totals DataFrame
    # ----------------------------
    with tabs[2]:
        rows = []

        for term in parsed.get("terms", []):
            for totals_type, totals in term.get("totals", {}).items():
                rows.append({
                    "term": term.get("term"),
                    "totals_type": totals_type,
                    "gpa": totals.get("gpa"),
                    "attempted": totals.get("attempted"),
                    "earned": totals.get("earned"),
                    "gpa_units": totals.get("gpa_units"),
                    "points": totals.get("points"),
                })

        if rows:
            df_totals = pd.DataFrame(rows)
            st.dataframe(df_totals, use_container_width=True)
        else:
            st.info("No term totals found")

    # ----------------------------
    # Career Totals DataFrame
    # ----------------------------
    with tabs[3]:
        rows = []

        for totals_type, totals in parsed.get("career_totals", {}).items():
            rows.append({
                "totals_type": totals_type,
                "gpa": totals.get("gpa"),
                "attempted": totals.get("attempted"),
                "earned": totals.get("earned"),
                "gpa_units": totals.get("gpa_units"),
                "points": totals.get("points"),
            })

        if rows:
            df_career = pd.DataFrame(rows)
            st.dataframe(df_career, use_container_width=True)
        else:
            st.info("No career totals found")

    # ----------------------------
    # Warnings
    # ----------------------------
    with tabs[4]:
        warnings = parsed.get("raw", {}).get("warnings", [])
        if warnings:
            for w in warnings:
                st.warning(w)
        else:
            st.success("No parser warnings")

# ============================
# Footer
# ============================

st.markdown("---")
st.caption("Transcript Parser – PDF structure aware, parser-grade")
