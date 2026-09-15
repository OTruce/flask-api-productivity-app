# Workout Log API

A secure, session-authenticated Flask REST API for a personal workout-tracking
app. Each user can sign up, log in, and manage their own list of workouts —
create, view (paginated), update, and delete entries. Users can never see or
modify another user's workouts.

Built for the "Full Auth Flask Backend" summative lab. The frontend (JWT and
session client versions) is provided separately; this repo is the backend
only, built to support the **session-based** client.

**Live API:** `<PASTE YOUR RENDER URL HERE, e.g. https://workout-log-api.onrender.com>`
_(Also add this same link to the "Website" field of this repo's GitHub "About" section — see [Deployment](#deployment) below.)_

## Tech Stack

- Flask + Flask-RESTful — routing / REST resources
- Flask-SQLAlchemy — ORM / models
- Flask-Migrate (Alembic) — database migrations
- Flask-Bcrypt — password hashing
- Flask-CORS — cross-origin session cookies for the separate frontend client
- Faker — seed data generation
- SQLite (dev) / PostgreSQL (production, e.g. on Render) — `config.py` picks
  whichever `DATABASE_URL`/`DATABASE_URI` env var is set, falling back to a
  local SQLite file
- Gunicorn — production WSGI server (used when deployed)

## Project Structure

```
flask-workout-api/
├── app.py              # Flask app + all RESTful resources/routes + serves the bonus frontend
├── config.py           # App config, extension instances (db, bcrypt, migrate, api, CORS)
├── models.py           # User and Workout SQLAlchemy models
├── seed.py             # Seeds the database with fake users + workouts
├── static/
│   └── index.html       # Optional, ungraded bonus frontend (plain HTML/CSS/JS)
├── Pipfile              # Dependencies (local dev, via pipenv)
├── requirements.txt      # Same dependencies, pip-installable (used by Render's build)
├── Procfile              # Tells the host how to start the server (gunicorn)
├── render.yaml           # Render Blueprint — optional one-click infra-as-code deploy
├── migrations/          # Flask-Migrate/Alembic migration history
└── README.md
```

## Installation

1. Clone this repo and `cd` into it.
2. Install dependencies:
   ```bash
   pipenv install
   pipenv shell
   ```
3. Set up the database:
   ```bash
   export FLASK_APP=app.py      # Windows (cmd): set FLASK_APP=app.py
   flask db upgrade
   ```
   (The `migrations/` folder is already included, so `flask db upgrade` alone
   will create `app.db` with the correct schema. If you ever need to
   regenerate migrations from scratch, delete `migrations/` and `app.db`,
   then run `flask db init && flask db migrate -m "Initial migration" && flask db upgrade`.)
4. Seed the database with sample users and workouts:
   ```bash
   python seed.py
   ```
   This prints a sample username you can use to log in (password for every
   seeded user is `password123`).

## Running the Server

```bash
python app.py
```

The API runs at `http://localhost:5555`.

If you're running the provided session-based frontend client on a different
port (e.g. `http://localhost:3000`), make sure requests from the client are
sent with `credentials: "include"` so the session cookie is stored/sent
correctly. The allowed CORS origins are configured in `config.py`.

## Authentication

Auth is **session-based** (a server-side cookie), not JWT. Passwords are
hashed with `bcrypt` before being stored — the plaintext password is never
saved.

| Method | Route      | Description                                              |
|--------|------------|------------------------------------------------------------|
| POST   | `/signup`  | Create a new user (`username`, `password`) and log them in |
| POST   | `/login`   | Log in an existing user (`username`, `password`)           |
| DELETE | `/logout`  | Log out the current user, clearing the session              |
| GET    | `/me`      | Return the currently logged-in user, or `401` if none       |

## Workout Endpoints (protected — auth required)

Every route below requires an active session. Unauthenticated requests
return `401 { "error": "Not authorized" }`. Attempting to update or delete a
workout you don't own returns `403 { "error": "Not authorized" }`.

| Method | Route             | Description                                          |
|--------|-------------------|-------------------------------------------------------|
| GET    | `/workouts`       | Paginated list of **the current user's** workouts. Query params: `page` (default `1`), `per_page` (default `10`, max `100`). |
| POST   | `/workouts`       | Create a new workout owned by the current user. Body: `title`, `description` (optional), `duration_minutes`. |
| PATCH  | `/workouts/<id>`  | Update a workout you own. Body: any of `title`, `description`, `duration_minutes`. |
| DELETE | `/workouts/<id>`  | Delete a workout you own.                              |

### `GET /workouts` response shape

```json
{
  "workouts": [
    { "id": 1, "title": "Leg Day", "description": "Squats and lunges", "duration_minutes": 45, "date_logged": "2026-09-11", "user_id": 3 }
  ],
  "page": 1,
  "per_page": 10,
  "total_items": 27,
  "total_pages": 3
}
```

## Data Models

**User**
- `id`
- `username` (unique, required)
- `password_hash` (write-only; hashed with bcrypt, never exposed via `to_dict`)

**Workout** (belongs to a `User`)
- `id`
- `title` (required)
- `description`
- `duration_minutes` (required, must be a positive integer)
- `date_logged` (defaults to today)
- `user_id` (foreign key to `User`)

## Bonus: Bundled Frontend (optional, ungraded)

Per the lab instructions ("you can develop the frontend further ... but you
will only be graded on your backend Flask API"), there's a small, plain
HTML/CSS/JS page at `static/index.html` that Flask serves directly at `/`.
It's not a framework app — no build step, no npm install — just one
self-contained file that talks to this same Flask app's endpoints (login,
signup, logout, and full workout CRUD with pagination), so it works
identically locally and on Render with no extra CORS setup, since it's
served from the same origin as the API.

Once the server is running (locally or on Render), just open the root URL
in a browser — `http://localhost:5555/` locally, or your Render URL — and
you'll get a login/signup screen followed by a workout list you can add to,
edit, delete, and page through.

This is separate from, and does not replace, the dedicated JWT/session
frontend client provided with the lab — use that one if you need the
full-featured reference client.

## Deployment

This API is set up to deploy on [Render](https://render.com) using its free
web service + free PostgreSQL plans. (SQLite is dev-only — Render's
filesystem isn't persistent between deploys, so production uses Postgres via
`DATABASE_URL`, which `config.py` already reads automatically.)

### Option A — Blueprint (one click)

1. Push this repo to GitHub.
2. In the Render dashboard, click **New > Blueprint**, and point it at your
   repo. Render will read `render.yaml` and provision both the web service
   and the Postgres database automatically, wiring `DATABASE_URL` and a
   random `SECRET_KEY` for you.
3. Once it deploys, open **Environment** on the web service and set
   `CORS_ORIGINS` to your deployed frontend's URL (comma-separate multiple
   origins if needed).

### Option B — Manual setup

1. **Create the database:** Render dashboard → **New > PostgreSQL** → note
   the generated "Internal Database URL".
2. **Create the web service:** **New > Web Service** → connect this GitHub
   repo, then set:
   - **Build Command:** `pip install -r requirements.txt && flask db upgrade`
   - **Start Command:** `gunicorn app:app`
   - **Environment variables:**
     - `FLASK_APP` = `app.py`
     - `DATABASE_URL` = *(the Internal Database URL from step 1)*
     - `SECRET_KEY` = *(any long random string)*
     - `CORS_ORIGINS` = *(your deployed frontend's URL, e.g. `https://your-frontend.vercel.app`)*
     - `PYTHON_VERSION` = `3.11.9`
3. Deploy. Render will install dependencies, run `flask db upgrade` (applying
   the migrations already committed in `migrations/`), then start the app
   with gunicorn.
4. (Optional) Seed production data once, from the Render Shell tab on the
   web service: `python seed.py`.

### After deploying

1. Copy the live URL Render gives your service (e.g.
   `https://workout-log-api.onrender.com`).
2. Paste it into this README where indicated above.
3. Also add it to the repo's GitHub **About** panel: on the repo's main page,
   click the ⚙️ gear icon next to "About" → paste the URL into the
   **Website** field → **Save changes**. This is what makes the live link
   show up on the repository's information page, per the submission
   requirements.
4. Commit and push the README update.

### Notes on cross-origin sessions

Because the frontend and backend are typically deployed to two different
domains, `config.py` automatically switches cookies to
`SESSION_COOKIE_SAMESITE=None` and `SESSION_COOKIE_SECURE=True` when running
on Render (or when `FLASK_ENV=production`), so the session cookie is
correctly sent/stored across origins over HTTPS. Locally, cookies stay
`SameSite=Lax` / non-Secure so everything still works over plain `http`.

## Status Codes Used

- `200` OK
- `201` Created
- `204` No Content (logout, delete)
- `401` Unauthorized (not logged in)
- `403` Forbidden (logged in, but doesn't own the resource)
- `404` Not Found
- `422` Unprocessable Entity (validation errors, e.g. duplicate username, bad duration)
