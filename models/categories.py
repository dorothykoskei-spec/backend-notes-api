from config import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="categories")

    # Turn this on once Beatrice adds category_id to the Note model
    # notes = db.relationship("Note", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"