import unittest
from src import * # import our project's source code

# Data is piped in from run-tests shell script to stdin

# run it on the input 
lines = runLinter()
individuals, families = runParser(lines)

# run tests
class TestGEDCOM(unittest.TestCase):
    # US01 - Dates before current date
    # Dates should come before current date
    def test_US01(self):
        '''Verifies birthdays occur before current date'''
        for ind in individuals:
            # convert ind.birthday string to datetime.datetime
            ind.birthday = datetime.datetime.strptime(ind.birthday, '%Y-%m-%d')
            if ind.birthday > datetime.datetime.now():
                return False
        return True


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
    
    # US05 - Marriage before death
    # Marriage should occur before death
    def test_US05(self):
        ''' It should fail when an individual marries after their deathdate '''
        failed = False
        try:
            individual = Individual('@TEST', 5)
            individual.setMarriage(datetime.datetime(2019, 1, 1))
            individual.setDeath(datetime.datetime(2018, 1, 1))
        except:
            failed = True
        self.assertTrue(failed)


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

    # US11 - No bigamy
    # Marriage should not occur during marriage to another spouse
    def test_US11(self):
        failed = False
        try:

            family1 = Family('@FAM1', 1)
            husband1 = Individual('@HUSB1', 2)
            husband1.name = "Dave Smith"
            family1.married = "2021-01-01"
            family1.setHusband(husband1)

            family2 = Family('@FAM2', 1)
            family2.married = "2021-01-01"
            family2.setHusband(husband1)

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

    # US18 - Siblings should not marry (Max Sprint 3)
    # Siblings should not marry
    def test_US18(self):
        ''' Check if given list contains any duplicates '''
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person1.name = "Dave Smith"

            person2 = Individual('@TEST2', 4)
            person2.name = "John Hunt"

            family = Family('@FAM1')
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

        # US24 - Unique Family by spouses (Max Sprint 3)
    # A family should only have one family with the same spouses by name and marriage date
    def test_US24(self):
        # create two families that fail the test
        family1 = Family('@FAM1')
        family1.married = "2021-01-01"
        family1.husbandId = '@HUSB1'
        family1.wifeId = '@WIFE1'

        family2 = Family('@FAM2')
        family2.married = "2021-01-01"
        family2.husbandId = '@HUSB1'
        family2.wifeId = '@WIFE1'

        # create two families that pass the test
        family3 = Family('@FAM3')
        family3.married = "2021-01-01"
        family3.husbandId = '@HUSB1'
        family3.wifeId = '@WIFE2'

        family4 = Family('@FAM4')
        family4.married = "2021-01-01"
        family4.husbandId = '@HUSB2'
        family4.wifeId = '@WIFE2'

        # create two individuals that fail the test
        individual1 = Individual('@HUSB1', 5)
        individual1.name = "Dave Smith"

        individual2 = Individual('@WIFE1', 4)
        individual2.name = "John Hunt"

        # create two individuals that pass the test
        individual3 = Individual('@HUSB2', 5)
        individual3.name = "Dave Smith"

        individual4 = Individual('@WIFE2', 4)
        individual4.name = "John Hunt"

        # add the individuals to the families
        family1.addHusband(individual1)
        family1.wifeId = '@WIFE1'

        family2.addHusband(individual1)
        family2.wifeId = '@WIFE1'

        family3.addHusband(individual3)
        family3.wifeId = '@WIFE2'

        family4.addHusband(individual3)
        family4.wifeId = '@WIFE2'

        # add the families to the list
        families.append(family1)
        families.append(family2)
        families.append(family3)
        families.append(family4)

        # check if the families are unique
        self.assertEqual(len(families), len(set(families)))

        
    def test_US11(self):
        '''Check if someone is married to more than 1 person'''
        indis = {}
        for fam in families:
            if fam.wifeId in indis or fam.husbandId in indis:
                return False
            else:
                indis[fam.wifeId] = 1
                indis[fam.husbandId] = 1
        return True
    
    def test_US15(self):
        '''Verifies families have less than 15 siblings'''
        for fam in families:
            if len(fam.children) >= 15:
                return False
        return True

# required unittest boilerplate
if __name__ == '__main__':
    unittest.main()