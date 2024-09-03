from app import app
from models import db, User

def init():
    with app.app_context():
        db.create_all() # Create tables

        # Check if the main user already exists
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin")
            admin.setPassword("admin")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    init()
