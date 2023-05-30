import unittest
from unittest.mock import MagicMock
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.repository.contacts import get_contacts, get_contact, create_contact, update_contact, delete_contact, search_contacts, get_contacts_with_birthdays
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


class ContactRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session())
        self.user = User(id=1)

    def test_search_contacts(self):
        # Arrange
        query = 'John'
        expected_contacts = [
            Contact(id=1, first_name='John', last_name='Doe'),
            Contact(id=2, first_name='Johnny', last_name='Johnson')
        ]
        self.session.query().filter().filter().all.return_value = expected_contacts

        # Act
        contacts = search_contacts(self.session, query, self.user)

        # Assert
        self.assertEqual(contacts, expected_contacts)
        self.session.query().filter().filter().all.assert_called_once_with()

    def test_search_contacts_not_found(self):
        # Arrange
        query = ''
        expected_contacts = []
        # Act
        contacts = search_contacts(self.session, query, self.user)
        # Assert
        self.assertEqual(contacts, expected_contacts)

    def test_get_contacts_with_birthdays(self):
        # Arrange
        today = date.today()
        next_week = today + timedelta(days=7)
        expected_contacts = [
            Contact(id=1, first_name='John', last_name='Doe', birthday=today),
            Contact(id=2, first_name='Jane', last_name='Smith', birthday=next_week)
        ]
        self.session.query().filter().filter().all.return_value = expected_contacts

        # Act
        contacts = get_contacts_with_birthdays(self.session, self.user)

        # Assert
        self.assertEqual(contacts, expected_contacts)
        self.session.query().filter().filter().all.assert_called_once_with()

    def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_create_contact(self):
        # Arrange
        contact_data = ContactCreate(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            birthday=date(1990, 1, 1),
            additional_info='Additional information'
        )
        created_contact = Contact(
            id=1,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            birthday=date(1990, 1, 1),
            additional_info='Additional information',
            user_id=1
        )
        self.session.add.side_effect = lambda obj: obj
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        # Act
        contact = create_contact(self.session, contact_data, self.user)

        # Assert
        self.assertEqual(contact.id, None)
        self.assertEqual(contact.first_name, created_contact.first_name)

    def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(ValueError):
            delete_contact(db=self.session, contact_id=1, user=self.user)

    def test_update_contact_found(self):
        contact_id = 1
        contact_data = ContactUpdate(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            birthday=date(1990, 1, 1),
            additional_info='Additional information',
        )

        existing_contact = Contact(
            id=1,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            birthday=date(1990, 1, 1),
            additional_info='Additional information',
            user_id=1
        )

        self.session.query().filter().first.return_value = existing_contact
        self.session.commit.return_value = None

        result = update_contact(self.session, contact_id, contact_data, self.user)

        self.assertEqual(result.id, existing_contact.id)
        self.assertEqual(result.first_name, contact_data.first_name)
        self.assertEqual(result.last_name, contact_data.last_name)
        self.assertEqual(result.email, contact_data.email)
        self.assertEqual(result.phone, contact_data.phone)
        self.assertEqual(result.birthday, contact_data.birthday)
        self.assertEqual(result.additional_info, contact_data.additional_info)

        self.session.query().filter().first.assert_called_once_with()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(existing_contact)

    def test_update_contact_not_found(self):
        contact_id = 1
        contact_data = ContactUpdate(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            birthday=date(1990, 1, 1),
            additional_info='Additional information',
        )

        self.session.query().filter().first.return_value = None

        with self.assertRaises(ValueError):
            update_contact(self.session, contact_id, contact_data, self.user)

if __name__ == '__main__':
    unittest.main()
