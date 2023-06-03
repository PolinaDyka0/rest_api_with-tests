from unittest.mock import MagicMock, patch
from src.schemas import ContactCreate
import pytest
from datetime import date
from fastapi.encoders import jsonable_encoder
from src.database.models import User
from src.services.auth import auth_service


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


def test_create_contact(client, token):
    # Arrange
    contact_data = ContactCreate(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='1234567890',
        birthday=date(1990, 1, 1),
        additional_info='Additional information'
    )

    # Serialize object to JSON
    contact_json = jsonable_encoder(contact_data)

    # Act
    response = client.post(
        "/contacts",
        json=contact_json,
        headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 200, response.text
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["phone"] == "1234567890"
    assert "id" in data

def test_get_contact(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "1234567890"
        assert "id" in data

def test_get_contact_not_found(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/contacts/999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text

def test_get_contacts(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "John"
        assert data[0]["last_name"] == "Doe"
        assert data[0]["email"] == "john.doe@example.com"
        assert data[0]["phone"] == "1234567890"
        assert "id" in data[0]

def test_update_contact(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/contacts/1",
            json={
                "first_name": "Updated",
                "last_name": "Contact",
                "email": "updated.contact@example.com",
                "phone": "9876543210",
                "birthday": "1990-01-02",
                "additional_info": "Updated information"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()

        # Assert the updated contact data
        assert "id" in data
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Contact"
        assert data["email"] == "updated.contact@example.com"
        assert data["phone"] == "9876543210"
        assert data["birthday"] == "1990-01-02"
        assert data["additional_info"] == "Updated information"

def test_update_contact_not_found(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/contacts/999",
            json={
                "first_name": "Updated",
                "last_name": "Contact",
                "email": "updated.contact@example.com",
                "phone": "9876543210",
                "birthday": "1990-01-02",
                "additional_info": "Updated information"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text


def test_delete_contact(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Contact"
        assert data["email"] == "updated.contact@example.com"
        assert data["phone"] == "9876543210"
        assert data["birthday"] == "1990-01-02"
        assert data["additional_info"] == "Updated information"
        assert "id" in data


def test_repeat_delete_contact(client, token):
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text

