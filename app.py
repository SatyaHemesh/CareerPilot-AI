import os
from flask import Flask, render_template, session, redirect, url_for
from dotenv import load_dotenv
from utils.database import init_db, get_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'careerpilot-dev-secret-key-change-in-prod')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Register Blueprints
from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.analysis_routes import analysis_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(admin_bp)


# Main blueprint routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as count FROM resumes WHERE user_id = ?", (user_id,))
    resume_count = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM analysis_reports WHERE user_id = ?", (user_id,))
    report_count = c.fetchone()['count']
    
    c.execute("SELECT AVG(ats_score) as avg FROM analysis_reports WHERE user_id = ?", (user_id,))
    avg_row = c.fetchone()
    avg_score = round(avg_row['avg'] or 0, 1)
    
    c.execute("""
        SELECT ar.*, r.original_filename
        FROM analysis_reports ar
        JOIN resumes r ON ar.resume_id = r.id
        WHERE ar.user_id = ?
        ORDER BY ar.created_at DESC
        LIMIT 5
    """, (user_id,))
    recent_reports = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY upload_date DESC LIMIT 3", (user_id,))
    recent_resumes = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return render_template('dashboard.html',
        resume_count=resume_count,
        report_count=report_count,
        avg_score=avg_score,
        recent_reports=recent_reports,
        recent_resumes=recent_resumes,
    )


# Add route alias to main blueprint
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/home')
def home():
    return redirect(url_for('index'))

@main_bp.route('/dash')
def dashboard_alias():
    return redirect(url_for('dashboard'))

app.register_blueprint(main_bp)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(413)
def too_large(e):
    return render_template('error.html', message="File is too large. Maximum size is 16MB."), 413


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="An internal error occurred."), 500


if __name__ == '__main__':
    init_db()
    
    # Create required directories
    for folder in ['uploads', 'reports', 'database']:
        os.makedirs(folder, exist_ok=True)
    
    print("🚀 CareerPilot AI is starting...")
    print("🌐 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
