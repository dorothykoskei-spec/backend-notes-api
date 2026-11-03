
from functools import wraps

from flask import session, jsonify, g

from config import db
from models.user import User


def get_current_user():
    """Return the currently logged-in user."""

    user_id = session.get("user_id")

    if user_id is None:
        return None

    user = db.session.get(User, user_id)

    if user is None:
        session.pop("user_id", None)

    return user


def get_current_user_id():
    """Return the ID of the currently logged-in user."""

    user = get_current_user()

    if user is None:
        return None

    return user.id


def login_required(view):
    """Protect a route from users who are not logged in."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        user = get_current_user()

        if user is None:
            return jsonify({
                "error": "Unauthorized. Please log in first."
            }), 401

        g.current_user = user

        return view(*args, **kwargs)

    return wrapped_view


def get_owned_note(note_id):
    """Return a note only if it belongs to the logged-in user."""

    from models.note import Note

    user = get_current_user()

    if user is None:
        return None

    return Note.query.filter_by(
        id=note_id,
        user_id=user.id
    ).first()


def get_owned_category(category_id):
    """Return a category only if it belongs to the logged-in user."""

    from models.categories import Category

    user = get_current_user()

    if user is None:
        return None

    return Category.query.filter_by(
        id=category_id,
        user_id=user.id
    ).first()
