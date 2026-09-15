from app import create_app, db, perform_seeding

app = create_app()

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        perform_seeding()

if __name__ == "__main__":
    init_db()
