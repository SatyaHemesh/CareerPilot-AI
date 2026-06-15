import json
from flask import Blueprint, render_template, session, redirect, url_for, flash
from utils.database import get_db
from utils.helpers import safe_json_loads

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
@admin_required
def dashboard():
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as count FROM users")
    user_count = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM resumes")
    resume_count = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM analysis_reports")
    report_count = c.fetchone()['count']
    
    c.execute("SELECT AVG(ats_score) as avg FROM analysis_reports")
    avg_score_row = c.fetchone()
    avg_score = round(avg_score_row['avg'] or 0, 1)
    
    c.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 10")
    recent_users = [dict(row) for row in c.fetchall()]
    
    c.execute("""
        SELECT ar.*, u.username, r.original_filename
        FROM analysis_reports ar
        JOIN users u ON ar.user_id = u.id
        JOIN resumes r ON ar.resume_id = r.id
        ORDER BY ar.created_at DESC LIMIT 10
    """)
    recent_reports = [dict(row) for row in c.fetchall()]
    
    # Aggregate missing skills
    c.execute("SELECT missing_skills FROM analysis_reports WHERE missing_skills IS NOT NULL")
    all_missing = {}
    for row in c.fetchall():
        missing = safe_json_loads(row['missing_skills'], [])
        for skill in missing:
            name = skill.get('skill', '') if isinstance(skill, dict) else str(skill)
            if name:
                all_missing[name] = all_missing.get(name, 0) + 1
    top_missing = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # ATS score distribution
    c.execute("""
        SELECT 
            COUNT(CASE WHEN ats_score >= 80 THEN 1 END) as excellent,
            COUNT(CASE WHEN ats_score >= 60 AND ats_score < 80 THEN 1 END) as good,
            COUNT(CASE WHEN ats_score >= 40 AND ats_score < 60 THEN 1 END) as fair,
            COUNT(CASE WHEN ats_score < 40 THEN 1 END) as poor
        FROM analysis_reports
    """)
    score_dist = dict(c.fetchone())
    
    c.execute("SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT 20")
    logs = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return render_template('admin.html',
        user_count=user_count,
        resume_count=resume_count,
        report_count=report_count,
        avg_score=avg_score,
        recent_users=recent_users,
        recent_reports=recent_reports,
        top_missing=top_missing,
        score_dist=score_dist,
        logs=logs,
    )
