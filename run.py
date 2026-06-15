#!/usr/bin/env python3
"""
CareerPilot AI – Setup & Run Script
Run this once to initialize the database and start the server.
"""

import os
import sys
import subprocess

def check_env():
    print("🔍 Checking environment...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        print("\n⚠️  WARNING: GEMINI_API_KEY not set in .env file!")
        print("   → Get your key at: https://aistudio.google.com/")
        print("   → Edit .env and set: GEMINI_API_KEY=your_key_here")
        print("   → The app will start but AI analysis will fail without a key.\n")
    else:
        print(f"   ✅ API key configured ({api_key[:12]}...)")

def init_database():
    print("🗄️  Initializing database...")
    from utils.database import init_db
    init_db()
    
    # Create default admin
    from utils.auth import register_user, get_user_by_email
    from utils.database import get_db
    
    if not get_user_by_email('admin@careerpilot.ai'):
        ok, _ = register_user('admin', 'admin@careerpilot.ai', 'admin123', 'Admin User')
        if ok:
            conn = get_db()
            conn.execute("UPDATE users SET is_admin=1 WHERE email='admin@careerpilot.ai'")
            conn.commit()
            conn.close()
            print("   ✅ Default admin created: admin@careerpilot.ai / admin123")
    else:
        print("   ✅ Admin user already exists")

def create_dirs():
    print("📁 Creating directories...")
    for d in ['uploads', 'reports', 'database', 'static/css', 'static/js']:
        os.makedirs(d, exist_ok=True)
    print("   ✅ Directories ready")

def run_app():
    print("\n🚀 Starting CareerPilot AI...")
    print("=" * 50)
    print("   URL: http://localhost:5000")
    print("   Admin: admin@careerpilot.ai / admin123")
    print("   Press CTRL+C to stop")
    print("=" * 50 + "\n")
    
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  🚀 CareerPilot AI – Startup")
    print("="*50 + "\n")
    
    create_dirs()
    check_env()
    init_database()
    run_app()
