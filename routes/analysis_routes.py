import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from utils.database import get_db
from utils.helpers import safe_json_loads, get_report_path
from utils.resume_parser import extract_resume_text, basic_parse_resume
from utils.gemini_service import (
    analyze_resume, calculate_ats_score, analyze_skill_gap,
    generate_interview_questions, generate_learning_roadmap, generate_recommendations
)

from utils.report_generator import generate_pdf_report

analysis_bp = Blueprint('analysis', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@analysis_bp.route('/analyze/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def analyze(resume_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE id = ? AND user_id = ?", (resume_id, session['user_id']))
    resume = c.fetchone()
    conn.close()
    
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.my_resumes'))
    
    target_role = request.form.get('target_role', 'Full Stack Developer') if request.method == 'POST' else 'Full Stack Developer'
    
    if request.method == 'POST':
        return redirect(url_for('analysis.run_analysis', resume_id=resume_id, target_role=target_role))
    
    return render_template('analysis_setup.html', resume=dict(resume))


@analysis_bp.route('/run-analysis/<int:resume_id>')
@login_required
def run_analysis(resume_id):
    target_role = request.args.get('target_role', 'Full Stack Developer')
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE id = ? AND user_id = ?", (resume_id, session['user_id']))
    resume = c.fetchone()
    
    if not resume:
        flash('Resume not found.', 'danger')
        conn.close()
        return redirect(url_for('resume.my_resumes'))
    
    try:
        # Extract text
        resume_text = extract_resume_text(resume['file_path'])
        if not resume_text or len(resume_text) < 50:
            flash('Could not extract text from resume. Please ensure the file is not corrupted.', 'danger')
            conn.close()
            return redirect(url_for('resume.my_resumes'))
        
        # Run all AI analyses
        analysis_data = analyze_resume(resume_text, target_role)
        ats_data = calculate_ats_score(resume_text, target_role)
        skill_gap_data = analyze_skill_gap(resume_text, target_role)
        interview_data = generate_interview_questions(resume_text, target_role)
        roadmap_data = generate_learning_roadmap(skill_gap_data, target_role)
        recommendations_data = generate_recommendations(analysis_data, ats_data, skill_gap_data)
        
        ats_score = ats_data.get('overall_score', 0)
        cat = ats_data.get('category_scores', {})
        
        # Save to DB
        c.execute("""
            INSERT INTO analysis_reports 
            (user_id, resume_id, target_role, ats_score, skills_score, education_score,
             projects_score, experience_score, formatting_score,
             extracted_skills, missing_skills, recommendations, raw_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session['user_id'], resume_id, target_role, ats_score,
            cat.get('skills_match', {}).get('score', 0),
            cat.get('education', {}).get('score', 0),
            cat.get('projects', {}).get('score', 0),
            cat.get('experience', {}).get('score', 0),
            cat.get('formatting', {}).get('score', 0),
            json.dumps(analysis_data.get('skills', {})),
            json.dumps(skill_gap_data.get('missing_critical_skills', [])),
            json.dumps(recommendations_data),
            json.dumps({
                'analysis': analysis_data,
                'ats': ats_data,
                'skill_gap': skill_gap_data,
                'interview': interview_data,
                'roadmap': roadmap_data,
                'recommendations': recommendations_data
            })
        ))
        conn.commit()
        report_id = c.lastrowid
        
        # Save interview questions
        for level in ['easy', 'medium', 'hard']:
            for q in interview_data.get(level, []):
                c.execute("""
                    INSERT INTO interview_questions 
                    (report_id, user_id, question, answer, explanation, tips, difficulty, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id, session['user_id'],
                    q.get('question', ''), q.get('answer', ''),
                    q.get('explanation', ''), q.get('tips', ''),
                    level, q.get('category', 'General')
                ))
        
        # Save roadmap
        c.execute("""
            INSERT INTO roadmaps (report_id, user_id, plan_type, roadmap_data)
            VALUES (?, ?, ?, ?)
        """, (report_id, session['user_id'], '30_60_90', json.dumps(roadmap_data)))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('analysis.view_report', report_id=report_id))
    
    except Exception as e:
        conn.close()
        flash(f'Analysis failed: {str(e)}. Please check your API key.', 'danger')
        return redirect(url_for('resume.my_resumes'))


@analysis_bp.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT ar.*, r.original_filename 
        FROM analysis_reports ar
        JOIN resumes r ON ar.resume_id = r.id
        WHERE ar.id = ? AND ar.user_id = ?
    """, (report_id, session['user_id']))
    report = c.fetchone()
    
    if not report:
        flash('Report not found.', 'danger')
        conn.close()
        return redirect(url_for('main.dashboard'))
    
    report = dict(report)
    raw = safe_json_loads(report.get('raw_analysis', '{}'))
    conn.close()
    
    return render_template('report.html',
        report=report,
        analysis_data=raw.get('analysis', {}),
        ats_data=raw.get('ats', {}),
        skill_gap_data=raw.get('skill_gap', {}),
        interview_data=raw.get('interview', {}),
        roadmap_data=raw.get('roadmap', {}),
        recommendations_data=raw.get('recommendations', {}),
    )


@analysis_bp.route('/download-report/<int:report_id>')
@login_required
def download_report(report_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM analysis_reports WHERE id = ? AND user_id = ?", (report_id, session['user_id']))
    report = c.fetchone()
    conn.close()
    
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    raw = safe_json_loads(report['raw_analysis'] or '{}')
    output_path = get_report_path(session['user_id'], report_id)
    
    candidate_name = raw.get('analysis', {}).get('candidate_name', session.get('username', 'Candidate'))
    
    # Capture the template style from the frontend dropdown (default to modern)
    style_choice = request.args.get('template_style', 'modern')
    
    # Pass the style_choice to the generator
    generate_pdf_report(
        analysis_data=raw.get('analysis', {}),
        ats_data=raw.get('ats', {}),
        skill_gap_data=raw.get('skill_gap', {}),
        interview_data=raw.get('interview', {}),
        roadmap_data=raw.get('roadmap', {}),
        recommendations_data=raw.get('recommendations', {}),
        output_path=output_path,
        candidate_name=candidate_name,
        template_style=style_choice
    )
    
    # as_attachment=False opens the PDF in a new tab for preview!
    return send_file(output_path, as_attachment=False, mimetype='application/pdf')


@analysis_bp.route('/my-reports')
@login_required
def my_reports():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT ar.*, r.original_filename
        FROM analysis_reports ar
        JOIN resumes r ON ar.resume_id = r.id
        WHERE ar.user_id = ?
        ORDER BY ar.created_at DESC
    """, (session['user_id'],))
    reports = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('my_reports.html', reports=reports)
