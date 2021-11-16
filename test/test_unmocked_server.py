import unittest
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

from app import delete, save_expense

INPUT = "INPUT"
EXPECTED_OUTPUT = "EXPECTED_OUTPUT"


class SetBudgetTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                INPUT: (),
                EXPECTED_OUTPUT: (None),
            },
            {
                INPUT: (1000),
                EXPECTED_OUTPUT: (1000.0),
            },
            {
                INPUT: (529.23),
                EXPECTED_OUTPUT: (529.23),
            },
        ]

    def test_save_budget(self):
        for test in self.success_test_params:
            self.assertEqual(delete(test[INPUT]), test[EXPECTED_OUTPUT])


class SetExpenseTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
