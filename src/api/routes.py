from flask import jsonify, request
from api.models import db, People, Planets, Users, Favorites
import requests

# Simulamos "usuario actual" (porque NO hay auth todavía)
CURRENT_USER_ID = 1


def setup_routes(app):

    # -----------------------------
    # Helpers
    # -----------------------------
    def get_current_user():
        """
        Devuelve el usuario actual. Si no existe, lo crea (id = CURRENT_USER_ID).
        """
        user = Users.query.get(CURRENT_USER_ID)
        if user is None:
            user = Users(id=CURRENT_USER_ID, username="demo", email="demo@test.com")
            db.session.add(user)
            db.session.commit()
        return user

    def to_str(value):
        if value is None:
            return ""
        return str(value)

    def safe_get(url: str):
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    # -----------------------------
    # Endpoints básicos (requeridos)
    # -----------------------------
    @app.route("/people", methods=["GET"])
    def get_people():
        people = People.query.all()
        return jsonify([p.serialize() for p in people]), 200

    @app.route("/people/<int:people_id>", methods=["GET"])
    def get_one_people(people_id):
        person = People.query.get(people_id)
        if person is None:
            return jsonify({"msg": "Person not found"}), 404
        return jsonify(person.serialize()), 200

    @app.route("/planets", methods=["GET"])
    def get_planets():
        planets = Planets.query.all()
        return jsonify([p.serialize() for p in planets]), 200

    @app.route("/planets/<int:planet_id>", methods=["GET"])
    def get_one_planet(planet_id):
        planet = Planets.query.get(planet_id)
        if planet is None:
            return jsonify({"msg": "Planet not found"}), 404
        return jsonify(planet.serialize()), 200

    # -----------------------------
    # Users + Favorites (requeridos)
    # -----------------------------
    @app.route("/users", methods=["GET"])
    def get_users():
        users = Users.query.all()
        return jsonify([u.serialize() for u in users]), 200

    @app.route("/users/favorites", methods=["GET"])
    def get_current_user_favorites():
        """
        Enunciado: listar todos los favoritos del usuario actual.
        """
        get_current_user()  # asegura que exista
        favs = Favorites.query.filter_by(user_id=CURRENT_USER_ID).all()
        return jsonify([f.serialize() for f in favs]), 200

    @app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
    def add_favorite_planet(planet_id):
        """
        Enunciado: añade planet favorito al usuario actual.
        """
        get_current_user()

        planet = Planets.query.get(planet_id)
        if planet is None:
            return jsonify({"msg": "Planet not found"}), 404

        exists = Favorites.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
        if exists:
            return jsonify({"msg": "Favorite already exists", "favorite": exists.serialize()}), 200

        fav = Favorites(user_id=CURRENT_USER_ID, planet_id=planet_id)
        try:
            fav.validate()
        except Exception as e:
            return jsonify({"msg": str(e)}), 400

        db.session.add(fav)
        db.session.commit()
        return jsonify(fav.serialize()), 201

    @app.route("/favorite/people/<int:people_id>", methods=["POST"])
    def add_favorite_people(people_id):
        """
        Enunciado: añade people favorito al usuario actual.
        """
        get_current_user()

        person = People.query.get(people_id)
        if person is None:
            return jsonify({"msg": "Person not found"}), 404

        exists = Favorites.query.filter_by(user_id=CURRENT_USER_ID, people_id=people_id).first()
        if exists:
            return jsonify({"msg": "Favorite already exists", "favorite": exists.serialize()}), 200

        fav = Favorites(user_id=CURRENT_USER_ID, people_id=people_id)
        try:
            fav.validate()
        except Exception as e:
            return jsonify({"msg": str(e)}), 400

        db.session.add(fav)
        db.session.commit()
        return jsonify(fav.serialize()), 201

    @app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
    def delete_favorite_planet(planet_id):
        """
        Enunciado: elimina planet favorito por planet_id del usuario actual.
        """
        get_current_user()

        fav = Favorites.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
        if fav is None:
            return jsonify({"msg": "Favorite planet not found"}), 404

        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "Deleted"}), 200

    @app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
    def delete_favorite_people(people_id):
        """
        Enunciado: elimina people favorito por people_id del usuario actual.
        """
        get_current_user()

        fav = Favorites.query.filter_by(user_id=CURRENT_USER_ID, people_id=people_id).first()
        if fav is None:
            return jsonify({"msg": "Favorite people not found"}), 404

        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "Deleted"}), 200

    # -----------------------------
    # Seeds (opcional, para poblar DB)
    # -----------------------------
    @app.route("/seed/test", methods=["POST"])
    def seed_test():
        """
        Crea 1 planeta y 1 persona para verificar que la DB guarda data.
        """
        get_current_user()

        planet = Planets(name="Test Planet", climate="temperate", terrain="plains", population="123456")
        person = People(
            name="Test Person",
            height="180",
            mass="80",
            hair_color="black",
            skin_color="light",
            eye_color="brown",
            birth_year="19BBY",
            gender="male",
        )

        db.session.add(planet)
        db.session.add(person)
        db.session.commit()

        return jsonify({
            "msg": "Test data created",
            "planet": planet.serialize(),
            "person": person.serialize()
        }), 201

    @app.route("/seed/swapi", methods=["POST"])
    def seed_swapi():
        """
        Poblar People y Planets desde SWAPI.
        Body opcional:
        { "people_limit": 10, "planets_limit": 10 }
        """
        body = request.get_json(silent=True) or {}
        people_limit = int(body.get("people_limit", 10))
        planets_limit = int(body.get("planets_limit", 10))

        get_current_user()

        created_planets = 0
        created_people = 0

        try:
            # Planets
            planet_url = "https://swapi.dev/api/planets/"
            while planet_url and created_planets < planets_limit:
                data = safe_get(planet_url)
                for item in data.get("results", []):
                    if created_planets >= planets_limit:
                        break

                    name = to_str(item.get("name"))
                    if Planets.query.filter_by(name=name).first():
                        continue

                    p = Planets(
                        name=name,
                        climate=to_str(item.get("climate")),
                        terrain=to_str(item.get("terrain")),
                        population=to_str(item.get("population")),
                    )
                    db.session.add(p)
                    created_planets += 1

                db.session.commit()
                planet_url = data.get("next")

            # People
            people_url = "https://swapi.dev/api/people/"
            while people_url and created_people < people_limit:
                data = safe_get(people_url)
                for item in data.get("results", []):
                    if created_people >= people_limit:
                        break

                    name = to_str(item.get("name"))
                    if People.query.filter_by(name=name).first():
                        continue

                    person = People(
                        name=name,
                        height=to_str(item.get("height")),
                        mass=to_str(item.get("mass")),
                        hair_color=to_str(item.get("hair_color")),
                        skin_color=to_str(item.get("skin_color")),
                        eye_color=to_str(item.get("eye_color")),
                        birth_year=to_str(item.get("birth_year")),
                        gender=to_str(item.get("gender")),
                    )
                    db.session.add(person)
                    created_people += 1

                db.session.commit()
                people_url = data.get("next")

            return jsonify({
                "msg": "SWAPI seeded!",
                "created": {"planets": created_planets, "people": created_people}
            }), 201

        except Exception as e:
            return jsonify({
                "msg": "SWAPI seed failed",
                "error": str(e),
                "created_so_far": {"planets": created_planets, "people": created_people}
            }), 500
