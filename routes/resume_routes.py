import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from utils.helpers import allowed_file, save_uploaded_file, safe_json_loads
from utils.resume_parser import extract_resume_text, basic_parse_resume
from utils.database import get_db

resume_bp = Blueprint('resume', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PDF and DOCX files are allowed.', 'danger')
            return redirect(request.url)
        
        try:
            unique_filename, filepath = save_uploaded_file(file)
            file_size = os.path.getsize(filepath)
            ext = os.path.splitext(file.filename)[1].lower()
            
            conn = get_db()
            c = conn.cursor()
            c.execute("""
                INSERT INTO resumes (user_id, filename, original_filename, file_path, file_type, file_size)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session['user_id'], unique_filename, file.filename, filepath, ext, file_size))
            conn.commit()
            resume_id = c.lastrowid
            conn.close()
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('analysis.analyze', resume_id=resume_id))
        
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html')


@resume_bp.route('/my-resumes')
@login_required
def my_resumes():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT r.*, 
               (SELECT COUNT(*) FROM analysis_reports WHERE resume_id = r.id) as report_count,
               (SELECT ats_score FROM analysis_reports WHERE resume_id = r.id ORDER BY created_at DESC LIMIT 1) as last_score
        FROM resumes r
        WHERE r.user_id = ?
        ORDER BY r.upload_date DESC
    """, (session['user_id'],))
    resumes = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('my_resumes.html', resumes=resumes)


@resume_bp.route('/delete-resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE id = ? AND user_id = ?", (resume_id, session['user_id']))
    resume = c.fetchone()
    if not resume:
        flash('Resume not found.', 'danger')
        conn.close()
        return redirect(url_for('resume.my_resumes'))
    
    try:
        if os.path.exists(resume['file_path']):
            os.remove(resume['file_path'])
    except Exception:
        pass
    
    c.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()
    conn.close()
    flash('Resume deleted.', 'info')
    return redirect(url_for('resume.my_resumes'))
