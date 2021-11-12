import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Userdb.query.get(int(user_id))


class Userdb(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return "<Userdb %r>" % self.username


class Expensedb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("userdb.id"), nullable=False)

    def __repr__(self):
        return "<Expensedb %r>" % self.expense


class Budgetdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("userdb.id"), nullable=False)

    def __repr__(self):
        return "<Artistdb %r>" % self.budget
