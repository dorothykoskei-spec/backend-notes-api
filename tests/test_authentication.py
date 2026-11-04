import pytest
from app import create_app
from extensions import db

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

def register_user(client):
    return client.post("/auth/register", json={
        "username": "faith123",
        "email": "faith@example.com",
        "password": "password123"
    })

# Test authentication endpoints
def test_register_user_successfully(client):
    response = register_user(client)

    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"
    assert response.json["user"]["username"] == "faith123"
    assert "password" not in response.json["user"]

def test_register_without_data(client):
    response = client.post("/auth/register", json={})

    assert response.status_code == 400

def test_register_duplicate_username(client):
    register_user(client)

    response = client.post("/auth/register", json={
        "username": "faith123",
        "email": "another@example.com",
        "password": "password123"
    })

    assert response.status_code == 400
    assert response.json["error"] == "Username or email already exists"

def test_register_duplicate_email(client):
    register_user(client)

    response = client.post("/auth/register", json={
        "username": "anotheruser",
        "email": "faith@example.com",
        "password": "password123"
    })

    assert response.status_code == 400
    assert response.json["error"] == "Username or email already exists"

def test_login_successfully(client):
    register_user(client)

    response = client.post("/auth/login", json={
        "email": "faith@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    assert response.json["message"] == "Login successful"
    assert "password" not in response.json["user"]

def test_login_with_wrong_password(client):
    register_user(client)

    response = client.post("/auth/login", json={
        "email": "faith@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json["error"] == "Invalid email or password"

def test_login_with_unknown_email(client):
    response = client.post("/auth/login", json={
        "email": "unknown@example.com",
        "password": "password123"
    })

    assert response.status_code == 401

def test_login_without_credentials(client):
    response = client.post("/auth/login", json={
        "email": "faith@example.com"
    })

    assert response.status_code == 400

def test_current_user_without_login(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json["error"] == "Please log in first"

def test_current_user_after_login(client):
    register_user(client)

    client.post("/auth/login", json={
        "email": "faith@example.com",
        "password": "password123"
    })

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json["user"]["username"] == "faith123"

def test_logout_successfully(client):
    register_user(client)

    client.post("/auth/login", json={
        "email": "faith@example.com",
        "password": "password123"
    })

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json["message"] == "Logout successful"

    response = client.get("/auth/me")

    assert response.status_code == 401