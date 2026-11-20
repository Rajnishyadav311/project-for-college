"""
MediPredict AI — Medical Laboratory Report Summary PDF Generator.
Uses ReportLab to create professional, branded healthcare summaries
with patient demographics, test results, clinical status badges, and disclaimers.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_report_pdf(report):
    """
    Builds a professional medical report PDF in-memory and returns bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom color palette (Healthcare Navy & Cyan)
    primary_color = colors.HexColor('#0f2b48')
    accent_color = colors.HexColor('#00a8cc')
    text_dark = colors.HexColor('#1e293b')
    gray_bg = colors.HexColor('#f8fafc')
    border_color = colors.HexColor('#e2e8f0')

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=accent_color
    )

    heading2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )

    elements = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>MediPredict AI</b>", title_style),
            Paragraph(f"<b>Report Date:</b> {report.report_date.strftime('%d-%b-%Y')}<br/><b>Generated:</b> {datetime.now().strftime('%d-%b-%Y %H:%M')}", body_style)
        ],
        [
            Paragraph("Intelligent Clinical Laboratory Analysis Summary", subtitle_style),
            Paragraph(f"<b>Patient:</b> {report.user.get_full_name() or report.user.username}", body_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.2 * inch, 3.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=12, spaceBefore=4))

    # 2. Patient & Report Overview Box
    user = report.user
    gender = getattr(user, 'gender', 'Not Specified')
    dob = getattr(user, 'date_of_birth', None)
    age_str = f"{(datetime.now().date() - dob).days // 365} Yrs" if dob else "N/A"

    overview_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {user.get_full_name() or user.username}", body_style),
            Paragraph(f"<b>Age / Sex:</b> {age_str} / {gender}", body_style),
            Paragraph(f"<b>Report ID:</b> #MP-{report.id:05d}", body_style),
        ],
        [
            Paragraph(f"<b>Category:</b> {report.get_report_category_display()}", body_style),
            Paragraph(f"<b>Total Tests:</b> {report.total_tests_count}", body_style),
            Paragraph(f"<b>Attention Needed:</b> <font color='#ef4444'><b>{report.abnormal_tests_count}</b></font>", body_style),
        ]
    ]
    overview_table = Table(overview_data, colWidths=[2.6 * inch, 2.4 * inch, 2.2 * inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), gray_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 14))

    # 3. Lab Parameters Table
    elements.append(Paragraph("<b>LABORATORY TEST RESULTS & CLINICAL EVALUATION</b>", heading2_style))
    elements.append(Spacer(1, 6))

    table_headers = ["Test Name", "Result", "Unit", "Biological Reference", "Status", "Clinical Significance"]
    data_rows = [table_headers]

    for param in report.parameters.all():
        # Status text styling
        status_color = '#10b981' # Normal
        if param.status == 'low':
            status_color = '#3b82f6' # Blue
        elif param.status == 'high':
            status_color = '#ef4444' # Red
        elif param.status == 'context_needed':
            status_color = '#f59e0b' # Amber

        status_display = param.get_status_display()
        status_cell = Paragraph(f"<font color='{status_color}'><b>{status_display}</b></font>", body_style)

        ref_str = f"{param.reference_min} - {param.reference_max}" if (param.reference_min is not None and param.reference_max is not None) else (param.reference_text or "Method dependent")
        val_str = f"{param.measured_value}" if param.measured_value is not None else (param.raw_value_str or "Recorded")

        data_rows.append([
            Paragraph(f"<b>{param.test_name}</b>", body_style),
            Paragraph(val_str, body_style),
            Paragraph(param.unit or "", body_style),
            Paragraph(ref_str, body_style),
            status_cell,
            Paragraph(param.explanation_en or "", body_style),
        ])

    results_table = Table(
        data_rows,
        colWidths=[1.6 * inch, 0.7 * inch, 0.7 * inch, 1.2 * inch, 1.1 * inch, 1.9 * inch],
        repeatRows=1
    )
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, gray_bg]),
        ('PADDING', (0,1), (-1,-1), 5),
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 14))

    # 4. Summary & Hindi Insight Notes
    elements.append(Paragraph("<b>Bilingual Diagnostic Notes / नैदानिक टिप्पणी</b>", heading2_style))
    elements.append(Spacer(1, 4))

    notes = []
    for param in report.parameters.filter(status__in=['low', 'high'])[:4]:
        notes.append(f"• <b>{param.test_name}:</b> {param.explanation_en}")
        if param.explanation_hi:
            notes.append(f"  <i>{param.explanation_hi}</i>")

    if not notes:
        notes.append("• All recorded biomarkers fall within standard reference intervals. Maintain a balanced diet and routine activity.")
        notes.append("  <i>सभी जाँच मान सामान्य सीमा में हैं। स्वस्थ जीवनशैली बनाए रखें।</i>")

    notes_text = "<br/>".join(notes)
    notes_box = Table([[Paragraph(notes_text, body_style)]], colWidths=[7.2 * inch])
    notes_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(notes_box)
    elements.append(Spacer(1, 14))

    # 5. Mandatory Medical Disclaimer
    disclaimer_html = (
        "<b>CLINICAL DISCLAIMER:</b> MediPredict AI produces analytical summaries based on user-provided "
        "laboratory values and standard clinical reference intervals. This summary is intended solely for personal health "
        "literacy and informational screening. It is <u>not</u> a formal medical diagnosis or clinical consultation. "
        "Never alter, initiate, or discontinue prescribed medications or therapies without direct evaluation from a licensed physician."
    )
    elements.append(Paragraph(disclaimer_html, disclaimer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
