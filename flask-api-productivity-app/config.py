import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Render (and most host providers) inject the Postgres connection string as
# DATABASE_URL. Older versions of that string use the "postgres://" scheme,
# which SQLAlchemy 1.4+ no longer accepts -- it must be "postgresql://".
# Locally, with no DATABASE_URL set, we fall back to a SQLite file so the
# app still runs with zero extra setup.
database_url = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_URI")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
if not database_url:
    database_url = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

# Render sets RENDER=true on every deployed service. We use that (or an
# explicit FLASK_ENV=production) to flip the app into "production mode":
# cookies become Secure + SameSite=None so a separately-hosted frontend
# (e.g. on Vercel/Netlify) can still send/receive the session cookie over
# HTTPS across origins. Locally over plain http this must stay off.
IS_PRODUCTION = bool(os.environ.get("RENDER")) or os.environ.get("FLASK_ENV") == "production"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SESSION_COOKIE_SAMESITE"] = "None" if IS_PRODUCTION else "Lax"
app.config["SESSION_COOKIE_SECURE"] = IS_PRODUCTION
app.json.compact = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

# Allow the frontend client (running on a different origin) to send/receive
# the session cookie. Set CORS_ORIGINS (comma-separated) in your deployment
# environment to the deployed frontend's URL(s); localhost ports are always
# included for local development.
_default_origins = ["http://localhost:3000", "http://localhost:4000", "http://127.0.0.1:3000"]
_env_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
CORS(app, supports_credentials=True, origins=_default_origins + _env_origins)
