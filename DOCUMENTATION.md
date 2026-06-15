# CareerPilot AI – Project Documentation

## Abstract

CareerPilot AI is a web-based AI-powered career development platform that analyzes resumes using advanced natural language processing. Users upload their resume and receive an ATS compatibility score, personalized skill gap analysis, AI-generated interview questions with model answers, a 30/60/90-day learning roadmap, and a downloadable PDF report — all powered by Anthropic's Claude AI.

---

## 1. Introduction

Modern job markets require candidates to optimize their resumes for ATS (Applicant Tracking Systems) before they reach human reviewers. Studies show that over 75% of resumes are rejected by ATS before a recruiter sees them. CareerPilot AI addresses this by providing instant, AI-driven feedback to help candidates improve their chances of landing interviews.

---

## 2. Problem Statement

Job seekers face three critical challenges:
1. **ATS Rejection** – Resumes are not optimized for keyword-based screening systems
2. **Skill Gaps** – Candidates don't know which skills to learn for their target role
3. **Interview Unpreparedness** – Lack of targeted practice questions based on their actual experience

---

## 3. Objectives

- Build a full-stack web application for resume analysis
- Integrate Claude AI for deep NLP-based resume parsing and feedback
- Provide an ATS scoring algorithm with weighted category scores
- Generate personalized 90-day learning roadmaps
- Produce downloadable PDF reports for job applications
- Implement a secure user authentication system
- Create an admin dashboard for platform analytics

---

## 4. Scope

**In Scope:**
- PDF and DOCX resume upload and parsing
- ATS scoring across 5 weighted categories
- Skill gap analysis for 6 career paths
- Interview question generation (Easy/Medium/Hard)
- 30/60/90-day roadmap generation
- PDF report download
- User registration, login, session management
- Admin dashboard with statistics

**Out of Scope:**
- Resume auto-editing / rewriting
- Direct job board integration
- Video mock interviews
- Payment / subscription management

---

## 5. System Design

### 5.1 Architecture

```
User Browser (HTML/CSS/JS)
        │
        │ HTTP/HTTPS
        ▼
Flask Web Server (app.py)
        │
   ┌────┴────────────────────┐
   │                         │
SQLite DB            Anthropic Claude API
(database.py)        (claude_service.py)
   │                         │
   │                    AI Analysis
Resumes/Reports         Results (JSON)
  (filesystem)               │
                       ReportLab PDF
                      (report_generator.py)
```

### 5.2 Database ER Diagram

```
users ──────────── resumes ──────────── analysis_reports
  │                   │                        │
  │                   │              ┌──────────┴──────────┐
  │                   │              │                     │
  │             (file stored   interview_questions      roadmaps
  │              in /uploads)
  │
admin_logs
```

### 5.3 Flow Diagram

```
[User] → Register/Login → Dashboard
           │
           ▼
        Upload Resume (PDF/DOCX)
           │
           ▼
        Choose Target Role
           │
           ▼
     ┌─────────────────────┐
     │    Claude AI Engine  │
     │  ┌────────────────┐  │
     │  │ Resume Analysis│  │
     │  │ ATS Scoring    │  │
     │  │ Skill Gap      │  │
     │  │ Interview Q's  │  │
     │  │ Roadmap Gen    │  │
     │  │ Recommendations│  │
     │  └────────────────┘  │
     └─────────────────────┘
           │
           ▼
     View Report (Tabbed UI)
           │
           ▼
     Download PDF Report
```

---

## 6. Modules Description

### Module 1: Authentication
- **Registration**: Username, email, full name, password (hashed via PBKDF2-SHA256)
- **Login**: Email + password verification, session creation
- **Session**: Flask server-side sessions with signed cookies
- **Security**: Password hashing, CSRF-protected forms

### Module 2: Resume Upload
- Accepts PDF (.pdf) and Word (.docx, .doc)
- Drag-and-drop upload interface
- File validation (type, size ≤ 16MB)
- Unique filename via UUID to prevent conflicts
- Stored in `/uploads/` directory

### Module 3: Resume Parser
- **PDF**: pdfplumber (primary) → PyPDF2 (fallback)
- **DOCX**: python-docx paragraph extraction
- **Local Parse**: Regex for email, phone, LinkedIn, GitHub; keyword scan for 100+ known skills
- **Deep Parse**: Claude AI extracts structured JSON (education, experience, projects, skills)

### Module 4: ATS Score Calculator
Claude evaluates the resume against the target role and scores:

| Category | Weight | What's Measured |
|----------|--------|-----------------|
| Skills Match | 40% | Technical skill alignment with role requirements |
| Education | 20% | Degree relevance, institution, certifications |
| Projects | 15% | Quantity, relevance, technical depth |
| Experience | 15% | Duration, seniority, achievements |
| Formatting | 10% | ATS readability, structure, keyword density |

### Module 5: Skill Gap Analyzer
- Extracts current skills from resume
- Compares against role-specific required skills (6 roles)
- Returns: found skills, missing critical skills (HIGH/MEDIUM/LOW priority), recommended skills
- Each missing skill includes: reason + estimated learning time

### Module 6: Interview Coach
- Generates 12 questions (4 Easy, 4 Medium, 4 Hard)
- Categories: Behavioral, Technical, HR, System Design
- Each question includes: model answer, explanation, tips
- Personalized based on actual resume content

### Module 7: Learning Roadmap
- 30-Day Plan: weeks 1–4 with topics, resources, milestones, daily tasks
- 60-Day Plan: weeks 5–8
- 90-Day Plan: weeks 9–12
- Key portfolio projects to build
- Success metrics

### Module 8: PDF Report Generator
Uses ReportLab to produce a multi-page professional PDF:
- Cover page with ATS score
- Resume analysis section
- ATS score table with category breakdown
- Skill gap analysis with color-coded priority
- Top interview questions with answers
- 30-day learning roadmap
- AI recommendations

### Module 9: Admin Dashboard
- Total users, resumes, reports counts
- Average ATS score
- ATS score distribution (doughnut chart via Chart.js)
- Most common missing skills leaderboard
- Recent users and reports table
- Admin activity logs

---

## 7. Implementation Details

### 7.1 Claude API Integration

```python
# claude_service.py – Example prompt structure
prompt = f"""You are an ATS expert. Evaluate this resume for a {target_role}.

RESUME: {resume_text[:4000]}

Return ONLY valid JSON:
{{
    "overall_score": 78,
    "category_scores": {{ ... }},
    "ats_tips": [...]
}}"""

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1500,
    messages=[{"role": "user", "content": prompt}]
)
```

### 7.2 Security Implementation
- Passwords: `werkzeug.security.generate_password_hash()` (PBKDF2-SHA256 + salt)
- Sessions: Flask signed cookies with `SECRET_KEY`
- File uploads: `werkzeug.utils.secure_filename()` + UUID renaming
- Route protection: `login_required` decorator on all authenticated routes

---

## 8. Testing

### Black Box Testing

| Test Case | Input | Expected Output | Status |
|-----------|-------|-----------------|--------|
| TC01 | Valid PDF upload | Success message + redirect to analysis | ✅ |
| TC02 | Invalid file (.txt) | "Invalid file type" error | ✅ |
| TC03 | Register with existing email | "Email already exists" error | ✅ |
| TC04 | Wrong password login | "Invalid email or password" | ✅ |
| TC05 | Access dashboard without login | Redirect to login | ✅ |
| TC06 | Access admin as regular user | "Admin access required" error | ✅ |
| TC07 | Upload file >16MB | "File too large" error | ✅ |
| TC08 | Run analysis with API key | Full report generated | ✅ |
| TC09 | Download PDF report | PDF file downloaded | ✅ |
| TC10 | Delete resume | Removed from DB and filesystem | ✅ |

### White Box Testing

| Module | Test | Coverage |
|--------|------|----------|
| auth.py | `register_user()` duplicate check | DB uniqueness constraint |
| auth.py | `login_user()` password verify | `check_password_hash()` |
| resume_parser.py | `parse_email()` | Regex pattern matching |
| resume_parser.py | `extract_skills_from_text()` | Skill list membership |
| helpers.py | `allowed_file()` | Extension set check |
| claude_service.py | JSON parse fallback | Try/except on malformed JSON |

---

## 9. Results

Sample analysis output for a mid-level developer resume targeting Full Stack Developer:
- **ATS Score**: 72/100
- **Skills Match**: 75% (missing TypeScript, Jest, Kubernetes)
- **Skill Match Percentage**: 65%
- **Interview Questions Generated**: 12 (4 per level)
- **Roadmap**: 12-week structured plan with 48 daily tasks
- **PDF Report Size**: ~11KB (fast to generate and download)

---

## 10. Advantages

1. **Speed**: Full analysis in 30–60 seconds vs days of manual research
2. **Personalization**: Every output is unique to the user's resume content
3. **Comprehensive**: 6 modules cover the entire job search journey
4. **Actionable**: Specific skills with learning time estimates and resources
5. **Professional Output**: Downloadable PDF suitable for sharing with mentors
6. **Multi-Role Support**: 6 different career path analyses available
7. **ATS-Aware**: Scoring mirrors real ATS logic (keyword density, formatting)

---

## 11. Limitations

1. **API Dependency**: Requires Anthropic API key (costs money at scale)
2. **Language**: English resumes only (Claude handles other languages but prompts are English)
3. **File Size**: Very long resumes (>10 pages) may lose context after 4000-char truncation
4. **No Real-Time Job Matching**: Does not compare against live job postings
5. **SQLite**: Not suitable for high-concurrency production (would need PostgreSQL)
6. **File Storage**: Files stored locally (would need S3 for production deployment)

---

## 12. Future Enhancements

1. **Job Description Matching**: Paste any JD → instant % match score
2. **LinkedIn Import**: Auto-fetch profile via LinkedIn API
3. **Resume Rewriter**: AI-powered resume improvement suggestions
4. **Mock Interview**: Video recording + AI body language analysis
5. **Multi-language**: Support resumes in Hindi, Telugu, etc.
6. **Email Alerts**: Scheduled weekly tips based on roadmap progress
7. **Team/Company Features**: Bulk analysis for recruiters
8. **Real PostgreSQL + S3**: Production-ready infrastructure
9. **Resume Versioning**: Compare v1 vs v2 score improvement

---

## 13. Conclusion

CareerPilot AI successfully demonstrates the power of combining Claude AI with a full-stack web application to solve real career challenges. The system provides end-to-end support from resume optimization through interview preparation, backed by AI-generated insights that would take hours to compile manually. The project showcases MERN-adjacent Python/Flask skills, REST API integration, database design, PDF generation, and modern UI/UX — making it an ideal portfolio piece for full-stack development roles.

---

## 14. References

1. Anthropic Claude API Documentation – https://docs.anthropic.com
2. Flask Documentation – https://flask.palletsprojects.com
3. ReportLab User Guide – https://www.reportlab.com/docs/
4. pdfplumber GitHub – https://github.com/jsvine/pdfplumber
5. Bootstrap 5 Docs – https://getbootstrap.com/docs/5.3
6. Werkzeug Security – https://werkzeug.palletsprojects.com/en/latest/utils/
7. SQLite Documentation – https://www.sqlite.org/docs.html
8. Chart.js Documentation – https://www.chartjs.org/docs/
