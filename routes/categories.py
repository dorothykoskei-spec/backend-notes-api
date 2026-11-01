from flask import Blueprint, request, session, jsonify

from server.extensions import db
from server.models.category import Category

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

def get_current_user_id():
    # TEMPORARY: replace with Faith's helper from auth_helpers.py
    return session.get("user_id")

@categories_bp.route("", methods=["POST"])
def create_category():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 422

    category = Category(name=name, user_id=user_id)
    db.session.add(category)
    db.session.commit()

    return jsonify({"id": category.id, "name": category.name}), 201

@categories_bp.route("", methods=["GET"])
def get_categories():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    categories = Category.query.filter_by(user_id=user_id).all()

    return jsonify([{"id": c.id, "name": c.name} for c in categories]), 200

@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({"id": category.id, "name": category.name}), 200

@categories_bp.route("/<int:category_id>", methods=["PATCH"])
def update_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return jsonify({"error": "Name is required"}), 422
        category.name = name

    db.session.commit()

    return jsonify({"id": category.id, "name": category.name}), 200

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

