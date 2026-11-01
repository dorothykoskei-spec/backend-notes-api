from flask import Blueprint, request, jsonify, session
from marshamllow import ValidationError
from config import db
from models.user import User
from schemas.user_schema import user_schema

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() 

    if not data:
        return jsonify({"error": "Request data missing"}), 400
    try:
        validated_data = user_schema.load(data)
    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 400
    user = User(
        username=username,
        email=email,
        password=password
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "message": "User registered successfully",
        "user": user_schema.dump(user)
        }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request data is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            "error": "Invalid email or password"
        }), 401
    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "message": "Login successful",
        "user": user_schema.dump(user)
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "message": "Logout successful"
    }), 200

@auth_bp.route("/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Please log in first"
        }), 401
    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "user": user_schema.dump(user)
    }), 200