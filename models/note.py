
import datetime

db = SQLAlchemy()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates


class Note (db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='notes', lazy=True)

    def __repr__(self):
        return f'<Note {self.title}>'


    