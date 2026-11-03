from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from config import db
from models.categories import Category
from schemas.category_schema import category_schema, categories_schema
from auth_helpers import login_required, get_owned_category

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("", methods=["POST"])
@login_required
def create_category():
    try:
        data = category_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    category = Category(name=data["name"], user_id=g.current_user.id)
    db.session.add(category)
    db.session.commit()

    return jsonify(category_schema.dump(category)), 201


@categories_bp.route("", methods=["GET"])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=g.current_user.id).all()

    return jsonify(categories_schema.dump(categories)), 200


@categories_bp.route("/<int:category_id>", methods=["GET"])
@login_required
def get_category(category_id):
    category = get_owned_category(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify(category_schema.dump(category)), 200


@categories_bp.route("/<int:category_id>", methods=["PATCH"])
@login_required
def update_category(category_id):
    category = get_owned_category(category_id)
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
@login_required
def delete_category(category_id):
    category = get_owned_category(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()

    return "", 204