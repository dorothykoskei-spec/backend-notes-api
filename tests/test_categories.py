import pytest
from app import create_app
from extensions import db
from models.user import User
from models.categories import Category


# Create a test app and temporary database for each test
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

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


# Create a category directly in the database
def create_category_record(client, email, name="Work"):
    with client.application.app_context():
        user = User.query.filter_by(email=email).first()

        category = Category(name=name, user_id=user.id)
        db.session.add(category)
        db.session.commit()

        return category.id


# Test that a logged-in user can create a category
def test_create_category_successfully(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")

    response = client.post("/categories", json={"name": "Work"})

    assert response.status_code == 201
    assert response.json["name"] == "Work"


# Test that a user cannot create a category without logging in
def test_create_category_without_login(client):
    response = client.post("/categories", json={"name": "Work"})

    assert response.status_code == 401


# Test that a category cannot be created without a name
def test_create_category_without_name(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")

    response = client.post("/categories", json={})

    assert response.status_code == 422


# Test that a category name cannot be empty
def test_create_category_with_empty_name(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")

    response = client.post("/categories", json={"name": "   "})

    assert response.status_code == 422


# Test that a user can view their own categories
def test_get_own_categories(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    create_category_record(client, "faith@example.com", "Work")

    response = client.get("/categories")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Work"


# Test that a user cannot view categories without logging in
def test_get_categories_without_login(client):
    response = client.get("/categories")

    assert response.status_code == 401


# Test that users only see their own categories
def test_get_categories_only_shows_own_categories(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    create_category_record(client, "faith@example.com", "Work")
    create_category_record(client, "user@example.com", "Personal")
    login_user(client, "faith@example.com")

    response = client.get("/categories")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Work"


# Test that a user can view their own category
def test_get_own_category(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    category_id = create_category_record(client, "faith@example.com")

    response = client.get(f"/categories/{category_id}")

    assert response.status_code == 200
    assert response.json["name"] == "Work"


# Test that a user cannot view another user's category
def test_user_cannot_get_another_users_category(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    category_id = create_category_record(client, "user@example.com")
    login_user(client, "faith@example.com")

    response = client.get(f"/categories/{category_id}")

    assert response.status_code == 404


# Test that a user can update their own category
def test_update_own_category(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    category_id = create_category_record(client, "faith@example.com")

    response = client.patch(
        f"/categories/{category_id}",
        json={"name": "Personal"}
    )

    assert response.status_code == 200
    assert response.json["name"] == "Personal"


# Test that a user cannot update another user's category
def test_user_cannot_update_another_users_category(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    category_id = create_category_record(client, "user@example.com")
    login_user(client, "faith@example.com")

    response = client.patch(
        f"/categories/{category_id}",
        json={"name": "Changed"}
    )

    assert response.status_code == 404


# Test that a category cannot be updated with an empty name
def test_update_category_with_empty_name(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    category_id = create_category_record(client, "faith@example.com")

    response = client.patch(
        f"/categories/{category_id}",
        json={"name": "   "}
    )

    assert response.status_code == 422


# Test that a user can delete their own category
def test_delete_own_category(client):
    register_user(client, "faith123", "faith@example.com")
    login_user(client, "faith@example.com")
    category_id = create_category_record(client, "faith@example.com")

    response = client.delete(f"/categories/{category_id}")

    assert response.status_code == 204


# Test that a user cannot delete another user's category
def test_user_cannot_delete_another_users_category(client):
    register_user(client, "faith123", "faith@example.com")
    register_user(client, "user456", "user@example.com")
    category_id = create_category_record(client, "user@example.com")
    login_user(client, "faith@example.com")

    response = client.delete(f"/categories/{category_id}")

    assert response.status_code == 404


# Test that a user cannot delete a category without logging in
def test_delete_category_without_login(client):
    response = client.delete("/categories/1")

    assert response.status_code == 401