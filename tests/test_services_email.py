
from unittest.mock import patch
from src.services.auth import auth_service, repository_users


from fastapi import status

def test_update_password_success(client):
    with patch.object(auth_service, "get_email_from_token", return_value="test@example.com"):
        with patch.object(repository_users, "get_user_by_email", return_value=True):
            with patch.object(repository_users, "update_password") as mock_update_password:
                response = client.post(
                    "/auth/update_password/test_token",
                    data={"new_password": "new_password"}
                )
                assert response.status_code == status.HTTP_200_OK
                assert response.json() == {"message": "Password has been updated successfully"}
                mock_update_password.assert_called_once()

def test_update_password_invalid_token_or_user_not_found(client):
    with patch.object(auth_service, "get_email_from_token", return_value="test@example.com"):
        with patch.object(repository_users, "get_user_by_email", return_value=False):
            response = client.post(
                "/auth/update_password/invalid_token",
                data={"new_password": "new_password"}
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": "Invalid token or user not found"}


