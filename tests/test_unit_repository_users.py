import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_password, update_avatar
from src.database.models import User
from src.schemas import UserModel


class UserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session())
        self.user = User(id=1)

    def test_get_user_by_email(self):
        # Arrange
        email = 'test@example.com'
        expected_user = User(email=email)

        self.session.query().filter().first.return_value = expected_user

        # Act
        user = get_user_by_email(email, self.session)

        # Assert
        self.assertEqual(user, expected_user)
        self.session.query().filter().first.assert_called_once_with()

    def test_create_user(self):
        # Arrange
        email = 'test@example.com'
        username = 'test_user'
        user_data = UserModel(email=email, username=username, password='password')
        avatar_url = 'https://example.com/avatar.jpg'

        g_mock = MagicMock()
        g_mock.get_image.return_value = avatar_url

        Gravatar_mock = MagicMock(return_value=g_mock)
        patcher = patch('src.repository.users.Gravatar', Gravatar_mock)
        patcher.start()

        # Act
        created_user = create_user(user_data, self.session)

        # Assert
        self.assertEqual(created_user.email, email)
        self.assertEqual(created_user.avatar, avatar_url)
        self.assertEqual(created_user.username, username)
        self.session.add.assert_called_once_with(created_user)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(created_user)

        patcher.stop()

    def test_update_token(self):
        # Arrange
        token = 'token123'

        # Act
        update_token(self.user, token, self.session)

        # Assert
        self.assertEqual(self.user.refresh_token, token)
        self.session.commit.assert_called_once()

    # def test_confirmed_email(self):
    #     # Arrange
    #     email = 'test@example.com'
    #
    #     self.session.commit.return_value = None
    #
    #     # Act
    #     confirmed_email(email, self.session)
    #
    #     # Assert
    #     self.assertTrue(self.user.confirmed)
    #     self.session.commit.assert_called_once()

    def test_update_avatar(self):
        # Arrange
        email = 'test@example.com'
        url = 'https://example.com/avatar.jpg'

        self.session.commit.return_value = None

        # Act
        user = update_avatar(email, url, self.session)

        # Assert
        self.assertEqual(user.avatar, url)
        self.session.commit.assert_called_once()

    def test_update_password(self):
        # Arrange
        new_password = 'new_password'

        # Act
        update_password(self.user, new_password, self.session)

        # Assert
        self.assertEqual(self.user.password, new_password)
        self.session.commit.assert_called_once()

    def test_confirmed_email(self):
        # Arrange
        email = 'test@example.com'
        self.user.confirmed = False
        self.session.commit.return_value = None

        # Act
        confirmed_email(email, self.session)

        # Assert
        self.user = self.session.query(User).filter_by(email=email).first()
        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()





if __name__ == '__main__':
    unittest.main()
