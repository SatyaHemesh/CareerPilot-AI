import re
import os
import json
import PyPDF2
import pdfplumber
from docx import Document


def extract_text_from_pdf(file_path):
    """Extract text from PDF using pdfplumber (better for tables/columns)."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            text = f"Error extracting PDF: {str(e)}"
    return text.strip()


def extract_text_from_docx(file_path):
    """Extract text from DOCX file."""
    try:
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_resume_text(file_path):
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"


def parse_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def parse_phone(text):
    patterns = [
        r'\+?[\d\s\-\(\)]{10,15}',
        r'\b\d{10}\b',
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0].strip()
    return ""


def parse_linkedin(text):
    pattern = r'linkedin\.com/in/[\w\-]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else ""


def parse_github(text):
    pattern = r'github\.com/[\w\-]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else ""


def extract_skills_from_text(text):
    """Extract known tech skills from resume text."""
    KNOWN_SKILLS = [
        # Programming Languages
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Rust",
        "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB",
        # Web
        "HTML", "CSS", "HTML5", "CSS3", "React", "React.js", "Angular", "Vue", "Vue.js",
        "Node.js", "Express", "Express.js", "Django", "Flask", "FastAPI", "Spring", "Laravel",
        "Next.js", "Nuxt.js", "Svelte", "Bootstrap", "Tailwind", "jQuery",
        # Databases
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Elasticsearch",
        "Oracle", "SQL Server", "DynamoDB", "Cassandra", "Firebase",
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
        "CI/CD", "Terraform", "Ansible", "Git", "GitHub", "GitLab", "Linux", "Bash",
        "Nginx", "Apache", "Heroku", "Vercel", "Netlify", "Railway", "Render",
        # Data & AI
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow",
        "PyTorch", "Keras", "scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn",
        "OpenCV", "NLTK", "spaCy", "Hugging Face", "LangChain", "OpenAI", "Claude",
        # Mobile
        "Android", "iOS", "React Native", "Flutter", "Xamarin",
        # Other
        "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "JIRA",
        "Selenium", "Jest", "PyTest", "Postman", "Figma", "Adobe XD",
        "Blockchain", "Solidity", "Web3",
    ]
    found = []
    text_lower = text.lower()
    for skill in KNOWN_SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)
    return list(dict.fromkeys(found))  # deduplicate preserving order


def basic_parse_resume(text):
    """
    Do a quick local parse of resume text (name, email, phone, skills, etc.)
    Returns a dict. Claude will do the deep analysis.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    name = lines[0] if lines else "Unknown"
    
    return {
        "name": name,
        "email": parse_email(text),
        "phone": parse_phone(text),
        "linkedin": parse_linkedin(text),
        "github": parse_github(text),
        "skills": extract_skills_from_text(text),
        "raw_text": text
    }
