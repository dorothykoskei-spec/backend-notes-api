from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from marshmallow import ValidationError

from models import db, Note
from schemas import NoteSchema

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

    note = Note(
        title=data["title"],
        content=data["content"],
        user_id=current_user.id
    )

    db.session.add(note)
    db.session.commit()

    return jsonify(note_schema.dump(note)), 201


@notes_bp.route("/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    note = db.session.get(Note, note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    if note.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(note_schema.dump(note)), 200