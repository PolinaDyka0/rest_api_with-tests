import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status


from src.routes.auth import confirmed_email


@pytest.fixture
def mock_get_email_from_token(monkeypatch):
    mock = MagicMock(return_value="test@example.com")
    monkeypatch.setattr("src.routes.auth.auth_service.get_email_from_token", mock)
    return mock


@pytest.fixture
def mock_get_user_by_email(monkeypatch):
    mock = MagicMock(return_value=None)
    monkeypatch.setattr("src.routes.auth.repository_users.get_user_by_email", mock)
    return mock


@pytest.fixture
def mock_confirmed_email(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("src.routes.auth.repository_users.confirmed_email", mock)
    return mock


def test_confirmed_email_user_not_found(mock_get_email_from_token, mock_get_user_by_email):
    with pytest.raises(Exception) as exc:
        confirmed_email("test_token")
    assert type(exc.value) == HTTPException
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Verification error"



def test_confirmed_email_already_confirmed(mock_get_email_from_token, mock_get_user_by_email):
    mock_get_user_by_email.return_value = MagicMock(confirmed=True)
    response = confirmed_email("test_token")
    assert response == {"message": "Your email is already confirmed"}


def test_confirmed_email_success(mock_get_email_from_token, mock_get_user_by_email, mock_confirmed_email):
    user = MagicMock(confirmed=False)
    mock_get_user_by_email.return_value = user
    response = confirmed_email("test_token", db=None)
    assert response == {"message": "Email confirmed"}
    mock_confirmed_email.assert_called_once_with("test@example.com", None)


