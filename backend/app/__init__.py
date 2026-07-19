from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_wtf.csrf import CSRFError

from .config import Config
from .extensions import csrf, db


def create_app(test_config=None):
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    if (
        app.config.get("SESSION_COOKIE_SECURE")
        and app.config["SECRET_KEY"] == "dev-only-change-me-before-production"
    ):
        raise RuntimeError("SECRET_KEY doit être définie en production.")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    from .routes.auth import auth_bp
    from .routes.favorites import favorites_bp
    from .routes.travel import travel_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(travel_bp, url_prefix="/api")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "TripPilot API"}

    @app.get("/")
    @app.get("/<path:path>")
    def frontend(path=""):
        """Serve the React build and let React Router handle client routes."""
        if path.startswith("api/"):
            return jsonify({"error": "Ressource introuvable."}), 404
        requested_file = frontend_dist / path
        if path and requested_file.is_file():
            return send_from_directory(frontend_dist, path)
        index_file = frontend_dist / "index.html"
        if index_file.is_file():
            return send_from_directory(frontend_dist, "index.html")
        return jsonify({"error": "Frontend non compilé. Lance `npm run build`."}), 503

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return jsonify({"error": "La session de sécurité a expiré. Recharge la page."}), 400

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Ressource introuvable."}), 404

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(self)"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https://images.unsplash.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    with app.app_context():
        db.create_all()

    return app
