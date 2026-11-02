from flask import Blueprint, request, session, jsonify
from marshmallow import ValidationError

from config import db
from models.category import Category
from schemas.category_schema import category_schema, categories_schema

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


def get_current_user_id():
    # TEMPORARY: replace with Faith's helper once it exists
    return session.get("user_id")


@categories_bp.route("", methods=["POST"])
def create_category():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = category_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    category = Category(name=data["name"], user_id=user_id)
    db.session.add(category)
    db.session.commit()

    return jsonify(category_schema.dump(category)), 201


@categories_bp.route("", methods=["GET"])
def get_categories():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    categories = Category.query.filter_by(user_id=user_id).all()

    return jsonify(categories_schema.dump(categories)), 200


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify(category_schema.dump(category)), 200


@categories_bp.route("/<int:category_id>", methods=["PATCH"])
def update_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        data = category_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if "name" in data:
        category.name = data["name"]

    db.session.commit()

    return jsonify(category_schema.dump(category)), 200


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()

    return "", 204