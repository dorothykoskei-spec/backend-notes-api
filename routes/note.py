from flask import Blueprint, request, jsonify, session
from marshmallow import ValidationError

from config import db
from models.note import Note
from models.categories import Category
from schemas.note_schema import NoteSchema

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


def get_current_user_id():
    # TEMPORARY: replace with Faith's helper once it exists
    return session.get("user_id")


@notes_bp.route("", methods=["POST"])
def create_note():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = note_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 422

    category_id = data.get("category_id")
    if category_id is not None:
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404

    note = Note(
        title=data["title"],
        content=data["content"],
        user_id=user_id,
        category_id=category_id,
    )
    db.session.add(note)
    db.session.commit()

    return jsonify(note_schema.dump(note)), 201


@notes_bp.route("/<int:note_id>", methods=["GET"])
def get_note(note_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note_schema.dump(note)), 200