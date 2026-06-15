from werkzeug.security import generate_password_hash, check_password_hash
from utils.database import get_db, log_admin_action
from datetime import datetime


def register_user(username, email, password, full_name=''):
    """Register a new user. Returns (True, user_id) or (False, error_message)."""
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
        if c.fetchone():
            return False, "Username or email already exists."
        
        pw_hash = generate_password_hash(password)
        c.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username, email, pw_hash, full_name)
        )
        conn.commit()
        user_id = c.lastrowid
        log_admin_action('user_registered', user_id, f'New user: {username}')
        return True, user_id
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def login_user(email, password):
    """Authenticate user. Returns (True, user_dict) or (False, error_message)."""
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        if not user:
            return False, "Invalid email or password."
        if not check_password_hash(user['password_hash'], password):
            return False, "Invalid email or password."
        c.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user['id']))
        conn.commit()
        return True, dict(user)
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_email(email):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None
