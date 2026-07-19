from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    destinations = db.relationship(
        "FavoriteDestination", back_populates="user", cascade="all, delete-orphan"
    )
    flights = db.relationship(
        "FavoriteFlight", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}


class FavoriteDestination(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "city", "country", name="uq_user_destination"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    user = db.relationship("User", back_populates="destinations")

    def to_dict(self):
        return {
            "id": self.id,
            "type": "destination",
            "city": self.city,
            "country": self.country,
            "image": self.image,
        }


class FavoriteFlight(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "provider", "flight_number", "departure_time",
            name="uq_user_flight",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    provider = db.Column(db.String(60), nullable=False)
    flight_number = db.Column(db.String(20), nullable=False)
    departure_airport = db.Column(db.String(10), nullable=False)
    arrival_airport = db.Column(db.String(10), nullable=False)
    departure_time = db.Column(db.String(40), nullable=False)
    arrival_time = db.Column(db.String(40), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default="EUR", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    user = db.relationship("User", back_populates="flights")

    def to_dict(self):
        return {
            "id": self.id,
            "type": "flight",
            "provider": self.provider,
            "flightNumber": self.flight_number,
            "from": self.departure_airport,
            "to": self.arrival_airport,
            "departureTime": self.departure_time,
            "arrivalTime": self.arrival_time,
            "price": self.price_cents / 100,
            "currency": self.currency,
        }

