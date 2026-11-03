from config import db
from models.user import User
from models.categories import Category
from models.note import Note

# TEMPORARY: confirm tomorrow how the app is created in app.py
from app import app


def clear_data():
    # Delete in this order: notes depend on categories, categories depend on users
    Note.query.delete()
    Category.query.delete()
    User.query.delete()
    db.session.commit()


def seed_users():
    users = [
        User(username="amara_cole", email="amara.cole@example.com", password="password123"),
        User(username="jonas_reed", email="jonas.reed@example.com", password="password123"),
        User(username="lina_ortiz", email="lina.ortiz@example.com", password="password123"),
    ]

    db.session.add_all(users)
    db.session.commit()
    return users


def seed_categories(users):
    names = ["Work", "School", "Personal"]
    categories = []

    for user in users:
        for name in names:
            category = Category(name=name, user_id=user.id)
            db.session.add(category)
            categories.append(category)

    db.session.commit()
    return categories


def seed_notes(categories):
    notes = []

    for category in categories:
        for number in range(1, 4):
            note = Note(
                title=f"{category.name} note {number}",
                content=f"Sample content for {category.name} note {number}.",
                user_id=category.user_id,
                category_id=category.id,
            )
            db.session.add(note)
            notes.append(note)

    db.session.commit()
    return notes


if __name__ == "__main__":
    with app.app_context():
        clear_data()
        users = seed_users()
        categories = seed_categories(users)
        notes = seed_notes(categories)
        print(f"Seeded {len(users)} users, {len(categories)} categories, {len(notes)} notes.")