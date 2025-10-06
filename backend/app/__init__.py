# app/__init__.py

from app.database import SessionLocal
from sqlalchemy import text

def test_users():
    with SessionLocal() as session:
        result = session.execute(text("SELECT * FROM users"))
        print(result.fetchall())

# only runs when explicitly executed
if __name__ == "__main__":
    test_users()
