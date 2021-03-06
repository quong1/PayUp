"""
PayUp
"""
# pylint: disable=invalid-name
# pylint: disable=no-member
# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use
import os
import secrets
import flask
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    Flask,
)
from flask_bcrypt import Bcrypt
from PIL import Image

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_mail import Mail, Message

from flask_login import (
    login_user,
    current_user,
    logout_user,
    login_required,
    LoginManager,
    UserMixin,
)
from dotenv import load_dotenv, find_dotenv
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

load_dotenv(find_dotenv())

app = Flask(__name__, static_folder="./static")
# Point SQLAlchemy to your Heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASSWD")
mail = Mail(app)


@login_manager.user_loader
def load_user(username):
    """Get the current user username"""
    return Userdb.query.get(username)


class RegistrationForm(FlaskForm):
    """Form for user to SignUp"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        """
        Check if username match with any username in the database.
        If so, prompt user to choose a different one
        """
        user = Userdb.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        """
        Check if email match with any email in the database.
        If so, prompt user to choose a different one
        """
        user = Userdb.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    """Form for user to Login"""

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    """Form where user can customize and update their account"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        """
        Check if username match with any username in the database.
        If so, prompt user to choose a different one
        """
        if username.data != current_user.username:
            user = Userdb.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    def validate_email(self, email):
        """
        Check if email match with any email in the database.
        If so, prompt user to choose a different one
        """
        if email.data != current_user.email:
            user = Userdb.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )


class RequestResetForm(FlaskForm):
    """Form for user to request password reset"""

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        """
        Check if email is in the database.
        If not, prompt user to register
        """
        user = Userdb.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "There is no account with that email. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    """Form for user to change and verify the password"""

    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")


class BudgetForm(FlaskForm):
    """Form for the user to add the budget"""

    budget = DecimalField("Budget", validators=[DataRequired()])
    submit = SubmitField("Add")


class ExpensesForm(FlaskForm):
    """Form for user to add the expenses and price"""

    expense = StringField("Expense", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    submit = SubmitField("Add")


class Userdb(db.Model, UserMixin):
    """Set up User database table"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.png")
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=3600):
        """Generate a reset token for 1 hour"""
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        """
        Check if token is appropriate.
        Inappropriate token will not reset the password
        """
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:  # pylint: disable=bare-except
            return None
        return Userdb.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Expensedb(db.Model):
    """
    Set up database for expenses based on user
    """

    id = db.Column(db.Integer, primary_key=True)
    expense = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("userdb.id"), nullable=False)

    def __repr__(self):
        return "<Expensedb %r>" % self.expense


class Budgetdb(db.Model):
    """
    Set up database for Budget based on user
    """

    id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("userdb.id"), nullable=False)

    def __repr__(self):
        return "<Artistdb %r>" % self.budget


@app.route("/")
def index():
    payup_image = url_for("static", filename="image/Payup.png")
    csv_image = url_for("static", filename="image/csv.jpg")
    table_image = url_for("static", filename="image/table.png")
    M_image = url_for("static", filename="image/M.jpg")
    Z_image = url_for("static", filename="image/zi.png")
    J_image = url_for("static", filename="image/j.png")
    S_image = url_for("static", filename="image/default.png")

    return render_template(
        "about.html",
        payup_image=payup_image,
        csv_image=csv_image,
        table_image=table_image,
        M_image=M_image,
        Z_image=Z_image,
        J_image=J_image,
        S_image=S_image,
        title="About",
    )


@app.route("/home", methods=["GET", "POST"])
def home():
    """
    Check if current user is aunthenticated.
    If so, get user budget and expenses from database.
    Render it to home.html.
    If not, redirect user to login page
    """
    db.create_all()
    if current_user.is_authenticated:
        username = current_user.username
        user_id = current_user.id
        form = ExpensesForm()
        expenses = Expensedb.query.filter_by(user_id=user_id).all()
        used = sum(map(lambda x: x.price, expenses))
        image_file = url_for(
            "static", filename="profile_pics/" + current_user.image_file
        )
        budget = (
            Budgetdb.query.order_by(Budgetdb.id.desc())
            .filter_by(user_id=user_id)
            .first()
        )
        return render_template(
            "home.html",
            username=username,
            expenses=expenses,
            budget=budget,
            used=used,
            form=form,
            user_id=user_id,
            image_file=image_file,
        )
    return redirect(url_for("login"))


@app.route("/about")
def about():
    payup_image = url_for("static", filename="image/Payup.png")
    csv_image = url_for("static", filename="image/csv.jpg")
    table_image = url_for("static", filename="image/table.png")
    M_image = url_for("static", filename="image/M.jpg")
    Z_image = url_for("static", filename="image/zi.png")
    J_image = url_for("static", filename="image/j.png")
    S_image = url_for("static", filename="image/default.png")

    return render_template(
        "about.html",
        payup_image=payup_image,
        csv_image=csv_image,
        table_image=table_image,
        M_image=M_image,
        Z_image=Z_image,
        J_image=J_image,
        S_image=S_image,
        title="About",
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    If current user is authenticated, redirect to home page
    If user's input valid on the registration form,
    add username, email, and password to the database.
    redirect user to login page to login again.
    If user is not authenticated, redirect to register page
    """
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
    """
    If current user is authenticated, redirect to home page.
    From user input, check database for existing email and password.
    If valid, redirect to home page.
    If not, prompt user to login again
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Userdb.query.filter_by(email=form.email.data).first()
        # pylint: disable=no-else-return
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    """
    Log user out and redirect to login page
    """
    logout_user()
    return redirect(url_for("login"))


def save_picture(form_picture):
    """
    Let user save the changed picture
    """
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
    """
    Let user update the account and save it
    """
    form = UpdateAccountForm()
    # pylint: disable=no-else-return
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file  # pylint: disable=assigning-non-slot
        current_user.username = form.username.data  # pylint: disable=assigning-non-slot
        current_user.email = form.email.data  # pylint: disable=assigning-non-slot
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
    """
    Send user link to reset password
    """
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request",
        sender="payupnoreply@gmail.com",
        recipients=[user.email],
    )
    msg.body = f"""You have requested to reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If it is not you, please ignore this email!
"""
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    """
    Form for user to reset password
    """
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
    """
    Check if token is valid for user to reset password
    """
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


@app.route("/saveBudget", methods=["POST"])
def save_budget():
    """
    Get user input from budget form.
    If user's input is valid,
    Add the input and store it to the user's budget database.
    Refresh the page.
    """
    form = BudgetForm()
    user_id = current_user.id
    if form.validate_on_submit():
        budget = flask.request.form.get("budget")
        db.session.add(Budgetdb(budget=budget, user_id=user_id))
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/saveExpense", methods=["POST"])
def save_expense():
    """
    Get user input from expenses form.
    If user's input is valid,
    Add the input and store it to the user's expenses database.
    Refresh the page.
    """
    form = ExpensesForm()
    user_id = current_user.id
    if form.validate_on_submit():
        expense = flask.request.form.get("expense")
        price = flask.request.form.get("price")
        db.session.add(Expensedb(expense=expense, price=price, user_id=user_id))
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<expense_id>", methods=["POST"])
def delete(expense_id):
    """
    Let user delete expenses
    """
    Expensedb.query.filter_by(id=expense_id).delete()
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete_all", methods=["POST"])
def delete_all():
    """
    Allows user to delete all expenses
    """
    engine = create_engine(os.getenv("DATABASE_URL"))
    Expensedb.__table__.drop(engine)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/reset_budget", methods=["POST"])
def reset_budget():
    """
    Allows user to reset budget value
    """
    engine = create_engine(os.getenv("DATABASE_URL"))
    Budgetdb.__table__.drop(engine)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"),
        port=int(os.getenv("PORT", "8081")),
        debug=True,
    )
