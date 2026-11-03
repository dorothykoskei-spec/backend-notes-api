from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

# Database extension
db = SQLAlchemy()

# Password hashing extension
bcrypt = Bcrypt()

# Marshmallow serialization extension
ma = Marshmallow()
