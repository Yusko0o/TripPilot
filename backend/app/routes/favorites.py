from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import FavoriteDestination, FavoriteFlight
from ..security import login_required

favorites_bp = Blueprint("favorites", __name__)


def clean_text(data, key, max_length, required=True):
    value = str(data.get(key, "")).strip()
    if required and not value:
        raise ValueError(f"Le champ {key} est obligatoire.")
    if len(value) > max_length:
        raise ValueError(f"Le champ {key} est trop long.")
    return value


@favorites_bp.get("")
@login_required
def list_favorites():
    user_id = session["user_id"]
    destinations = db.session.execute(
        db.select(FavoriteDestination)
        .filter_by(user_id=user_id)
        .order_by(FavoriteDestination.created_at.desc())
    ).scalars()
    flights = db.session.execute(
        db.select(FavoriteFlight)
        .filter_by(user_id=user_id)
        .order_by(FavoriteFlight.created_at.desc())
    ).scalars()
    return {
        "destinations": [item.to_dict() for item in destinations],
        "flights": [item.to_dict() for item in flights],
    }


@favorites_bp.post("/destinations")
@login_required
def add_destination():
    data = request.get_json(silent=True) or {}
    try:
        favorite = FavoriteDestination(
            user_id=session["user_id"],
            city=clean_text(data, "city", 100),
            country=clean_text(data, "country", 100),
            image=clean_text(data, "image", 500, required=False) or None,
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return save_favorite(favorite)


@favorites_bp.post("/flights")
@login_required
def add_flight():
    data = request.get_json(silent=True) or {}
    try:
        price = float(data.get("price", -1))
        if not 0 <= price <= 100000:
            raise ValueError("Le prix est invalide.")
        favorite = FavoriteFlight(
            user_id=session["user_id"],
            provider=clean_text(data, "provider", 60),
            flight_number=clean_text(data, "flightNumber", 20),
            departure_airport=clean_text(data, "from", 10),
            arrival_airport=clean_text(data, "to", 10),
            departure_time=clean_text(data, "departureTime", 40),
            arrival_time=clean_text(data, "arrivalTime", 40),
            price_cents=round(price * 100),
            currency=clean_text(data, "currency", 3).upper(),
        )
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    return save_favorite(favorite)


def save_favorite(favorite):
    db.session.add(favorite)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cet élément se trouve déjà dans tes favoris."}), 409
    return jsonify({"favorite": favorite.to_dict()}), 201


@favorites_bp.delete("/<string:item_type>/<int:item_id>")
@login_required
def delete_favorite(item_type, item_id):
    models = {"destination": FavoriteDestination, "flight": FavoriteFlight}
    model = models.get(item_type)
    if model is None:
        return jsonify({"error": "Type de favori invalide."}), 400

    favorite = db.session.execute(
        db.select(model).filter_by(id=item_id, user_id=session["user_id"])
    ).scalar_one_or_none()
    if favorite is None:
        return jsonify({"error": "Favori introuvable."}), 404

    db.session.delete(favorite)
    db.session.commit()
    return {"message": "Favori supprimé."}

