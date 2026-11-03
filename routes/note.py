from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from config import db
from models.note import Note
from schemas.note_schema import NoteSchema
from auth_helpers import login_required, get_owned_note, get_owned_category

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


@notes_bp.route("", methods=["POST"])
@login_required
def create_note():
    try:
        data = note_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400

    category_id = data.get("category_id")

    if category_id is not None:
        category = get_owned_category(category_id)
        if category is None:
            return jsonify({"error": "Category not found"}), 404

    
    note = Note(
        title=data["title"],
        content=data["content"],
        user_id=get_current_user_id(),
        category_id=category_id
    )

    db.session.add(note)
    db.session.commit()

    return jsonify(note_schema.dump(note)), 201


@notes_bp.route("/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    note = get_owned_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note_schema.dump(note)), 200


@notes_bp.route("", methods = ["GET"])
@login_required
def get_notes():
    user_id = get_current_user_id() # Helper function to get the current user's ID from the session or token

    if not user_id:
        return jsonify({"error": "User is not authorized"}), 401

    page = request.args.get("page", 1, type=int)    #Reads the page number from the query parameters, defaulting to 1 if not provided
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1 or per_page < 1:
        return jsonify({"error": "Page and per_page must be positive integers"}), 400

    query = Note.query.filter_by(user_id=user_id)   #Restricts the query to only notes belonging to the current user
    category_id = request.args.get("category_id", type=int)

    if category_id is not None:
        category = get_owned_category(category_id)
        if category is None:
            return jsonify({"error": "Category not found"}), 404
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(Note.id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "notes": notes_schema.dump(pagination.items),
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_notes": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_previous": pagination.has_prev
        }
    }), 200


@notes_bp.route("/<int:note_id>", methods = ["PATCH"])
@login_required
def update_note(note_id):
    note = get_owned_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    try:
        data = note_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400

    if not data:
        return jsonify({"error": "No data provided for update"}), 400


    if "category_id" in data and data["category_id"] is not None:
        category = get_owned_category(data["category_id"])
        if category is None:
            return jsonify({"error": "Category not found"}), 404

    for field, value in data.items():
        setattr(note, field, value)

    db.session.commit()

    return jsonify(note_schema.dump(note)), 200


@notes_bp.route("/<int:note_id>", methods = ["DELETE"])
@login_required
def delete_note(note_id):
    note = get_owned_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Note deleted successfully"}), 200