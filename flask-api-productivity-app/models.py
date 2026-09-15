from datetime import date

from sqlalchemy.orm import validates

from config import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String, nullable=False)

    workouts = db.relationship(
        "Workout", backref="user", cascade="all, delete-orphan", lazy=True
    )

    @property
    def password_hash(self):
        raise AttributeError("password_hash is not a readable attribute")

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError("Username must not be empty")
        return username.strip()

    def to_dict(self):
        return {"id": self.id, "username": self.username}

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    duration_minutes = db.Column(db.Integer, nullable=False)
    date_logged = db.Column(db.Date, default=date.today, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @validates("title")
    def validate_title(self, key, title):
        if not title or not str(title).strip():
            raise ValueError("Title must not be empty")
        return title.strip()

    @validates("duration_minutes")
    def validate_duration(self, key, duration_minutes):
        try:
            duration_minutes = int(duration_minutes)
        except (TypeError, ValueError):
            raise ValueError("Duration (minutes) must be a whole number")
        if duration_minutes <= 0:
            raise ValueError("Duration (minutes) must be a positive number")
        return duration_minutes

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "date_logged": self.date_logged.isoformat() if self.date_logged else None,
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Workout {self.id}: {self.title}>"
