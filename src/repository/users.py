from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from typing import Optional



def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email. If no such user exists, it returns None.

    :param email: str: Specify the type of the parameter
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    return db.query(User).filter(User.email == email).first()


def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Define the data that will be used to create a new user
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Failed to get Gravatar image: {e}")
        avatar = None

    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: User, token: Optional[str], db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user
    :param token: Optional[str]: Pass in the token that is returned from the spotify api
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user.refresh_token = token
    db.commit()


def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session.
    It then gets the user by their email, sets their confirmed status to True,
    and commits the changes to the database.

    :param email: str: Specify the email of the user to be confirmed
    :param db: Session: Pass in the database session to the function
    :return: None
        """
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that will be passed to the function
    :param db: Session: Pass the database session to the function
    :return: The user object, which is a row in the users table
    """
    user = get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

def update_password(user: User, new_password: str, db: Session):
    """
    The update_password function takes in a user object, new_password string, and db session.
    It then updates the password of the user object to be equal to the new_password string.
    Finally it commits this change to the database.

    :param user: User: Specify that the user parameter is of type user
    :param new_password: str: Pass in the new password to be set
    :param db: Session: Pass in the database session to the function
    :return: None
    """
    user.password = new_password
    db.commit()
