from app.db import engine, Base
from app import models  # Ensure models are registered

Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
