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
        return jsonify({"errors": error.messages}), 422

    category_id = data.get("category_id")
    if category_id is not None and not get_owned_category(category_id):
        return jsonify({"error": "Category not found"}), 404

    note = Note(
        title=data["title"],
        content=data["content"],
        user_id=g.current_user.id,
        category_id=category_id,
    )
    db.session.add(note)
    db.session.commit()

    return jsonify(note_schema.dump(note)), 201


@notes_bp.route("/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    note = get_owned_note(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note_schema.dump(note)), 200