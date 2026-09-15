from flask import make_response, request, send_from_directory, session
from flask_restful import Resource

from config import api, app, db
from models import User, Workout


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


# Frontend + API info
@app.route("/")
def serve_frontend():
    
    return send_from_directory(app.static_folder, "index.html")


class ApiInfo(Resource):

    def get(self):
        return {
            "message": "Workout Log API is running.",
            "endpoints": [
                "POST /signup",
                "POST /login",
                "DELETE /logout",
                "GET /me",
                "GET /workouts",
                "POST /workouts",
                "PATCH /workouts/<id>",
                "DELETE /workouts/<id>",
            ],
        }, 200



# Auth resources

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Username and password are required"}, 422

        if User.query.filter_by(username=username).first():
            return {"error": "Username already taken"}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session["user_id"] = None
            return make_response("", 204)
        return {"error": "Not authorized"}, 401


class CheckSession(Resource):
    def get(self):
        user = current_user()
        if user:
            return user.to_dict(), 200
        return {"error": "Not authorized"}, 401


# Workout (resource) CRUD

class Workouts(Resource):
    def get(self):
        user = current_user()
        if not user:
            return {"error": "Not authorized"}, 401

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = max(1, min(per_page, 100))
        page = max(1, page)

        pagination = (
            Workout.query.filter_by(user_id=user.id)
            .order_by(Workout.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "workouts": [w.to_dict() for w in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
        }, 200

    def post(self):
        user = current_user()
        if not user:
            return {"error": "Not authorized"}, 401

        data = request.get_json() or {}
        try:
            workout = Workout(
                title=data.get("title"),
                description=data.get("description"),
                duration_minutes=data.get("duration_minutes"),
                user_id=user.id,
            )
            db.session.add(workout)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

        return workout.to_dict(), 201


class WorkoutByID(Resource):
    def _get_owned_workout(self, id, user):
        workout = Workout.query.get(id)
        if not workout:
            return None, ({"error": "Workout not found"}, 404)
        if workout.user_id != user.id:
            return None, ({"error": "Not authorized"}, 403)
        return workout, None

    def patch(self, id):
        user = current_user()
        if not user:
            return {"error": "Not authorized"}, 401

        workout, err = self._get_owned_workout(id, user)
        if err:
            return err

        data = request.get_json() or {}
        try:
            for attr in ("title", "description", "duration_minutes"):
                if attr in data:
                    setattr(workout, attr, data[attr])
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

        return workout.to_dict(), 200

    def delete(self, id):
        user = current_user()
        if not user:
            return {"error": "Not authorized"}, 401

        workout, err = self._get_owned_workout(id, user)
        if err:
            return err

        db.session.delete(workout)
        db.session.commit()
        return make_response("", 204)


api.add_resource(ApiInfo, "/api")
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/me")
api.add_resource(Workouts, "/workouts")
api.add_resource(WorkoutByID, "/workouts/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
