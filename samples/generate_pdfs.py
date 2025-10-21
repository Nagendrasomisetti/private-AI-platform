"""
Generate sample PDFs for PrivAI demo using reportlab.
Outputs:
 - policies.pdf (2-3 pages)
 - NAAC_criteria.pdf (2-3 pages)
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent


def draw_wrapped_text(c, text, x, y, max_width, leading=14):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words = text.split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if stringWidth(test, "Helvetica", 11) > max_width:
            c.drawString(x, y, line)
            y -= leading
            line = word
        else:
            line = test
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def gen_policies_pdf(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    # Page 1 - Academic Policies Overview
    c.setTitle("College Policies")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "College Academic Policies - 2024/2025")
    c.setFont("Helvetica", 11)
    y = height - 3*cm
    y = draw_wrapped_text(c,
        "This document outlines institutional policies for attendance, examinations, grading, code of conduct, and grievance redressal. All students are expected to follow the guidelines to ensure fairness and academic integrity.",
        2*cm, y, width - 4*cm)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y-10, "Attendance Policy")
    y -= 26
    c.setFont("Helvetica", 11)
    y = draw_wrapped_text(c,
        "A minimum of 75% attendance is mandatory for eligibility to appear in semester examinations. Medical and officially approved activities may be considered for condonation as per policy.",
        2*cm, y, width - 4*cm)
    c.showPage()

    # Page 2 - Examination & Conduct
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 2*cm, "Examination Policy")
    c.setFont("Helvetica", 11)
    y = height - 3*cm
    y = draw_wrapped_text(c,
        "Examination schedules will be published by the Controller of Examinations. Students must carry valid ID cards. Any form of malpractice will lead to disciplinary action as per the code of conduct.",
        2*cm, y, width - 4*cm)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y-10, "Code of Conduct")
    y -= 26
    c.setFont("Helvetica", 11)
    y = draw_wrapped_text(c,
        "All members of the academic community are expected to maintain decorum, respect diversity, and ensure a safe environment. Grievances can be submitted to the committee for timely resolution.",
        2*cm, y, width - 4*cm)
    c.showPage()

    # Page 3 - Grievance Redressal (optional)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 2*cm, "Grievance Redressal")
    c.setFont("Helvetica", 11)
    y = height - 3*cm
    draw_wrapped_text(c,
        "The institution maintains a transparent grievance redressal mechanism with defined timelines. Students may submit complaints via the portal; anonymized summaries inform continuous improvement.",
        2*cm, y, width - 4*cm)

    c.save()


def gen_naac_pdf(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    # Page 1 - NAAC Overview
    c.setTitle("NAAC Criteria Summary")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "NAAC Criteria Summary - 2024")
    c.setFont("Helvetica", 11)
    y = height - 3*cm
    y = draw_wrapped_text(c,
        "This document provides a concise summary of NAAC criteria with exemplar practices and data points used for accreditation. It is intended for internal review and preparation.",
        2*cm, y, width - 4*cm)

    # Criteria X (placeholder)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y-10, "Criteria X: Curriculum Design and Development")
    y -= 26
    c.setFont("Helvetica", 11)
    y = draw_wrapped_text(c,
        "The institution periodically revises curricula with stakeholder inputs, integrates emerging areas like AI/ML, and emphasizes experiential learning through projects and internships.",
        2*cm, y, width - 4*cm)
    c.showPage()

    # Page 2 - Evidence & Outcomes
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 2*cm, "Evidence and Outcomes")
    c.setFont("Helvetica", 11)
    y = height - 3*cm
    y = draw_wrapped_text(c,
        "Key evidence includes BOS minutes, industry advisory feedback, student performance analytics, and graduate employability metrics. Outcomes reflect continuous quality improvement.",
        2*cm, y, width - 4*cm)

    c.save()


def main():
    gen_policies_pdf(OUTPUT_DIR / "policies.pdf")
    gen_naac_pdf(OUTPUT_DIR / "NAAC_criteria.pdf")
    print("Generated: policies.pdf, NAAC_criteria.pdf in", OUTPUT_DIR)


if __name__ == "__main__":
    main()
