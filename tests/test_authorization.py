from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from flask import Flask, g, jsonify, session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
fake_db = SimpleNamespace(session=SimpleNamespace(get=Mock()))

class FakeUser:
    pass

fake_config = ModuleType("config")
fake_config.db = fake_db

fake_models = ModuleType("models")
fake_models.__path__ = []

fake_user_module = ModuleType("models.user")
fake_user_module.User = FakeUser

# Use a fake database so we can test the authorization helpers without the full app.
spec = spec_from_file_location(
    "_auth_helpers_under_test",
    PROJECT_ROOT / "auth_helpers.py"
)
auth_helpers = module_from_spec(spec)

with patch.dict(
    "sys.modules",
    {
        "config": fake_config,
        "models": fake_models,
        "models.user": fake_user_module,
    },
):
    spec.loader.exec_module(auth_helpers)

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    return app

@pytest.fixture(autouse=True)
def reset_database_mock():
    fake_db.session.get.reset_mock()
    fake_db.session.get.return_value = None
    yield
    fake_db.session.get.reset_mock()

def test_get_current_user_returns_none_when_session_has_no_user_id(app):
    with app.test_request_context():
        assert auth_helpers.get_current_user() is None

    fake_db.session.get.assert_not_called()

def test_get_current_user_returns_user_from_database(app):
    user = SimpleNamespace(id=1)
    fake_db.session.get.return_value = user

    with app.test_request_context():
        session["user_id"] = 1
        result = auth_helpers.get_current_user()

    assert result is user
    fake_db.session.get.assert_called_once_with(FakeUser, 1)

def test_get_current_user_clears_session_when_user_does_not_exist(app):
    fake_db.session.get.return_value = None

    with app.test_request_context():
        session["user_id"] = 999
        result = auth_helpers.get_current_user()

        assert result is None
        assert "user_id" not in session

def test_get_current_user_id_returns_logged_in_user_id(app):
    user = SimpleNamespace(id=5)
    fake_db.session.get.return_value = user

    with app.test_request_context():
        session["user_id"] = 5
        result = auth_helpers.get_current_user_id()

    assert result == 5

def test_get_current_user_id_returns_none_when_not_logged_in(app):
    with app.test_request_context():
        assert auth_helpers.get_current_user_id() is None

def test_login_required_returns_401_when_user_is_not_logged_in(app):
    @auth_helpers.login_required
    def protected_route():
        return jsonify({"message": "You reached the protected route"}), 200

    with app.test_request_context():
        response, status_code = protected_route()

    assert status_code == 401
    assert response.get_json() == {
        "error": "Please log in to access this resource."
    }

def test_login_required_sets_current_user_and_allows_access(app):
    user = SimpleNamespace(id=8)
    fake_db.session.get.return_value = user

    @auth_helpers.login_required
    def protected_route():
        return jsonify({"user_id": g.current_user.id}), 200

    with app.test_request_context():
        session["user_id"] = 8
        response, status_code = protected_route()

    assert status_code == 200
    assert response.get_json() == {"user_id": 8}

def test_get_owned_note_returns_only_note_matching_user_id(app):
    user = SimpleNamespace(id=3)
    note = SimpleNamespace(id=12, user_id=3)
    fake_db.session.get.return_value = user

    class FakeQuery:
        def __init__(self):
            self.filters = None

        def filter_by(self, **kwargs):
            self.filters = kwargs
            return self

        def first(self):
            return note

    query = FakeQuery()
    fake_note_module = ModuleType("models.note")
    fake_note_module.Note = SimpleNamespace(query=query)

    with app.test_request_context():
        session["user_id"] = 3
        with patch.dict("sys.modules", {"models.note": fake_note_module}):
            result = auth_helpers.get_owned_note(12)

    assert result is note
    assert query.filters == {"id": 12, "user_id": 3}

def test_get_owned_note_returns_none_when_note_is_not_owned(app):
    user = SimpleNamespace(id=3)
    fake_db.session.get.return_value = user

    class FakeQuery:
        def filter_by(self, **kwargs):
            assert kwargs == {"id": 12, "user_id": 3}
            return self

        def first(self):
            return None

    fake_note_module = ModuleType("models.note")
    fake_note_module.Note = SimpleNamespace(query=FakeQuery())

    with app.test_request_context():
        session["user_id"] = 3
        with patch.dict("sys.modules", {"models.note": fake_note_module}):
            result = auth_helpers.get_owned_note(12)

    assert result is None

def test_get_owned_note_returns_none_when_user_is_not_logged_in(app):
    fake_note_module = ModuleType("models.note")
    fake_note_module.Note = SimpleNamespace(query=Mock())

    with app.test_request_context():
        with patch.dict("sys.modules", {"models.note": fake_note_module}):
            result = auth_helpers.get_owned_note(12)

    assert result is None
    fake_db.session.get.assert_not_called()

def test_get_owned_category_returns_only_category_matching_user_id(app):
    user = SimpleNamespace(id=4)
    category = SimpleNamespace(id=7, user_id=4)
    fake_db.session.get.return_value = user

    class FakeQuery:
        def __init__(self):
            self.filters = None

        def filter_by(self, **kwargs):
            self.filters = kwargs
            return self

        def first(self):
            return category

    query = FakeQuery()
    fake_category_module = ModuleType("models.categories")
    fake_category_module.Category = SimpleNamespace(query=query)

    with app.test_request_context():
        session["user_id"] = 4
        with patch.dict("sys.modules", {"models.categories": fake_category_module}):
            result = auth_helpers.get_owned_category(7)

    assert result is category
    assert query.filters == {"id": 7, "user_id": 4}

def test_get_owned_category_returns_none_when_category_is_not_owned(app):
    user = SimpleNamespace(id=4)
    fake_db.session.get.return_value = user

    class FakeQuery:
        def filter_by(self, **kwargs):
            assert kwargs == {"id": 7, "user_id": 4}
            return self

        def first(self):
            return None

    fake_category_module = ModuleType("models.categories")
    fake_category_module.Category = SimpleNamespace(query=FakeQuery())

    with app.test_request_context():
        session["user_id"] = 4
        with patch.dict("sys.modules", {"models.categories": fake_category_module}):
            result = auth_helpers.get_owned_category(7)

    assert result is None

def test_get_owned_category_returns_none_when_user_is_not_logged_in(app):
    fake_category_module = ModuleType("models.categories")
    fake_category_module.Category = SimpleNamespace(query=Mock())

    with app.test_request_context():
        with patch.dict("sys.modules", {"models.categories": fake_category_module}):
            result = auth_helpers.get_owned_category(7)

    assert result is None
    fake_db.session.get.assert_not_called()