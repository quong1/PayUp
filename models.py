from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin

load_dotenv(find_dotenv())
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="./build/static")
# Point SQLAlchemy to your Heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = b"I am a secret key"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bp = Blueprint("bp", __name__, template_folder="./build")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class Userdb(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return Userdb.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


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
