from config import db, bcrypt

class User(db.Model):
  _tablename_ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.password = bcrypt.generate_password_hash(password).decode('utf-8')

  def set_password(self,password):
    self.password = bcrypt.generate_password_hash(password).decode('utf-8')

  def check_password(self, password):
    return bcrypt.check_password_hash(self.password, password)
