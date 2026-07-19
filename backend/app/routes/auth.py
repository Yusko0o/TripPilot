from flask import Blueprint, jsonify, request, session
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User
from ..security import clear_login_attempts, login_rate_limited, validate_registration

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/csrf")
def csrf_token():
    return {"csrfToken": generate_csrf()}


@auth_bp.post("/register")
def register():
    data, error = validate_registration(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Impossible de créer ce compte avec ces informations."}), 409

    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()[:254]
    password = str(data.get("password", ""))

    if login_rate_limited(email):
        return jsonify({"error": "Trop de tentatives. Réessaie dans 15 minutes."}), 429

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if user is None or not user.check_password(password):
        return jsonify({"error": "E-mail ou mot de passe incorrect."}), 401

    clear_login_attempts(email)
    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return {"user": user.to_dict()}


@auth_bp.post("/logout")
def logout():
    session.clear()
    return {"message": "Déconnexion réussie."}


@auth_bp.get("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return {"user": None}
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return {"user": None}
    return {"user": user.to_dict()}

