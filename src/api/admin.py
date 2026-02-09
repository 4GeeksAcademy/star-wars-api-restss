import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from api.models import db, Users, People, Planets, Favorites

def setup_admin(app):
    app.secret_key = os.environ.get("FLASK_ADMIN_KEY", "super-secret-key")
    admin = Admin(app, name="Star Wars Admin", template_mode="bootstrap3")

    admin.add_view(ModelView(Users, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(ModelView(Planets, db.session))
    admin.add_view(ModelView(Favorites, db.session))
