import re
import threading
import time
from collections import defaultdict, deque
from functools import wraps

from flask import jsonify, session

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_attempts = defaultdict(deque)
_attempt_lock = threading.Lock()


def validate_registration(data):
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not 2 <= len(username) <= 40:
        return None, "Le nom doit contenir entre 2 et 40 caractères."
    if not EMAIL_RE.fullmatch(email) or len(email) > 254:
        return None, "L'adresse e-mail n'est pas valide."
    if len(password) < 10 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        return None, "Le mot de passe doit avoir 10 caractères, une lettre et un chiffre."
    return {"username": username, "email": email, "password": password}, None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Connecte-toi pour effectuer cette action."}), 401
        return view(*args, **kwargs)

    return wrapped


def login_rate_limited(email):
    key = email
    now = time.monotonic()
    with _attempt_lock:
        attempts = _attempts[key]
        while attempts and now - attempts[0] > 900:
            attempts.popleft()
        if len(attempts) >= 5:
            return True
        attempts.append(now)
    return False


def clear_login_attempts(email):
    key = email
    with _attempt_lock:
        _attempts.pop(key, None)
