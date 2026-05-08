from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Yeh humari local SQLite database file ka naam hoga
SQLALCHEMY_DATABASE_URL = "sqlite:///./taskmanager.db"

# Engine banate hain jo DB se connect karega
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Yeh base class hai jisse humari tables banengi
Base = declarative_base()

# DB session get karne ka function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        