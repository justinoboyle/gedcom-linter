import unittest
from src import * # import our project's source code

setFailMode(True)

def prepareTest():
    flushIDBuffer()


# UNIT tests -- these unit tests run on small data sets
class TestGEDCOM(unittest.TestCase):
    # US01 - Dates before current date
    # Dates should come before current date
    def test_US01(self):
        ''' it should fail if birth is after the current date '''
        prepareTest()
        
        failed = False
        try:
            individual = Individual('@TEST01', 2)
            individual.setBirthday(datetime.datetime(9999, 1, 1))
        except:
            failed = True
        self.assertTrue(failed)
    
    # US02 (Irakli)
    # Birth should occur before marriage of an individual
    def test_US02(self):
        ''' it should fail if birth is after marriage'''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.married = "2021-01-01"

            member1 = Individual('@TEST1', 4)
            member1.birthday = "2021-01-02"

            family.addHusband(member1)
        except:
            failed = True
        self.assertTrue(failed)


    # US03 - Birth Before Death 
    # All birthdays should be before deaths
    def test_US03(self):
        ''' it should fail if birthday is after death  '''
        prepareTest()
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
        ''' it should fail if marriage is before divorce '''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM4', 1)
            family.setMarried("2021-01-01")
            family.setDivorced("2021-01-02")
        except:
            failed = True
        self.assertTrue(failed)
    
    # US05 - Marriage before death
    # Marriage should occur before death
    def test_US05(self):
        ''' it should fail if marriage is after death '''
        prepareTest()
        failed = False
        try:
            individual = Individual('@TEST', 5)
            individual.setMarriage(datetime.datetime(2019, 1, 1))
            individual.setDeath(datetime.datetime(2018, 1, 1))
        except:
            failed = True
        self.assertTrue(failed)

    # US06 (Irakli)
    # Divorce can only occur before death of both spouses
    def test_US06(self):
        ''' Checks if divorce occurs after death of a spouse'''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.married = "2021-01-02"

            member1 = Individual('@TEST1', 4)
            member1.death = "2021-01-01"

            family.addHusband(member1)
        except:
            failed = True
        self.assertTrue(failed)


    # US07 - Less then 150 years old
    # All users have to be less than 150 years old
    def test_US07(self):
        ''' It should fail when an individual is older than 150 years '''
        prepareTest()
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
        prepareTest()
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

    # US09 ??

    # US10 ??

    # US11 (Irakli)
    # Marriage should not occur during marriage to another spouse
    def test_US11(self):
        '''Checks if someone is married to more than 1 person'''
        prepareTest()
        failed = False
        try:
            family1 = Family('@FAM1', 4)
            family2 = Family('@FAM2', 4)
            member1 = Individual('@TEST1', 4)
            member2 = Individual('@TEST2', 4)
            member3 = Individual('@TEST3', 4)
            family1.husbandId = member1.id
            family1.wifeId = member2.id
            family2.husbandId = member1.id
            family2.wifeId = member3.id
        except:
            failed = True
        self.assertTrue(failed)

    # US12 ??

    # US13 ??

    # US14 ??
    
    # US15 (Irakli)
    # There should be fewer than 15 siblings in a family
    def test_US15(self):
        '''Verifies function will throw with more than 15 siblings'''
        prepareTest()
        failed = False
        families = []
        try:
            families.append(self.constructFamily(16))
            Family.tooManySiblings(families)
        except:
            failed = True
        self.assertTrue(failed)
     
    # US16 - Male last names
    # All male members of a family should have the same last name
    def test_US16(self):
        ''' It should fail if you create a man with a different last name in a family '''
        prepareTest()
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

    # US17 ??

    # US18 - Siblings should not marry (Max Sprint 3)
    # Siblings should not marry
    def test_US18(self):
        ''' Check if given list contains any duplicates '''
        prepareTest()
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

    # US19 ??

    # US20 (Irakli)
    # Aunts and Uncles should not marry their nephews or nieces
    
    # def test_US20(self):
    #     ''' Checks if aunt or uncle is married to nephew or niece'''
        prepareTest()
    #     failed = False
    #     try:
    #         aunt = Individual('@TEST1', 1)
    #         uncle = Individual('@TEST2', 2)
    #         niece = Individual('@TEST3', 3)
    #         nephew = Individual('@TEST4', 4)

    #         family1 = Family('@FAM1')
    #         family1.wifeId = aunt.id
    #         family1.husbandId = uncle.id

    #         family2 = Family('@FAM2')
    #         family2.children = [niece.id, nephew.id]
            
    #     except:
    #         failed = True
    #     self.assertTrue(failed)

    # US22 - Unique IDs
    # All individual IDs should be unique and all family IDs should be unique
    def test_US22(self):
        ''' it should throw an error if there are duplicate IDs '''
        prepareTest()
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person2 = Individual('@TEST1', 5)
        except:
            failed = True
        self.assertTrue(failed)


    # US23 - Unique Name and Birth Date
    # No more than one individual with the same name and birth date should appear in a GEDCOM file
    def test_US23(self):
        ''' it should throw an error if the name and date are not unique '''
        prepareTest()
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person1.name = "Dave Smith"
            person1.setBirthday("2021-01-01")

            person2 = Individual('@TEST2', 5)
            person2.name = "Dave Smith"
            person1.setBirthday("2021-01-01")

        except:
            failed = True
        self.assertTrue(failed)

    # US24 - Unique families by spouses
    # No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file
    def test_US24(self):
        prepareTest()
        failed = False
        try:
            families = []
            family1 = Family('@FAM1', 1)
            family2 = Family('@FAM2', 1)

            husband = Individual('@TEST1', 5)
            wife = Individual('@TEST1', 5)
            
            family1.setHusband(husband)
            family1.setWife(wife)

            family2.setHusband(husband)
            family2.setWife(wife)

            postvalidate([], families)

        except:
            failed = True
        self.assertTrue(failed)

    # US25 ???

    # US26 (Irakli)
    # the information in the individual and family records should be consistent
    def test_US26(self):
        '''Checks if an individual does not exist in its own family'''
        prepareTest()
        failed = False
        try:
            person1 = Individual('@TEST1', 1)
            person1.name = "John Doe"
            person2 = Individual('@TEST2', 2)
            person2.name = "Jane Doe"

            family = Family('@FAM1')
            family.wifeId = person2.id

            person1.family = family
            person2.family = family
            checkConsistency(person1,family)
        except:
            failed = True
        self.assertTrue(failed)

# required unittest boilerplate
if __name__ == '__main__':
    unittest.main()