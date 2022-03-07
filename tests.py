import unittest
from src import * # import our project's source code

# Data is piped in from run-tests shell script to stdin

# run it on the input 
lines = runLinter()
individuals, families = runParser(lines)

# run tests
class TestGEDCOM(unittest.TestCase):

    # US22 - Unique IDs
    # All individual IDs should be unique and all family IDs should be unique
    def test_US22(self):
        ''' Check if given list contains any duplicates '''
        return self.assertEqual(len(individuals), len(set(individuals))) and self.assertEqual(len(families), len(set(families)))

    # US04 - Marriage before divorce
    # Marriage should occur before divorce of spouses (if divorce is listed)
    def test_US04(self):
        ''' Check if marriage occurs before divorce '''
        for family in families:
            if family.divorced != None:
                self.assertTrue(family.married <= family.divorced)

    # US23 - Unique Name and Birth Date
    # All individuals should have a unique name and birth date
    def test_US23(self):
        ''' Check if given list contains any duplicates '''
        return self.assertEqual(len(individuals), len(set(individuals)))

# required unittest boilerplate
if __name__ == '__main__':
    unittest.main()