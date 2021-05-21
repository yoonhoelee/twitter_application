import os
from flask import Flask
from twit_app.routes import main_routes
from twit_app.models import db, migrate
from dotenv import load_dotenv
load_dotenv()



DATABASE_URI = os.getenv("DATABASE_URL")


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_routes.main_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)