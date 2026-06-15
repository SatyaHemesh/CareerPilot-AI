import os
import json
import google.generativeai as genai

# Configure the API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 2.5 Flash for high-speed text analysis, forcing JSON output
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def _call_gemini_json(prompt):
    """Helper function to call Gemini, strip Markdown, and parse the JSON response."""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Strip markdown code blocks if Gemini accidentally includes them
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {}

def analyze_resume(resume_text, target_role):
    prompt = f"""
    Analyze this resume for a {target_role} role. 
    Return a JSON object with this exact structure:
    {{
        "candidate_name": "String", "email": "String", "phone": "String",
        "overall_impression": "String", "strengths": ["String"], "weaknesses": ["String"],
        "skills": {{"technical": ["String"], "soft": ["String"], "certifications": ["String"]}},
        "projects": [{{"name": "String", "description": "String", "technologies": ["String"]}}]
    }}
    
    Resume Text: {resume_text}
    """
    return _call_gemini_json(prompt)

def calculate_ats_score(resume_text, target_role):
    prompt = f"""
    Calculate the ATS score for this resume against a {target_role} role.
    Return a JSON object with this exact structure:
    {{
        "overall_score": Integer,
        "score_breakdown_explanation": "String",
        "ats_tips": ["String"],
        "keyword_analysis": {{"found_keywords": ["String"], "missing_keywords": ["String"]}},
        "category_scores": {{
            "skills_match": {{"score": Integer, "weight": 25, "weighted_score": Float, "feedback": "String"}},
            "education": {{"score": Integer, "weight": 15, "weighted_score": Float, "feedback": "String"}},
            "projects": {{"score": Integer, "weight": 20, "weighted_score": Float, "feedback": "String"}},
            "experience": {{"score": Integer, "weight": 30, "weighted_score": Float, "feedback": "String"}},
            "formatting": {{"score": Integer, "weight": 10, "weighted_score": Float, "feedback": "String"}}
        }}
    }}
    
    Resume Text: {resume_text}
    """
    return _call_gemini_json(prompt)

def analyze_skill_gap(resume_text, target_role):
    prompt = f"""
    Identify skill gaps for a {target_role} based on this resume.
    Return a JSON object with this exact structure:
    {{
      "target_role": "{target_role}",
      "skill_match_percentage": Integer,
      "roadmap_summary": "String",
      "found_skills": ["String"],
      "missing_critical_skills": [{{"skill": "String", "priority": "HIGH", "reason": "String", "learning_time": "String"}}], 
      "recommended_skills": [{{"skill": "String", "reason": "String"}}]
    }}
    
    Resume Text: {resume_text}
    """
    return _call_gemini_json(prompt)

def generate_interview_questions(resume_text, target_role):
    prompt = f"""
    Generate interview questions for a {target_role} based on this resume.
    Return a JSON object with this exact structure:
    {{
        "easy": [{{"question": "String", "answer": "String", "tips": "String", "category": "String"}}], 
        "medium": [{{"question": "String", "answer": "String", "tips": "String", "category": "String"}}], 
        "hard": [{{"question": "String", "answer": "String", "tips": "String", "category": "String"}}]
    }}
    
    Resume Text: {resume_text}
    """
    return _call_gemini_json(prompt)

def generate_learning_roadmap(skill_gap_data, target_role):
    prompt = f"""
    Create a 30-60-90 day learning roadmap for a {target_role} based on these missing skills: {json.dumps(skill_gap_data)}.
    Return a JSON object with this exact structure:
    {{
        "30_day_plan": {{"goal": "String", "daily_commitment": "String", "weeks": [{{"week": Integer, "focus": "String", "milestone": "String", "daily_tasks": ["String"], "topics": ["String"]}}]}},
        "60_day_plan": {{"goal": "String", "daily_commitment": "String", "weeks": [{{"week": Integer, "focus": "String", "milestone": "String", "daily_tasks": ["String"], "topics": ["String"]}}]}},
        "90_day_plan": {{"goal": "String", "daily_commitment": "String", "weeks": [{{"week": Integer, "focus": "String", "milestone": "String", "daily_tasks": ["String"], "topics": ["String"]}}]}}
    }}
    """
    return _call_gemini_json(prompt)

def generate_recommendations(analysis_data, ats_data, skill_gap_data):
    prompt = f"""
    Provide actionable resume recommendations based on this data:
    Analysis: {json.dumps(analysis_data)}
    ATS: {json.dumps(ats_data)}
    Gaps: {json.dumps(skill_gap_data)}
    
    Return a JSON object with this exact structure:
    {{
        "career_advice": "A short, encouraging paragraph providing overarching career advice based on the analysis.",
        "quick_wins": ["String"],
        "portfolio_suggestions": ["String"],
        "resume_improvements": ["String"],
        "priority_actions": [{{"impact": "HIGH", "action": "String", "timeframe": "String", "details": "String"}}]
    }}
    """
    return _call_gemini_json(prompt)