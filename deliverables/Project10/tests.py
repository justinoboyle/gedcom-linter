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

    # US09 - Birth before death of parents
    # Child should be born before death of mother and before 9 months after death of father
    def test_US09(self):
        ''' Checks if a child is born before death of mother '''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.married = "2021-01-01"

            member1 = Individual('@TEST1', 4)
            member1.birthday = "2021-01-02"
            member1.death = "2021-01-01"

            family.addWife(member1)

            child = Individual('@CHILD', 2)
            child.birthday = "2021-01-03"
            child.name = "John Smith"

            family.addChild(child)
        except:
            failed = True
        self.assertTrue(failed)  

    # US10 - Marriage after 14
    # Marriage should be at least 14 years after birth of both spouses (parents must be at least 14 years old)
    def test_US10(self):
        ''' It should fail when marriage occurs before 14 years after birth '''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.setMarried("2019-01-01")

            member1 = Individual('@TEST1', 4)
            member1.birthday = "2019-01-02"

            family.addHusband(member1)

            member2 = Individual('@TEST2', 4)
            member2.birthday = "2019-01-03"

            family.addWife(member2)
        except:
            failed = True
        self.assertTrue(failed)

    # US11 (Irakli) - No Bigamy
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

    # US12 - Parents not too old
    # Mother should be less than 60 years older than her children and father should be less than 80 years older than his children
    def test_US12(self):
        ''' Creates a family where mother is 61 years older than their children '''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.setMarried("1980-01-01")

            member1 = Individual('@TEST1', 4)
            member1.birthday = "1946-01-02"

            family.addHusband(member1)

            member2 = Individual('@TEST2', 4)
            member2.birthday = "1946-01-03"

            family.addWife(member2)

            child = Individual('@CHILD', 2)
            child.birthday = "2021-01-04"
            child.name = "John Smith"

            family.addChild(child)
        except:
            failed = True
        self.assertTrue(failed)

    # US13 - Siblings spacing
    # Birth dates of siblings should be more than 8 months apart or less than 2 days apart 
    # (twins may be born one day apart, e.g. 11:59 PM and 12:02 AM the following calendar day)
    def test_US13(self):
        ''' Create two siblings born 4 months apart '''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.setMarried("2021-01-01")

            member1 = Individual('@TEST1', 4)
            member1.birthday = "2021-01-02"

            family.addHusband(member1)

            member2 = Individual('@TEST2', 4)
            member2.birthday = "2021-01-04"

            family.addWife(member2)

            child = Individual('@CHILD', 2)
            child.birthday = "2021-01-04"
            child.name = "John Smith"

            family.addChild(child)

            child2 = Individual('@CHILD2', 2)
            child2.birthday = "2021-05-03"
            child2.name = "Dave Smith"

            family.addChild(child2)
        except:
            failed = True
        self.assertTrue(failed)

    # US14 - Multiple births <= 5
    # No more than five siblings should be born at the same time
    def test_US14(self):
        ''' Create six siblings born on the same day and it should fail '''
        prepareTest()
        failed = False
        try:
            family = Family('@FAM1', 1)
            family.setMarried("2021-01-01")

            member1 = Individual('@TEST1', 4)
            member1.birthday = "2021-01-02"

            family.addHusband(member1)

            member2 = Individual('@TEST2', 4)
            member2.birthday = "2021-01-02"

            family.addWife(member2)

            child = Individual('@CHILD', 2)
            child.birthday = "2021-01-02"
            child.name = "John Smith"

            family.addChild(child)

            child2 = Individual('@CHILD2', 2)
            child2.birthday = "2021-01-02"
            child2.name = "Dave Smith"

            family.addChild(child2)

            child3 = Individual('@CHILD3', 2)
            child3.birthday = "2021-01-02"
            child3.name = "John Smith"

            family.addChild(child3)

            child4 = Individual('@CHILD4', 2)
            child4.birthday = "2021-01-02"
            child4.name = "Dave Smith"

            family.addChild(child4)

            child5 = Individual('@CHILD5', 2)
            child5.birthday = "2021-01-02"
            child5.name = "John Smith"

            family.addChild(child5)

            child6 = Individual('@CHILD6', 2)
            child6.birthday = "2021-01-02"
            child6.name = "Dave Smith"

            family.addChild(child6)
        except:
            failed = True
        self.assertTrue(failed)
    
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

    # US17 - No marriages to descendants
    # Parents should not marry any of their descendants
    def test_US17(self):
        ''' It should fail if a parent tries to marry a decendant '''
        prepareTest()
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person1.name = "Dave Smith"

            person2 = Individual('@TEST2', 4)
            person2.name = "John Hunt"

            person3 = Individual('@TEST3', 4)
            person3.name = "John Smith"

            family = Family('@FAM1', 5)
            family.addHusband(person1)
            family.addChild(person2)
            family.addChild(person3)
        except:
            failed = True
        self.assertTrue(failed)

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

    # US19 - First cousins should not marry
    # First cousins should not marry one another
    def test_US19(self):
        ''' it should fail if a first cousin marries another '''
        prepareTest()
        failed = False
        try:
            # First level Pat and Anne have 2 kids: John and Mary
            family1 = Family('@FAM1', 1)
            family1.setMarried("2021-01-01")

            patrick = Individual('@PATRICK', 4)
            patrick.setName("Patrick")
            family1.setHusband(patrick)

            anne = Individual('@ANNE', 4)
            anne.setName("Anne")
            family1.setWife(anne)

            patrick.setSpouse(anne)
            anne.setSpouse(patrick)

            # Make john and mary

            john = Individual('@JOHN', 4)
            john.setName("John")
            family1.addChild(john)

            mary = Individual('@MARY', 4)
            mary.setName("Mary")
            family1.addChild(mary)

            # John marries Stacey (new person)
            family2 = Family('@FAM2', 5)
            family2.setMarried("2021-01-01")

            stacey = Individual('@STACEY', 5)
            stacey.setName("Stacey")

            family2.setHusband(john)
            family2.setWife(stacey)

            # They have a kid named Bridget
            bridget = Individual('@BRIDGET', 6)
            bridget.setName("Bridget")
            family2.addChild(bridget)

            # Mary marries Kieran (new person)
            family3 = Family('@FAM3', 5)
            family3.setMarried("2021-01-01")

            kieran = Individual('@KIERAN', 5)
            kieran.setName("Kieran")

            family3.setWife(mary)
            family3.setHusband(kieran)

            # They have a kid named Dave
            dave = Individual('@DAVE', 6)
            dave.setName("Dave")
            family3.addChild(dave)

            # Bridget tries to marry dave
            family4 = Family('@FAM4', 5)
            family4.setMarried("2021-01-01")

            family4.setWife(bridget)
            family4.setHusband(dave)

            # The post check should fail
            people = [
                patrick,
                anne,
                john,
                mary,
                stacey,
                bridget,
                kieran,
                dave
            ]

            families = [
                family1,
                family2,
                family3,
                family4
            ]

            postvalidate(people, families)

        except:
            failed = True
        self.assertTrue(failed)

    # US20 (Irakli)
    # Aunts and Uncles should not marry their nephews or nieces
    
    # def test_US20(self):
    #     ''' Checks if aunt or uncle is married to nephew or niece'''
        prepareTest()

    # US20 - Aunts and uncles
    # Aunts and uncles should not marry their nieces or nephews
    def test_US20(self):
        ''' Checks if aunt or uncle is married to niece or nephew'''
        prepareTest()
        failed = False
        try:
            aunt = Individual('@TEST1', 1)
            uncle = Individual('@TEST2', 2)
            niece = Individual('@TEST3', 3)
            nephew = Individual('@TEST4', 4)

            family1 = Family('@FAM1')
            family1.wifeId = aunt.id
            family1.husbandId = uncle.id

            family2 = Family('@FAM2')
            family2.children = [niece.id, nephew.id]

            postvalidate([aunt, uncle, niece, nephew], [family1, family2])
            
        except:
            failed = True
        self.assertTrue(failed)

    # US21 - Correct gender for role
    # Husband in family should be male and wife in family should be female
    def test_US21(self):
        ''' It should fail if we try to create a female husband '''
        prepareTest()
        try:
            # create a family
            family = Family('@FAM1', 1)
            family.setMarried("2021-01-01")

            # create a person with gender F
            person1 = Individual('@TEST1', 5)
            person1.sex = 'F'
            family.setHusband(person1)

        except:
            failed = True
        self.assertTrue(failed)

    # US22 - Unique IDs
    # All individual IDs should be unique and all family IDs should be unique
    def test_US22(self):
        ''' it should throw an error if there are duplicate IDs '''
        prepareTest()
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person2 = Individual('@TEST1', 5)

            postvalidate([person1, person2], [])
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

    # US25 - Unique first names in families
    # No more than one child with the same name and birth date should appear in a family
    def test_US25(self):
        ''' fail if same name and birthday appears in family '''
        prepareTest()
        failed = False
        try:
            person1 = Individual('@TEST1', 5)
            person1.name = "Dave Smith"
            person1.setBirthday("2021-01-01")

            person2 = Individual('@TEST2', 5)
            person2.name = "Dave Smith"
            person1.setBirthday("2021-01-01")

            family1 = Family('@FAM1', 1)
            family1.addChild(person1)
            family1.addChild(person2)

        except:
            failed = True
        self.assertTrue(failed)

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

    # US27 - Include individual ages
    # Include person's current age when listing individuals
    def test_US27(self):
        ''' Post list should have person's age '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setAge(15)

        postvalidate([person1], [])

        res = printprep([person1], [])

        self.assertTrue(''.join(res).__contains__('15'))

    # US28 - Order siblings by age
    # List siblings in families by decreasing age, i.e. oldest siblings first
    def test_US28(self):
        ''' Post list should put older first '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setBirthday("1980-01-01")

        person2 = Individual('@TEST2', 2)
        person2.name = "Jane Doe"
        person2.setBirthday("1980-01-02")

        person3 = Individual('@TEST3', 2)
        person3.name = "Jane2 Doe"
        person3.setBirthday("2021-01-02")

        husband = Individual('@TEST4', 2)
        husband.name = "John Doe"
        husband.setBirthday("1960-01-01")

        wife = Individual('@TEST5', 2)
        wife.name = "Jane Doe"
        wife.setBirthday("1960-01-02")

        family = Family('@FAM1')
        family.addHusband(husband)
        family.addWife(wife)
        family.setMarried("1970-01-01")
        family.addChild(person2)
        family.addChild(person1)
        family.addChild(person3)

        x= [person1, person2]
        individuals, families = postvalidate(x, [family])

        self.assertEqual(families[0].children[0], person3.id)

    # US29 - List deceased
    # List all deceased individuals in a GEDCOM file
    def test_US29(self):
        ''' see if listBuffer contains deceased individuals '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setBirthday("2021-01-01")
        person1.setDeath("2022-01-01")

        person2 = Individual('@TEST2', 2)
        person2.name = "Jane Doe"
        person2.setBirthday("2021-01-02")
        person2.setDeath("2022-01-01")

        postvalidate([person1, person2], [])

        ret = printprep([person1, person2], [])

        # check if the text person1 id is in list buffer
        self.assertTrue(''.join(ret).__contains__(person1.name))


    # US30 - List living married
    # List all living married people in a GEDCOM file
    def test_US30(self):
        ''' see if listBuffer contains married people '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setBirthday("2021-01-01")
        # person1.setDeath("2021-01-01")

        person2 = Individual('@TEST2', 2)
        person2.name = "Jane Doe"
        person2.setBirthday("2021-01-02")
        # person2.setDeath("2021-01-01")

        family = Family('@FAM1')
        family.setMarried("2022-01-01")
        family.addHusband(person1)
        family.addWife(person2)

        postvalidate([person1, person2], [family])

        ret = printprep([person1, person2], [family])

        # check if the text person1 id is in list buffer
        self.assertTrue(''.join(ret).__contains__(person1.name))

    # US31 - List living single
    # List all living people over 30 who have never been married in a GEDCOM file
    def test_US31(self):
        ''' see if listBuffer contains single people '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setBirthday("1990-01-01")
        # person1.setDeath("2021-01-01")

        person2 = Individual('@TEST2', 2)
        person2.name = "Jane Doe"
        person2.setBirthday("1990-01-02")
        # person2.setDeath("2021-01-01")

        postvalidate([person1, person2], [])

        entireBuffer = ' '.join(getListBuffer())

        # check if the text person1 id is in list buffer
        self.assertTrue(entireBuffer.__contains__(person1.name))

    # US32 - List multiple births 
    # List all multiple births in a GEDCOM file
    def test_US32(self):
        ''' see if listBuffer contains multiple births '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setBirthday("2021-01-01")
        # person1.setDeath("2021-01-01")

        person2 = Individual('@TEST2', 2)
        person2.name = "Jane Doe"
        person2.setBirthday("2021-01-01")
        # person2.setDeath("2021-01-01")

        postvalidate([person1, person2], [])

        entireBuffer = ' '.join(getListBuffer())

        # check if the text person1 id is in list buffer
        self.assertTrue(entireBuffer.__contains__(person1.name))

    # US33 - List orphans
    # List all orphaned children (both parents dead and child < 18 years old) in a GEDCOM file
    def test_US33(self):
        ''' all orphaned children should be in the listBuffer '''
        prepareTest()
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe"
        person1.setBirthday("1980-01-01")
        person1.setDeath("2022-01-01")

        person2 = Individual('@TEST2', 2)
        person2.name = "Jane Doe"
        person2.setBirthday("1980-01-02")
        person2.setDeath("2022-01-01")

        # add a child
        person3 = Individual('@TEST3', 2)
        person3.name = "Jane Doe"
        person3.setBirthday("2021-01-02")
        # person3.setDeath("2022-01-01")

        # marry them and add a child
        family = Family('@FAM1')
        family.setMarried("1990-01-01")
        family.addWife(person2)
        family.addHusband(person1)
        family.addChild(person3)
        
        postvalidate([person1, person2, person3], [family])

        # check if the text person1 id is in list buffer
        found = False
        for i in getListBuffer():
            if i.__contains__(person3.id):
                found = True
                break
        self.assertTrue(found)

    # US34
    # List all couples who were married when the older spouse was 
    # more than twice as old as the younger spouse
    def test_US34(self):
        '''Checks if output is all couples married when one spouse was at least twice as old'''
        prepareTest()
        failed = False
    
        family1 = Family('@FAM1')
        family2 = Family('@FAM2')
        family3 = Family('@FAM3')

        husband1 = Individual('@TEST1', 5)
        husband1.name = 'John Smith'
        husband1.setBirthday("1940-01-01")
        wife1 = Individual('@TEST2', 5)
        wife1.name = 'Jane Smith'
        wife1.setBirthday("1990-01-01")

        husband2 = Individual('@TEST3', 5)
        husband2.name = "Joe Moe"
        husband2.setBirthday("1990-01-01")
        wife2 = Individual('@TEST4', 5)
        wife2.name = "Jenny Moe"
        wife2.setBirthday("1930-01-01")

        husband3 = Individual('@TEST5', 5)
        husband3.name = "Joe Schmo"
        husband3.setBirthday("1980-01-02")
        wife3 = Individual('@TEST6', 5)
        wife3.name = "Jenny Schmo"
        wife3.setBirthday("1981-01-01")
        

        family1.addHusband(husband1)
        family1.addWife(wife1)
        family1.married = "2010-01-01"

        family2.addHusband(husband2)
        family2.addWife(wife2)
        family2.married = "2010-01-01"

        family3.addHusband(husband3)
        family3.addWife(wife3)
        family3.married = "2010-01-01"
        
        families = [family1, family2, family3]
        if listOlderSpouses(families) != ['FAM1', 'FAM2']:
            failed = True

        self.assertTrue(failed)

    # US35
    # List all people in a GEDCOM file who were born in the last 30 days
    def test_US35(self):
        '''Checks if output is all people born in last 30 days'''
        prepareTest()
        failed = False

        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe New"
        person1.setBirthday("2021-03-15")

        person2 = Individual('@TEST2', 1)
        person2.name = "John Boe New"
        person2.setBirthday("2021-03-01")

        person3 = Individual('@TEST3', 1)
        person3.name = "John Coe Old"
        person3.setBirthday("2020-01-15")
        
        indiList = [person1, person2, person3]

        ret = ', '.join(listRecentBirths(indiList, dateFromString("2021-03-30")))

        if ret.__contains__("John Doe New") and ret.__contains__("John Boe New"):
            failed = True
        self.assertTrue(failed)

    # US36
    # List all people in a GEDCOM file who died in the last 30 days
    def test_US36(self):
        '''Checks if output is all people dead in last 30 days'''
        prepareTest()
        failed = False
        
        person1 = Individual('@TEST1', 1)
        person1.name = "John Doe New"
        person1.setDeath("2021-03-15")

        person2 = Individual('@TEST2', 1)
        person2.name = "John Boe New"
        person2.setDeath("2021-03-01")

        person3 = Individual('@TEST3', 1)
        person3.name = "John Coe Old"
        person3.setDeath("2020-01-15")
        
        indiList = [person1, person2, person3]

        ret = ', '.join(listRecentDeaths(indiList, dateFromString("2021-03-30")))

        if ret.__contains__("John Doe New") and ret.__contains__("John Boe New"):
            failed = True
        self.assertTrue(failed)

# required unittest boilerplate
if __name__ == '__main__':
    unittest.main()