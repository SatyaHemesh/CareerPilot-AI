import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    KeepTogether, ListFlowable, ListItem, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Shared Helpers
def safe_dict(data): return data if isinstance(data, dict) else {}
def safe_list(data): return data if isinstance(data, list) else []

def get_score_label(score):
    try:
        s = int(score)
        if s >= 80: return "Excellent"
        if s >= 60: return "Good"
        if s >= 40: return "Fair"
        return "Needs Work"
    except: return "Evaluated"

# ==========================================
# MASTER ROUTER
# ==========================================
def generate_pdf_report(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name="Candidate", template_style="modern"):
    """Routes the generation to the selected template style."""
    if template_style == "minimalist":
        return _build_minimalist_pdf(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name)
    elif template_style == "corporate":
        return _build_corporate_pdf(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name)
    else:
        return _build_modern_pdf(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name)


# ==========================================
# 1. MODERN CARDS TEMPLATE (Your current favorite)
# ==========================================
def _build_modern_pdf(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name):
    COLOR_PRIMARY = HexColor('#2563EB')    
    COLOR_DARK = HexColor('#0F172A')       
    COLOR_TEXT = HexColor('#334155')       
    COLOR_MUTED = HexColor('#64748B')      
    COLOR_SUCCESS = HexColor('#10B981')    
    COLOR_WARNING = HexColor('#F59E0B')    
    COLOR_DANGER = HexColor('#EF4444')     
    COLOR_BG_LIGHT = HexColor('#F8FAFC')   
    
    def get_color(s):
        try:
            val = int(s)
            return COLOR_SUCCESS if val >= 75 else (COLOR_WARNING if val >= 50 else COLOR_DANGER)
        except: return COLOR_PRIMARY

    def create_card(content):
        tbl = Table([[content]], colWidths=[17*cm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
            ('PADDING', (0,0), (-1,-1), 12),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12)
        ]))
        return KeepTogether(tbl)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=20, textColor=COLOR_DARK, fontName='Helvetica-Bold', spaceBefore=20, spaceAfter=15)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=COLOR_PRIMARY, fontName='Helvetica-Bold', spaceBefore=15, spaceAfter=8)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10.5, textColor=COLOR_TEXT, leading=16, spaceAfter=10)
    body_bold = ParagraphStyle('BodyB', parent=styles['Normal'], fontSize=10.5, textColor=COLOR_DARK, leading=16, spaceAfter=6, fontName='Helvetica-Bold')
    
    analysis, ats, gaps = safe_dict(analysis_data), safe_dict(ats_data), safe_dict(skill_gap_data)
    story = []

    # Cover
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("<b>CareerPilot AI</b>", ParagraphStyle('CT', fontSize=40, textColor=COLOR_PRIMARY, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.5*inch))
    score = ats.get('overall_score', 0)
    cover_card = f"""
    <font size="14"><b>Candidate:</b> {candidate_name}</font><br/><br/>
    <font size="14"><b>Target Role:</b> {gaps.get('target_role', 'Not Specified')}</font><br/><br/>
    <font size="14"><b>Overall ATS Match Score</b></font><br/>
    <font size="48" color="{get_color(score).hexval()}"><b>{score}</b></font><font size="18" color="{COLOR_MUTED.hexval()}">/100</font>
    """
    story.append(create_card(Paragraph(cover_card, ParagraphStyle('CC', alignment=TA_CENTER, leading=22))))
    story.append(PageBreak())

    # Summary
    story.append(Paragraph("1. Executive Summary", h1))
    story.append(Paragraph(analysis.get('overall_impression', ''), body))
    skills = safe_dict(analysis.get('skills', {}))
    if skills.get('technical'):
        story.append(Paragraph("<b>Technical Arsenal</b>", h2))
        story.append(create_card(Paragraph(", ".join(safe_list(skills.get('technical'))), body)))
    
    # Missing Skills
    story.append(Paragraph("2. Skill Gaps", h1))
    missing = safe_list(gaps.get('missing_critical_skills', []))
    for m in missing:
        if isinstance(m, dict):
            pri = str(m.get('priority', 'MEDIUM')).upper()
            c_hex = COLOR_DANGER.hexval() if pri == 'HIGH' else COLOR_WARNING.hexval()
            story.append(create_card([
                Paragraph(f"<b>{m.get('skill', '')}</b> [<font color='{c_hex}'>{pri}</font>]", body_bold),
                Paragraph(m.get('reason', ''), body)
            ]))
            story.append(Spacer(1, 0.1*inch))
            
    doc.build(story)
    return output_path


# ==========================================
# 2. CORPORATE TEMPLATE (Professional, Serif)
# ==========================================
def _build_corporate_pdf(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name):
    CORP_BLUE = HexColor('#0f2b4a')
    CORP_TEXT = HexColor('#212529')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, textColor=CORP_BLUE, fontName='Times-Bold', spaceBefore=20, spaceAfter=10)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, textColor=CORP_TEXT, fontName='Times-Roman', leading=15, spaceAfter=8)
    
    analysis, ats, gaps = safe_dict(analysis_data), safe_dict(ats_data), safe_dict(skill_gap_data)
    story = []

    # Clean Header
    story.append(Paragraph(f"<b>CANDIDATE ANALYSIS REPORT:</b> {candidate_name.upper()}", h1))
    story.append(HRFlowable(width="100%", thickness=2, color=CORP_BLUE, spaceAfter=15))
    story.append(Paragraph(f"<b>Role Evaluated:</b> {gaps.get('target_role', 'Professional')}", body))
    story.append(Paragraph(f"<b>System ATS Score:</b> {ats.get('overall_score', 0)}/100", body))
    story.append(Spacer(1, 0.5*inch))
    
    # Content
    story.append(Paragraph("<b>1. PROFILE SUMMARY</b>", h1))
    story.append(Paragraph(analysis.get('overall_impression', ''), body))
    
    missing = safe_list(gaps.get('missing_critical_skills', []))
    if missing:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>2. CRITICAL SKILL DEFICIENCIES</b>", h1))
        for m in missing:
            if isinstance(m, dict):
                story.append(Paragraph(f"• <b>{m.get('skill', '')}</b>: {m.get('reason', '')}", body))

    doc.build(story)
    return output_path


# ==========================================
# 3. MINIMALIST TEMPLATE (Ink Saver)
# ==========================================
def _build_minimalist_pdf(analysis_data, ats_data, skill_gap_data, interview_data, roadmap_data, recommendations_data, output_path, candidate_name):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=14, textColor=black, fontName='Helvetica-Bold', spaceBefore=15, spaceAfter=8)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=black, fontName='Helvetica', leading=14, spaceAfter=6)
    
    analysis, ats, gaps = safe_dict(analysis_data), safe_dict(ats_data), safe_dict(skill_gap_data)
    story = []

    story.append(Paragraph(f"{candidate_name} - AI Resume Analysis", h1))
    story.append(Paragraph(f"Target Role: {gaps.get('target_role', '')} | ATS Score: {ats.get('overall_score', 0)}/100", body))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("EXECUTIVE SUMMARY", h1))
    story.append(Paragraph(analysis.get('overall_impression', ''), body))
    
    missing = safe_list(gaps.get('missing_critical_skills', []))
    if missing:
        story.append(Paragraph("SKILL GAPS", h1))
        for m in missing:
            if isinstance(m, dict):
                story.append(Paragraph(f"- {m.get('skill', '')}: {m.get('reason', '')}", body))

    doc.build(story)
    return output_path