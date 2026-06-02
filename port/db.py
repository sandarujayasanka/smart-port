"""
db.py  —  PostgreSQL connection helpers for Smart Port App (Supabase)
Requires:  pip install psycopg2-binary bcrypt
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import secrets
from datetime import datetime, timedelta
import streamlit as st

# Supabase Connection String එක (Password එක ඇතුළත් කර ඇත)
DB_URI = "postgresql://postgres:Smart_port123@db.zmkrkrfdfjddlikziocg.supabase.co:5432/postgres"

def get_connection():
    try:
        conn = psycopg2.connect(DB_URI)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

# Tables ටික සහ Default Admin ව සර්වර් එක ඇතුළේ ඔටෝම හදන Function එක
def init_db():
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Users Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'operator',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        # Sessions Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            );
        """)
        
        # Default Admin කෙනෙක් නැත්නම් ඔටෝම ඇතුළත් කිරීම
        cur.execute("SELECT id FROM users WHERE email = 'admin@smartport.lk';")
        if not cur.fetchone():
            pw_hash = hash_password("admin123")
            cur.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                ("System Administrator", "admin@smartport.lk", pw_hash, "admin")
            )
        conn.commit()
    except Exception as e:
        print(f"Init DB Error: {e}")
    finally:
        conn.close()

# App එක Start වෙද්දීම Tables ටික රන් වෙනවා
init_db()

def register_user(full_name: str, email: str, password: str, role: str = "operator") -> dict:
    if role not in ("admin", "operator"):
        role = "operator"

    conn = get_connection()
    if not conn:
        return {"ok": False, "error": "Database unavailable"}
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email.lower().strip(),))
        if cur.fetchone():
            return {"ok": False, "error": "This email is already registered."}
        pw_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
            (full_name.strip(), email.lower().strip(), pw_hash, role)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return {"ok": True, "user_id": user_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()

def login_user(email: str, password: str) -> dict:
    conn = get_connection()
    if not conn:
        return {"ok": False, "error": "Database unavailable"}
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT id, full_name, email, password_hash, role, is_active FROM users WHERE email = %s",
            (email.lower().strip(),)
        )
        user = cur.fetchone()
        if not user:
            return {"ok": False, "error": "No account found with that email."}
        if not user["is_active"]:
            return {"ok": False, "error": "Account is disabled. Contact your administrator."}
        if not verify_password(password, user["password_hash"]):
            return {"ok": False, "error": "Incorrect password."}

        cur.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.now(), user["id"]))

        token = secrets.token_hex(32)
        expires = datetime.now() + timedelta(hours=8)
        cur.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user["id"], token, expires)
        )
        conn.commit()
        user.pop("password_hash")
        return {"ok": True, "user": dict(user), "token": token}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()

def logout_user(token: str):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
            conn.commit()
        finally:
            conn.close()
