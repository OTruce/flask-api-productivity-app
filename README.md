# Workout Log API

A secure, session-authenticated Flask REST API for a personal workout-tracking
app. Each user can sign up, log in, and manage their own list of workouts —
create, view, update and delete entries. Users can never see or
modify another user's workouts.


**Live API:** `https://flask-api-productivity-app.onrender.com`

## Try it in a browser (optional frontend)

A small, plain HTML/JS page is bundled at `static/index.html` and served
directly at the root URL — no build step, no separate setup. It's the
easiest way to actually use the API: sign up or log in, then add, edit,
delete and page through your workouts, all from the browser.

Just open `http://localhost:5555/` locally after running it in the terminal, or prefarably the live Render URL provided above. The frontend is optional but is there so you don't have to test everything with curl or Postman, making interaction with the system a whole lot easier.

## Installation

1. Clone this repo and `cd` into it.
   ```bash
   git clone https://github.com/OTruce/flask-api-productivity-app
   ```
2. Install dependencies:
   ```bash
   pipenv install
   pipenv shell
   ```
3. Set up the local database:       # Note: Locally it uses different data compared to what the system uses while launched with Render
   ```bash
   export FLASK_APP=app.py     
   flask db upgrade
   ```

4. Seed the database with sample users and workouts:
   ```bash
   python seed.py
   ```
   This prints a sample username you can log in with (password for every
   seeded user is `password123`).

5. Running the Server
   ```bash
   python app.py
   ```
The API and the bundled frontend runs at `http://localhost:5555` instead of giving a JSON message.

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

## Deployment

This API is set up to deploy on Render using its free
web service and free PostgreSQL plans. 

### Setup For Firsttime
To deploy the project manually so that you can run it via the Render link that it provides:

1. **Create the database:** Render dashboard → **New > PostgreSQL** → copy
   the generated "Internal Database URL" and paste somewhere on a notepad.
2. **Create the web service:** **New > Web Service** → connect this GitHub
   repo or your own after cloning, then set:
   - **Build Command:** `pip install -r requirements.txt && flask db upgrade`
   - **Start Command:** `gunicorn app:app`
   - **Environment variables:**
     - `FLASK_APP` = `app.py`
     - `DATABASE_URL` = *(the Internal Database URL from step 1)*
     - `PYTHON_VERSION` = `3.11.9`
3. Deploy. Render installs dependencies, runs `flask db upgrade`, then starts the app.
4. (Optional) Seed sample data once, from the Render Shell tab on the web
   service: `python seed.py`.
5. Once the service is live, you can copy the link Render assigns to the service and access the system via the link in a different tab
   Also note that Render puts the service to sleep after 15 min of inactivity, and awakes it once it gets an attempt to start it which takes 20 to 40 seconds.

##NOTE: Be sure to select the free tiers when creating the database and web services on Render just for testing purposes

## Status Codes Used

- `200` OK
- `201` Created
- `204` No Content (logout, delete)
- `401` Unauthorized (not logged in)
- `403` Forbidden (logged in, but doesn't own the resource)
- `404` Not Found
- `422` Unprocessable Entity (validation errors)

### Author
Stephen Njenga