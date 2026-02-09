from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class People(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    height = db.Column(db.String(80), nullable=False)
    mass = db.Column(db.String(80), nullable=False)
    hair_color = db.Column(db.String(80), nullable=False)
    skin_color = db.Column(db.String(80), nullable=False)
    eye_color = db.Column(db.String(80), nullable=False)
    birth_year = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(80), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
        }


class Planets(db.Model):
    __tablename__ = "planets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    climate = db.Column(db.String(80), nullable=False)
    terrain = db.Column(db.String(80), nullable=False)
    population = db.Column(db.String(80), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
        }


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # One-to-many: un usuario tiene muchos favorites
    favorites = db.relationship(
        "Favorites",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


class Favorites(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=True)

    # relaciones (opcional pero recomendado)
    user = db.relationship("Users", back_populates="favorites")
    planet = db.relationship("Planets", lazy=True)
    people = db.relationship("People", lazy=True)

    def validate(self):
        # Debe ser planeta o persona, pero no ninguno de los dos
        if self.planet_id is None and self.people_id is None:
            raise ValueError("A favorite must be either a planet or a person.")

        # (Opcional) si querés impedir que sea ambos a la vez:
        if self.planet_id is not None and self.people_id is not None:
            raise ValueError("A favorite cannot be both a planet and a person.")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id,
        }
