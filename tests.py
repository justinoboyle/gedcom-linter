import unittest
from src import * # import our project's source code

# Data is piped in from run-tests shell script to stdin

# run it on the input 
lines = runLinter()
individuals, families = runParser(lines)

# run tests
class TestGEDCOM(unittest.TestCase):

    # US03 - Birth Before Death 
    # All birthdays should be before deaths
    def test_US03(self):
        ''' It should fail if birthday is after death  '''
        failed = False
        try:
            individual = Individual('@TEST', 5)
            individual.setBirthday(datetime.datetime(2019, 1, 1))
            individual.setDeath(datetime.datetime(2018, 1, 1))
        except:
            failed = True
        self.assertTrue(failed)

    # US04 - Marriage before divorce
    # Marriage should occur before divorce of spouses (if divorce is listed)
    def test_US04(self):
        ''' Check if marriage occurs before divorce '''
        for family in families:
            if family.divorced != None:
                self.assertTrue(family.married <= family.divorced)

    # US07 - Less then 150 years old
    # All users have to be less than 150 years old
    def test_US07(self):
        ''' It should fail when an individual is older than 150 years '''
        failed = False
        try:
            Individual('@TEST', 5).setAge(151)
        except:
            failed = True
        self.assertTrue(failed)

    # US08 - Birth before marriage of parents
    # Children should be born after marriage of parents
    def test_US08(self):
        ''' It should fail when a child is born after parents are married '''
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.husbandName = "Dave Smith"
            family.married = "2021-01-01"

            child = Individual('@CHILD', 2)
            child.birthday = "2021-01-02"
            child.name = "John Smith"

            family.addChild(child)
        except:
            failed = True
        self.assertTrue(failed)

    # US16 - Male last names
    # All male members of a family should have the same last name
    def test_US16(self):
        ''' It should fail if you create a man with a different last name in a family '''
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person1.name = "Dave Smith"

            person2 = Individual('@TEST2', 4)
            person2.name = "John Hunt"

            family = Family('@FAM1', 5)
            family.addHusband(person1)
            family.addChild(person2)
        except:
            failed = True
        self.assertTrue(failed)

    # US22 - Unique IDs
    # All individual IDs should be unique and all family IDs should be unique
    def test_US22(self):
        ''' Check if given list contains any duplicates '''
        return self.assertEqual(len(individuals), len(set(individuals))) and self.assertEqual(len(families), len(set(families)))

    # US23 - Unique Name and Birth Date
    # All individuals should have a unique name and birth date
    def test_US23(self):
        ''' Check if given list contains any duplicates '''
        return self.assertEqual(len(individuals), len(set(individuals)))

# required unittest boilerplate
if __name__ == '__main__':
    unittest.main()