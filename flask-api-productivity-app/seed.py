from random import choice, randint

from faker import Faker

from config import app, db
from models import User, Workout

fake = Faker()

WORKOUT_TITLES = [
    "Leg Day",
    "Upper Body Push",
    "Upper Body Pull",
    "Cardio Blast",
    "Core Crusher",
    "Full Body Circuit",
    "Rest Day Stretch",
    "HIIT Session",
    "Long Run",
    "Yoga Flow",
]

if __name__ == "__main__":
    with app.app_context():
        print("Clearing db...")
        Workout.query.delete()
        User.query.delete()
        db.session.commit()

        print("Seeding users...")
        users = []
        for _ in range(5):
            user = User(username=fake.unique.user_name())
            user.password_hash = "password123"
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        print("Seeding workouts...")
        workouts = []
        for _ in range(30):
            workout = Workout(
                title=choice(WORKOUT_TITLES),
                description=fake.sentence(nb_words=10),
                duration_minutes=randint(15, 90),
                user_id=choice(users).id,
            )
            workouts.append(workout)
        db.session.add_all(workouts)
        db.session.commit()

        print(f"Seeding complete! Created {len(users)} users and {len(workouts)} workouts.")
        print("Sample login -> username:", users[0].username, "| password: password123")
