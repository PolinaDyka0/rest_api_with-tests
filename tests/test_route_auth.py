from unittest.mock import MagicMock, patch
import pytest
from src.services.auth import auth_service
from src.database.models import User



@pytest.fixture
def mock_send_email(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock)
    return mock


def test_create_user(client, user, mock_send_email):
    response = client.post(
        "/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]
    mock_send_email.assert_called_once()


def test_repeat_create_user(client, user):
    response = client.post(
        "/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    response = client.post(
        "/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

def test_refresh_token(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    access_token = auth_service.create_access_token(data={"sub": user.get('email')})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.get('email')})  # Оновлений рядок
    current_user.refresh_token = refresh_token
    session.commit()
    headers = {"Authorization": f"Bearer {refresh_token}"}  # Оновлений рядок
    response = client.get("/auth/refresh_token", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

def test_refresh_token_invalid_token(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    access_token = auth_service.create_access_token(data={"sub": user.get('email')})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.get('email')})
    current_user.refresh_token = refresh_token
    session.commit()
    # Змінюємо refresh_token, щоб зробити його недійсним
    invalid_refresh_token = refresh_token + "invalid"
    headers = {"Authorization": f"Bearer {invalid_refresh_token}"}
    response = client.get("/auth/refresh_token", headers=headers)
    assert response.status_code == 401, response.text
    data = response.json()
    assert "Could not validate credentials" in data["detail"]

def test_request_reset_password(client, session, user, mock_send_email, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()

    def mock_send_email_mock(email, username, base_url):
        assert base_url == "http://testserver"
        assert email == user.get('email')
        assert username == user.get('username')

    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email_mock)

    response = client.post(
        "/auth/request_reset_password",
        json={"email": user.get('email')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


