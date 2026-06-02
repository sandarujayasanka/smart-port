"""
db.py  —  Supabase Data API connection helpers for Smart Port App
Requires:  pip install supabase bcrypt
"""

import streamlit as st
import bcrypt
import secrets
from datetime import datetime, timedelta
from supabase import create_client, Client

# Supabase Credentials (100% Correct & Secured)
SUPABASE_URL = "https://zmkrkrfdfjddlikziocg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpta3JrcmZkZmpkZGxpa3ppb2NnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAzOTcyMjgsImV4cCI6MjA5NTk3MzIyOH0.NdYjvvcI2dvYjtdD0mCK7jBnSO7rFMvd5M7YhlW2y8s"

def get_supabase_client() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase API connection failed: {e}")
        return None

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def register_user(full_name: str, email: str, password: str, role: str = "operator") -> dict:
    if role not in ("admin", "operator"):
        role = "operator"

    supabase = get_supabase_client()
    if not supabase:
        return {"ok": False, "error": "Database unavailable"}
    
    try:
        # Email එක දැනටමත් තියෙනවාද බැලීම
        res = supabase.table("users").select("id").eq("email", email.lower().strip()).execute()
        if res.data:
            return {"ok": False, "error": "This email is already registered."}
            
        pw_hash = hash_password(password)
        # අලුත් යූසර් ඇතුළත් කිරීම
        insert_res = supabase.table("users").insert({
            "full_name": full_name.strip(),
            "email": email.lower().strip(),
            "password_hash": pw_hash,
            "role": role
        }).execute()
        
        return {"ok": True, "user_id": insert_res.data[0]["id"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def login_user(email: str, password: str) -> dict:
    supabase = get_supabase_client()
    if not supabase:
        return {"ok": False, "error": "Database unavailable"}
        
    try:
        res = supabase.table("users").select("*").eq("email", email.lower().strip()).execute()
        if not res.data:
            return {"ok": False, "error": "No account found with that email."}
            
        user = res.data[0]
        if not user["is_active"]:
            return {"ok": False, "error": "Account is disabled. Contact your administrator."}
        if not verify_password(password, user["password_hash"]):
            return {"ok": False, "error": "Incorrect password."}

        # Last Login Update කිරීම
        supabase.table("users").update({"last_login": datetime.now().isoformat()}).eq("id", user["id"]).execute()

        token = secrets.token_hex(32)
        expires = (datetime.now() + timedelta(hours=8)).isoformat()
        
        # Session එකක් සෑදීම
        supabase.table("sessions").insert({
            "user_id": user["id"],
            "token": token,
            "expires_at": expires
        }).execute()
        
        user.pop("password_hash")
        return {"ok": True, "user": user, "token": token}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def logout_user(token: str):
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.table("sessions").delete().eq("token", token).execute()
        except Exception:
            pass
