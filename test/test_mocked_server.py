import unittest
from unittest.mock import MagicMock, patch
from flask import request
from flask_login import current_user

import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from base import BaseTestCase
from app import Userdb, bcrypt

INPUT = "INPUT"
EXPECTED_OUTPUT = "EXPECTED_OUTPUT"


class TestUser(BaseTestCase):

    # Test registration function
    def test_user_registeration(self):
        with self.client:
            response = self.client.post(
                "register/",
                data=dict(
                    username="test123",
                    email="test123@gmail.com",
                    password="payup123",
                    confirm="payup123",
                ),
                follow_redirects=True,
            )
            self.assertIn(b"Welcome to PayUp!", response.data)
            self.assertTrue(current_user.name == "test123")
            self.assertTrue(current_user.is_active())
            user = Userdb.query.filter_by(email="test123@gmail.com").first()
            self.assertTrue(str(user) == "<name - test123>")

    # Test errors are thrown during an incorrect user registration
    def test_incorrect_user_registeration(self):
        with self.client:
            response = self.client.post(
                "register/",
                data=dict(
                    username="test123",
                    email="test123",
                    password="payup123",
                    confirm="payup123",
                ),
                follow_redirects=True,
            )
            self.assertIn(b"Invalid email address.", response.data)
            self.assertIn(b"/register/", request.url)

    # Test given password is correct after unhashing
    def test_check_password(self):
        user = Userdb.query.filter_by(email="test123@gmail.com").first()
        self.assertTrue(bcrypt.check_password_hash(user.password, "payup123"))
        self.assertFalse(bcrypt.check_password_hash(user.password, "foobar"))


if __name__ == "__main__":
    unittest.main()
