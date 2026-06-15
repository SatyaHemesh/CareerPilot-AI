# 🚀 CareerPilot AI

> **Analyze. Improve. Succeed.**

An AI-powered Resume Analyzer and Interview Coach built with Flask + Claude AI. Upload your resume and get a complete career analysis in under 60 seconds.

---

## ✨ Features

| Module | What You Get |
|--------|-------------|
| **ATS Score** | Weighted scoring (Skills 40%, Education 20%, Projects 15%, Experience 15%, Formatting 10%) |
| **Resume Analysis** | Deep parsing of skills, education, experience, projects, strengths & weaknesses |
| **Skill Gap Analysis** | Compare against 6 career paths, get prioritized missing skills |
| **Interview Coach** | 12 personalized questions (Easy / Medium / Hard) with answers and tips |
| **Learning Roadmap** | 30/60/90-day week-by-week plan with resources and milestones |
| **AI Recommendations** | Priority actions, quick wins, portfolio suggestions, career advice |
| **PDF Reports** | Downloadable professional report with all analyses |
| **Admin Dashboard** | User stats, score distributions, most-missing skills |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.0
- **AI**: Anthropic Claude API (`claude-sonnet-4-6`)
- **Database**: SQLite (via Python's built-in sqlite3)
- **PDF Parsing**: pdfplumber, PyPDF2
- **PDF Generation**: ReportLab
- **Frontend**: Bootstrap 5, Chart.js, Vanilla JS
- **Auth**: Werkzeug password hashing + Flask sessions

---

## ⚡ Quick Start (2–3 Hours Setup)

### 1. Clone / Extract the Project
```bash
cd CareerPilot-AI
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Edit `.env` file:
```env
ANTHROPIC_API_KEY=your_actual_api_key_here
SECRET_KEY=any_random_secret_string_here
FLASK_ENV=development
```

> Get your Anthropic API key at: https://console.anthropic.com

### 5. Run the App
```bash
python app.py
```

Open **http://localhost:5000** in your browser.

### 6. Create Admin Account
Register normally, then run in Python:
```python
from utils.database import get_db
conn = get_db()
conn.execute("UPDATE users SET is_admin=1 WHERE email='your@email.com'")
conn.commit()
conn.close()
```

---

## 📁 Project Structure

```
CareerPilot-AI/
├── app.py                    # Main Flask app + routes
├── requirements.txt
├── .env                      # Environment variables (add your API key here)
├── README.md
│
├── routes/
│   ├── auth_routes.py        # Login, register, logout
│   ├── resume_routes.py      # Upload, manage resumes
│   ├── analysis_routes.py    # Run analysis, view/download reports
│   └── admin_routes.py       # Admin dashboard
│
├── utils/
│   ├── claude_service.py     # All Claude AI API calls
│   ├── resume_parser.py      # PDF/DOCX text extraction
│   ├── report_generator.py   # ReportLab PDF generation
│   ├── auth.py               # Registration, login logic
│   ├── database.py           # SQLite setup and helpers
│   └── helpers.py            # File utilities
│
├── templates/
│   ├── base.html             # Shared layout + navbar
│   ├── index.html            # Landing page
│   ├── login.html / register.html
│   ├── dashboard.html        # User dashboard
│   ├── upload.html           # Resume upload with drag & drop
│   ├── analysis_setup.html   # Choose target role
│   ├── report.html           # Full analysis report (tabbed)
│   ├── my_reports.html       # Report history
│   ├── my_resumes.html       # Resume management
│   └── admin.html            # Admin dashboard
│
├── static/
│   ├── css/style.css         # Full custom stylesheet
│   └── js/main.js            # Animations, interactivity
│
├── database/
│   └── careerpilot.db        # Auto-created on first run
├── uploads/                  # Uploaded resumes (auto-created)
└── reports/                  # Generated PDF reports (auto-created)
```

---

## 🗄️ Database Schema

```sql
users          (id, username, email, password_hash, full_name, is_admin, created_at, last_login)
resumes        (id, user_id, filename, original_filename, file_path, file_type, file_size, upload_date, parsed_data)
analysis_reports (id, user_id, resume_id, target_role, ats_score, skills_score, education_score,
                  projects_score, experience_score, formatting_score, extracted_skills,
                  missing_skills, recommendations, raw_analysis, pdf_path, created_at)
interview_questions (id, report_id, user_id, question, answer, explanation, tips, difficulty, category, created_at)
roadmaps       (id, report_id, user_id, plan_type, roadmap_data, created_at)
admin_logs     (id, action, user_id, details, ip_address, created_at)
```

---

## 🌐 Deployment

### Render.com (Free)
1. Push to GitHub
2. Create new Web Service on render.com
3. Set environment variables in Render dashboard
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`

### Railway.app
1. Push to GitHub
2. Create project → Deploy from GitHub
3. Add environment variables
4. Deploy automatically

---

## 🎓 Viva Q&A

**Q: What AI model powers CareerPilot AI?**
A: Anthropic's Claude (`claude-sonnet-4-6`) via the Messages API.

**Q: How is the ATS score calculated?**
A: Weighted scoring: Skills Match (40%) + Education (20%) + Projects (15%) + Experience (15%) + Formatting (10%) = 100.

**Q: How are passwords stored?**
A: Using Werkzeug's `generate_password_hash()` with PBKDF2-SHA256. Plain text passwords are never stored.

**Q: What file formats are supported?**
A: PDF (parsed via pdfplumber + PyPDF2) and DOCX (parsed via python-docx).

**Q: How does the skill gap analysis work?**
A: Claude extracts skills from the resume and compares them against a role-specific required skill set, returning missing skills with priority (HIGH/MEDIUM/LOW) and estimated learning time.

**Q: How are PDF reports generated?**
A: Using ReportLab's `SimpleDocTemplate` with custom styles, tables, and color coding.

**Q: What is the session management mechanism?**
A: Flask's server-side sessions stored in signed cookies using the SECRET_KEY.

---

## 📋 Testing

### Manual Test Cases

| Test | Input | Expected Output |
|------|-------|----------------|
| Register with existing email | Duplicate email | "Username or email already exists" |
| Upload invalid file type | .txt file | "Invalid file type" error |
| Upload valid PDF | Valid resume PDF | Redirect to analysis setup |
| Run analysis | PDF + target role | Full report with ATS score |
| Download PDF | Completed report | PDF file download |
| Admin access as non-admin | Admin URL | Redirect with "Admin access required" |
| Empty resume | Blank PDF | "Could not extract text" error |

---

## 🔮 Future Enhancements

- LinkedIn profile import
- Real-time job description comparison (paste JD → instant match %)
- Email report delivery
- Resume version comparison
- Multi-language support
- AI resume rewriting suggestions
- Mock interview video recording

---

## 📄 License

Built for educational and portfolio demonstration purposes.
CareerPilot AI · Powered by Anthropic Claude
