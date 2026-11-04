# Backend Notes API

A RESTful API built with Flask that allows users to securely create, manage, organize, and retrieve personal notes. Users can register, log in, manage their notes, and organize them using categories.

## Features

- User registration and login.
- Session-based authentication and logout.
- Secure password hashing using Flask-Bcrypt.
- Protected routes that require authentication.
- User-specific notes and categories.
- Create, retrieve, update, and delete notes.
- Create, retrieve, update, and delete categories.
- Pagination when retrieving notes.
- Filter notes by category.
- Input validation using Marshmallow.
- Database migrations using Flask-Migrate.
- Automated tests using Pytest.

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- Flask-Marshmallow
- Marshmallow
- Flask-Migrate
- SQLite
- Pytest

## Project Structure

```text
backend-notes-api/
├── app.py
├── config.py
├── extensions.py
├── auth_helpers.py
├── seed.py
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── note.py
│   └── categories.py
├── schemas/
│   ├── user_schema.py
│   ├── note_schema.py
│   └── category_schema.py
├── routes/
│   ├── auth.py
│   ├── note.py
│   └── categories.py
├── migrations/
└── tests/
    ├── configtest.py
    ├── test_authentication.py
    ├── test_authorization.py
    ├── test_notes.py
    └── test_categories.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/dorothykoskei-spec/backend-notes-api.git
cd backend-notes-api
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Environment Variables

The application uses the following environment variables:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Secret key used by Flask for session security | `development-secret-key` |
| `DATABASE_URL` | Database connection URI | `sqlite:///notes.db` |

For local development, the application can run with the default SQLite database.

For a more secure setup, configure a strong secret key through the environment rather than using the development default.

Example:

```bash
export SECRET_KEY="your-secure-secret-key"
export DATABASE_URL="sqlite:///notes.db"
```

## Database Setup and Migrations

The project uses Flask-SQLAlchemy for database operations and Flask-Migrate for database migrations.

To apply the existing migrations:

```bash
python3 -m flask --app app db upgrade
```

If you make changes to the database models and need to create a new migration:

```bash
python3 -m flask --app app db migrate -m "Describe your changes"
python3 -m flask --app app db upgrade
```

## Seeding the Database

The project includes a seed script that creates sample users, categories, and notes.

Run:

```bash
python3 seed.py
```

The script creates:
- 3 sample users.
- 9 categories (3 per user).
- 27 sample notes.

**Warning:** The seed script clears existing notes, categories, and users before inserting sample data. Do not run it against a database containing data you want to keep.

Sample user credentials:

| Username | Email | Password |
|---|---|---|
| amara_cole | amara.cole@example.com | password123 |
| jonas_reed | jonas.reed@example.com | password123 |
| lina_ortiz | lina.ortiz@example.com | password123 |

These credentials are for development and testing only.

## Authentication

The API uses session-based authentication.

Users register and log in using their email and password. After a successful login, the user's ID is stored in the session. Protected endpoints require an authenticated session.

Passwords are hashed using Flask-Bcrypt and are not included in public user responses.

### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in |
| POST | `/auth/logout` | Log out |
| GET | `/auth/me` | Retrieve the currently logged-in user |

### Register a User

`POST /auth/register`

Request body:

```json
{
  "username": "faith123",
  "email": "faith@example.com",
  "password": "password123"
}
```

### Log In

`POST /auth/login`

Request body:

```json
{
  "email": "faith@example.com",
  "password": "password123"
}
```

### Log Out

`POST /auth/logout`

No request body is required.

### Get Current User

`GET /auth/me`

Returns the currently authenticated user's public information.

## Notes Endpoints

All note endpoints require authentication.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/notes` | Create a note |
| GET | `/notes` | Retrieve notes |
| GET | `/notes/<note_id>` | Retrieve one note |
| PATCH | `/notes/<note_id>` | Update a note |
| DELETE | `/notes/<note_id>` | Delete a note |

### Create a Note

`POST /notes`

Request body:

```json
{
  "title": "Learning Flask",
  "content": "Understanding Flask API development.",
  "category_id": 1
}
```

The `category_id` field is optional and can be `null`.

### Retrieve Notes

`GET /notes`

Notes can be retrieved using pagination and category filtering.

Query parameters:

| Parameter | Description | Default |
|---|---|---|
| `page` | Page number | 1 |
| `per_page` | Number of notes per page | 10 |
| `category_id` | Filter notes by category ID | None |

Example:

```text
GET /notes?page=1&per_page=10
```

Filter notes by category:

```text
GET /notes?category_id=1
```

Example response structure:

```json
{
  "notes": [],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_notes": 0,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

### Retrieve a Single Note

`GET /notes/1`

### Update a Note

`PATCH /notes/1`

Request body:

```json
{
  "title": "Updated Note Title",
  "content": "Updated note content."
}
```

Only the fields being updated need to be provided.

### Delete a Note

`DELETE /notes/1`

Returns a success message when the note is deleted.

## Categories Endpoints

All category endpoints require authentication.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/categories` | Create a category |
| GET | `/categories` | Retrieve all categories belonging to the user |
| GET | `/categories/<category_id>` | Retrieve one category |
| PATCH | `/categories/<category_id>` | Update a category |
| DELETE | `/categories/<category_id>` | Delete a category |

### Create a Category

`POST /categories`

Request body:

```json
{
  "name": "Work"
}
```

### Retrieve Categories

`GET /categories`

Returns the categories belonging to the authenticated user.

### Retrieve a Single Category

`GET /categories/1`

### Update a Category

`PATCH /categories/1`

Request body:

```json
{
  "name": "Personal"
}
```

### Delete a Category

`DELETE /categories/1`

Returns HTTP `204 No Content` when successful.

## Authorization and Data Protection

- Users can only access their own notes and categories.
- Protected routes return HTTP `401 Unauthorized` when a user is not logged in.
- Requests for notes or categories that do not belong to the authenticated user return HTTP `404 Not Found`.
- Passwords are hashed before storage.
- Marshmallow validates incoming user, note, and category data.

## Running the Application

Activate the virtual environment, then run:

```bash
python3 app.py
```

The application runs in Flask debug mode during development.

The root endpoint can be accessed at:

```text
GET /
```

It returns:

```json
{
  "message": "Backend Notes API is running!"
}
```

## Running Tests

The project uses Pytest for automated testing.

Run all discovered tests:

```bash
python3 -m pytest
```

To see the tests Pytest discovers without executing them:

```bash
python3 -m pytest --collect-only -q
```

The test suite includes authentication, authorization, notes, and categories tests.

## Contributors

This project was developed collaboratively as part of a Software Engineering learning project at Moringa School. The collaborators were:

1. Beatrice Kamoni
2. Dorothy Chemutai
3. Emmanuel Mwangi
4. Faith Kyungu
5. Kaitlyn Njeri