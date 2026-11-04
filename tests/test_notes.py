
import pytest
from app import create_app
from extensions import db
from models.user import User
from models.note import Note

# Create a test app and a temporary database for each test
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        # Create a test client to send requests to the app
        with app.test_client() as client:
            yield client

        # Remove the test data after each test
        db.session.remove()
        db.drop_all()

# Register a user for testing
def register_user(client, username, email):
    return client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "password123"
    })

# Log in a user before testing protected routes
def login_user(client, email):
    return client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })

# Create a note directly in the database for testing
def create_note_record(client, email, title="Test Note", content="Test content"):
    with client.application.app_context():
        user = User.query.filter_by(email=email).first()
        note = Note(
            title=title,
            content=content,
            user_id=user.id
        )
        db.session.add(note)
        db.session.commit()
        return note.id

# Test that a logged-in user can create a note
def test_create_note_successfully(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")

    response = client.post("/notes", json={
        "title": "My First Note",
        "content": "This is my first note"
    })

    assert response.status_code == 201
    assert response.json["title"] == "My First Note"

# Test that a user cannot create a note without logging in
def test_create_note_without_login(client):
    response = client.post("/notes", json={
        "title": "My Note",
        "content": "Some content"
    })

    assert response.status_code == 401

# Test that a note cannot be created without required fields
def test_create_note_without_required_fields(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")

    response = client.post("/notes", json={
        "title": "My Note"
    })

    assert response.status_code == 400

# Test that a user can view their own note
def test_get_own_note(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    note_id = create_note_record(client, "faith@example.com")

    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.json["title"] == "Test Note"

# Test that a user cannot view a note without logging in
def test_get_note_without_login(client):
    response = client.get("/notes/1")

    assert response.status_code == 401

# Test that a user cannot view another user's note
def test_user_cannot_get_another_users_note(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    note_id = create_note_record(client, "user@example.com")
    login_user(client, "faith@example.com")

    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 404

# Test that users only see their own notes
def test_get_notes_only_shows_own_notes(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    create_note_record(client, "faith@example.com", "Faith Note")
    create_note_record(client, "user@example.com", "Other User Note")
    login_user(client, "faith@example.com")

    response = client.get("/notes")

    assert response.status_code == 200
    assert len(response.json["notes"]) == 1
    assert response.json["notes"][0]["title"] == "Faith Note"

# Test that a user can update their own note
def test_update_own_note(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    note_id = create_note_record(client, "faith@example.com")

    response = client.patch(f"/notes/{note_id}", json={
        "title": "Updated Note"
    })

    assert response.status_code == 200
    assert response.json["title"] == "Updated Note"

# Test that a user cannot update another user's note
def test_user_cannot_update_another_users_note(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    note_id = create_note_record(client, "user@example.com")
    login_user(client, "faith@example.com")

    response = client.patch(f"/notes/{note_id}", json={
        "title": "Changed Note"
    })

    assert response.status_code == 404

# Test that a user can delete their own note
def test_delete_own_note(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    note_id = create_note_record(client, "faith@example.com")

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.json["message"] == "Note deleted successfully"

# Test that a user cannot delete another user's note
def test_user_cannot_delete_another_users_note(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    note_id = create_note_record(client, "user@example.com")
    login_user(client, "faith@example.com")

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 404
