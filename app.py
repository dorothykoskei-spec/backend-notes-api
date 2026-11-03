from flask import Flask

from config import Config
from extensions import db, bcrypt, ma, migrate

# Import models
from models.user import User
from models.note import Note
from models.categories import Category

# Import routes
from routes.auth import auth_bp
from routes.note import notes_bp
from routes.categories import categories_bp


def create_app():

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(categories_bp)

    @app.route("/")
    def home():
        return {
            "message": "Backend Notes API is running!"
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
