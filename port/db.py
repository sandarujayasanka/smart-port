"""
db.py  —  MySQL connection helpers for Smart Port App
Requires:  pip install mysql-connector-python bcrypt
"""

import mysql.connector
from mysql.connector import Error
import bcrypt
import secrets
from datetime import datetime, timedelta
import streamlit as st

DB_CONFIG = {
    "host":     "mysql-1938fbd-sandarujayasanka27-0cd3.h.aivencloud.com",
    "port":     27352,
    "user":     "avnadmin",
    "password": "AVNS_dsQHTSc114xvgwOErps",        
    "database": "defaultdb",
    "autocommit": True,
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def register_user(full_name: str, email: str, password: str, role: str = "operator") -> dict:
    # Only allow valid roles
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
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (full_name.strip(), email.lower().strip(), pw_hash, role)
        )
        return {"ok": True, "user_id": cur.lastrowid}
    except Error as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def login_user(email: str, password: str) -> dict:
    conn = get_connection()
    if not conn:
        return {"ok": False, "error": "Database unavailable"}
    try:
        cur = conn.cursor(dictionary=True)
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
        user.pop("password_hash")
        return {"ok": True, "user": user, "token": token}
    except Error as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def logout_user(token: str):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
        finally:
            conn.close()
