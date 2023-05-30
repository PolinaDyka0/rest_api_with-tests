from unittest.mock import MagicMock, patch
from src.database.models import User

import pytest


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_read_users_me(client, token):
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)
    assert data["email"] == "deadpool@example.com"
    assert data["username"] == "deadpool"
    assert "id" in data


def test_update_avatar_user(client, token):
    avatar_url = "https://example.com/avatar.jpg"
    with patch("src.routes.users.cloudinary") as mock_cloudinary:
        mock_cloudinary.CloudinaryImage.return_value.build_url.return_value = avatar_url
        response = client.patch(
            "/users/avatar",
            files={"file": ("avatar.jpg", b"dummydata", "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "deadpool@example.com"
        assert data["username"] == "deadpool"
        assert "avatar" in data
