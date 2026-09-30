from app.database.database import engine, Base
import app.models  # ensure models are imported

def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
