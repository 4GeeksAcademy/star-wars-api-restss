import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate

from api.models import db
from api.routes import setup_routes
from api.admin import setup_admin
from api.utils import generate_sitemap, APIException

# -----------------------------
# Crear la app Flask
# -----------------------------
app = Flask(__name__)
app.url_map.strict_slashes = False

# -----------------------------
# Configuración DB
# -----------------------------
db_url = os.getenv("DATABASE_URL")

if db_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Migrate(app, db)

# -----------------------------
# Middlewares
# -----------------------------
CORS(app)

# -----------------------------
# Registrar admin y rutas
# -----------------------------
setup_admin(app)
setup_routes(app)

# -----------------------------
# Sitemap
# -----------------------------
@app.route("/")
def sitemap():
    return generate_sitemap(app)


# -----------------------------
# Error handler
# -----------------------------
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=PORT, debug=True)
