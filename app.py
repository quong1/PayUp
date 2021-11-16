import os
import flask
import secrets
from flask import render_template, url_for, flash, redirect, request, Flask, Blueprint
from flask_bcrypt import Bcrypt
from PIL import Image

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed

from flask_login import (
    login_user,
    current_user,
    logout_user,
    login_required,
    LoginManager,
    UserMixin,
)
from dotenv import load_dotenv, find_dotenv
from flask_mail import Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_sqlalchemy import SQLAlchemy

load_dotenv(find_dotenv())

app = Flask(__name__, static_folder="./static")
# Point SQLAlchemy to your Heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = b"I am a secret key"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    user_id = current_user.id
    form = ExpensesForm()
    expenses = Expensedb.query.all()
    used = sum(map(lambda x: x.price, expenses))
    budget = Budgetdb.query.order_by(Budgetdb.id.desc()).first()
    return render_template(
        "home.html",
        expenses=expenses,
        budget=budget,
        used=used,
        form=form,
        user_id=user_id,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = Userdb(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Userdb.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join("static/profile_pics", picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Userdb.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = Userdb.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)


@app.route("/")
def main():

    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@login_manager.user_loader
def load_user(username):
    return Userdb.query.get(username)


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    # noinspection PyMethodMayBeStatic
    def validate_username(self, username):
        user = Userdb.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    # noinspection PyMethodMayBeStatic
    def validate_email(self, email):
        user = Userdb.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    # noinspection PyMethodMayBeStatic
    def validate_username(self, username):
        if username.data != current_user.username:
            user = Userdb.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    # noinspection PyMethodMayBeStatic
    def validate_email(self, email):
        if email.data != current_user.email:
            user = Userdb.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    # noinspection PyMethodMayBeStatic
    def validate_email(self, email):
        user = Userdb.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "There is no account with that email. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")


class ExpensesForm(FlaskForm):
    expense = StringField("Expense", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    submit = SubmitField("Add")


class BudgetForm(FlaskForm):
    budget = DecimalField("Budget", validators=[DataRequired()])
    submit = SubmitField("Add")


class Userdb(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.png")
    password = db.Column(db.String(60), nullable=False)

    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(app.config["SECRET_KEY"], expires_sec)
    #     return s.dumps({"user_id": self.id}).decode("utf-8")
    #
    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer(app.config["SECRET_KEY"])
    #     try:
    #         user_id = s.loads(token)["user_id"]
    #     except:
    #         return None
    #     return Userdb.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Expensedb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("userdb.id"), nullable=False)

    def __repr__(self):
        return "<Expensedb %r>" % self.expense


class Budgetdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("userdb.id"), nullable=False)

    def __repr__(self):
        return "<Artistdb %r>" % self.budget


@app.route("/saveBudget", methods=["POST"])
def save_budget():
    form = BudgetForm()
    user_id = current_user.id
    if form.validate_on_submit():
        budget = flask.request.form.get("budget")
        db.session.add(Budgetdb(budget=budget, user_id=user_id))
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("home.html", form=form)


@app.route("/saveExpense", methods=["POST"])
def save_expense():
    form = ExpensesForm()
    user_id = current_user.id
    if form.validate_on_submit():
        expense = flask.request.form.get("expense")
        price = flask.request.form.get("price")
        db.session.add(Expensedb(expense=expense, price=price, user_id=user_id))
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("home.html", form=form)


@app.route("/delete/<expense_id>", methods=["POST"])
def delete(expense_id):
    Expensedb.query.filter_by(id=expense_id).delete()
    db.session.commit()
    return redirect(url_for("home"))


db.create_all()


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"),
        port=int(os.getenv("PORT", "8081")),
    )
