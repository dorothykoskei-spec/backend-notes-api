from functools import wraps
from flask import session, jsonify, g
from config import db
from models.user import User

# Get the currently logged-in user
def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    user = db.session.get(User, user_id)

    if user is None:
        session.pop("user_id", None)

    return user

# Get the ID of the currently logged-in user
def get_current_user_id():
    user = get_current_user()

    if user is None:
        return None

    return user.id

# Protect routes that require a logged-in user
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()

        if user is None:
            return jsonify({
                "error": "Please log in to access this resource."
            }), 401

        g.current_user = user

        return view(*args, **kwargs)

    return wrapped_view

# Get a note only if it belongs to the logged-in user
def get_owned_note(note_id):
    from models.note import Note

    user = get_current_user()

    if user is None:
        return None

    note = Note.query.filter_by(
        id=note_id,
        user_id=user.id
    ).first()

    return note

# Get a category only if it belongs to the logged-in user
def get_owned_category(category_id):
    from models.categories import Category

    user = get_current_user()

    if user is None:
        return None

    category = Category.query.filter_by(
        id=category_id,
        user_id=user.id
    ).first()

    return category
