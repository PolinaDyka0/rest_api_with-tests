from typing import List
from datetime import datetime, date, timedelta

from sqlalchemy.orm import Session

from sqlalchemy import or_, extract
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate, ContactBirthday


def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param user: User: Filter the contacts by user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user: User) -> Contact:
    """
    The get_contact function takes in a database session, contact_id, and user.
    It then queries the database for a Contact with the given id and user_id.
    If it finds one, it returns that Contact object.

    :param db: Session: Pass the database session to the function
    :param contact_id: int: Specify the contact id
    :param user: User: Ensure that the user is logged in and has access to the contact
    :return: A contact object
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()


def create_contact(db: Session, contact: ContactCreate, user: User) -> Contact:
    """
    The create_contact function creates a new contact in the database.
        Args:
            db (Session): The SQLAlchemy session object.
            contact (ContactCreate): The ContactCreate schema model to be created in the database.
            user (User): The User schema model that is creating this contact, used for foreign key relationship with contacts table.

    :param db: Session: Access the database
    :param contact: ContactCreate: Create a new contact
    :param user: User: Get the user id from the user object
    :return: The newly created contact
    """
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user: User) -> Contact:
    """
    The update_contact function updates a contact in the database.

    :param db: Session: Access the database
    :param contact_id: int: Find the contact in the database
    :param contact: ContactUpdate: Get the data from the request body
    :param user: User: Ensure that the user is only able to update their own contacts
    :return: The updated contact
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not db_contact:
        raise ValueError("Contact not found")
    for field, value in contact.dict(exclude_unset=True).items():
        setattr(db_contact, field, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user: User) -> Contact:
    """
    The delete_contact function deletes a contact from the database.
        Args:
            db (Session): The database session to use for querying.
            contact_id (int): The id of the contact to delete.
            user (User): The user who is deleting the contact.

    :param db: Session: Pass the database session to the function
    :param contact_id: int: Specify the contact to delete
    :param user: User: Make sure that the user is authorized to delete the contact
    :return: The deleted contact
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not db_contact:
        raise ValueError("Contact not found")
    db.delete(db_contact)
    db.commit()
    return db_contact


def search_contacts(db: Session, query: str, user: User) -> List[Contact]:
    """
    The search_contacts function searches the database for contacts that match a given query.

    :param db: Session: Access the database
    :param query: str: Search for a contact by first name, last name or email
    :param user: User: Get the user id of the current user
    :return: A list of contacts that match the query
    """
    if not query:
        return []
    return db.query(Contact).filter(Contact.user_id == user.id).filter(or_(
        Contact.first_name.ilike(f"%{query}%"),
        Contact.last_name.ilike(f"%{query}%"),
        Contact.email.ilike(f"%{query}%"),
    )).all()


def get_contacts_with_birthdays(db: Session, user: User):
    """
    The get_contacts_with_birthdays function returns a list of contacts with birthdays in the next week.

    :param db: Session: Pass in the database session
    :param user: User: Get the user_id from the database
    :return: A list of contact objects
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).filter(Contact.user_id == user.id).filter(
        extract('month', Contact.birthday) == today.month,
        extract('day', Contact.birthday) >= today.day,
        extract('day', Contact.birthday) <= next_week.day
    ).all()
    return contacts
