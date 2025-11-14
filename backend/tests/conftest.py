import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import create_app  # noqa: E402
from app.db import Base  # noqa: E402
from app.dependencies import get_db  # noqa: E402
from app.models import User, UserStats  # noqa: E402
from app.security import hash_password  # noqa: E402


@pytest.fixture(scope="session")
def test_engine():
	engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
	Base.metadata.create_all(bind=engine)
	return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
	Session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
	session = Session()
	try:
		yield session
	finally:
		session.close()


@pytest.fixture(scope="function")
def test_client(db_session):
	app = create_app()

	def override_get_db():
		try:
			yield db_session
		finally:
			pass

	app.dependency_overrides[get_db] = override_get_db

	test_user = User(
		name="Test User",
		email="test@example.com",
		password_hash=hash_password("password123"),
	)
	db_session.add(test_user)
	db_session.flush()
	stats = UserStats(user_id=test_user.id)
	db_session.add(stats)
	db_session.commit()

	def override_current_user():
		return test_user

	from app.dependencies import get_current_user

	app.dependency_overrides[get_current_user] = override_current_user
	return TestClient(app)


@pytest.fixture
def current_user(db_session):
	return db_session.query(User).first()

