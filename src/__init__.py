import fileinput
import csv
import os
import datetime
import sys

from printer import printer

tagNames = []

def dateFromString(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d')

with open(os.path.realpath(__file__+ "/..") + '/tags.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    next(csvfile)
    for row in reader:
        tagNames.append(row[1])

def isValidTag(tag):
    return tag in tagNames

class ParsedGEDCOM:
    def __init__(self, line):
        ids = []
        builder = line.strip().split(" ")

        # the level of the input line, e.g. 0, 1, 2
        self.level = int(builder[0])

        if len(builder) > 2 and (builder[2] == "INDI" or builder[2] == "FAM"):
            self.tag = builder[2]
            if len(builder) < 4:
                self.args = [builder[1]]
            else:
                self.args = [builder[1]] + builder[3:]
        else:
            # the tag associated with the line, e.g. 'INDI', 'FAM', 'DATE', ...
            self.tag = builder[1]

            self.args = builder[2:]

        self.valid = isValidTag(self.tag)

        if self.tag == "INDI":
            if self.args[0] in ids:
                pass
            else:
                ids.append(self.args[0])

    def __str__(self):
        return str(self.level) + "|" + self.tag + "|" + ("Y" if self.valid else "N") + "|" + " ".join(self.args)

errorBuffer = []
listBuffer = []
failMode = False
def doError(error):
    if failMode:
        raise Exception(error)
    errorBuffer.append(error)

def doListBuffer(msg):
    global listBuffer
    listBuffer.append(msg)

def clearListBuffer():
    global listBuffer
    listBuffer = []

def runLinter():
    # Read from standard input and return an array of ParsedGEDCOM objects
    lines = []
    for line in fileinput.input():
        # print(ParsedGEDCOM(line))
        lines.append(ParsedGEDCOM(line))
    return lines

idBuffer = []

# Use this buffer for things that have to be unique -- e.g. IDs
def uniqueIdBuffer(newID, idType):
    global idBuffer
    if (idType + newID) in idBuffer:
        # TODO Add a feature to make this error message better.
        doError("ID " + newID + " is not unique!")
    else:
        idBuffer.append(idType + newID)

def flushIDBuffer():
    global idBuffer
    idBuffer = []

class Individual:
    def __init__(self, id, level):
        self.id = id
        uniqueIdBuffer(id, "INDI")
        self.level = level
        self.name = "N/A"
        self.sex = "N/A"
        self.birthday = "N/A"
        self.age = "N/A"
        self.isAlive = True
        self.death = "N/A"
        self.children = []
        self.spouse = "N/A"
        self.family = "N/A"

    def setSpouse(self, spouse):
        if(self.spouse != "N/A"):
            doError("Bigamy: already married! (Individual ID " + self.id + ")")
        self.spouse = spouse

    def setAge(self, age):
        if age >= 150:
            doError("Age must be less than 150! (Individual ID " + self.id + ")")
        self.age = age

    def validateBirthDeath(self):
        if self.birthday != "N/A" and datetime.datetime.strptime(self.birthday, '%Y-%m-%d') > datetime.datetime.now():
            doError("Birthday must be before current date! (Individual ID " + self.id + ")")
        if self.birthday == "N/A" or self.death == "N/A":
            pass
        else:
            if dateFromString(self.birthday) > dateFromString(self.death):
                doError("Birthday must be before death! (Individual ID " + self.id + ")")

    def setBirthday(self, birthday):
        self.birthday = birthday
        uniqueIdBuffer(self.name + self.birthday, "INDI-BDAYD")
        self.validateBirthDeath()

    def setDeath(self, death):
        self.death = death
        self.validateBirthDeath()
    
    # US02 (Irakli)
    # Birth should occur before marriage of an individual
    def checkMarriage(self):
        '''verify that birth comes before marriage'''
        marriage = self.family.married
        if datetime.datetime.strptime(self.birthday, '%Y-%m-%d') < datetime.datetime.strptime(marriage, '%Y-%m-%d'):
            doError("Birthday must be before marriage! (Individual ID " + self.id + ")")

    # US06 (Irakli)
    # Divorce can only occur before death of both spouses
    def checkDivorce(self):
        '''verify that divorce comes before death'''
        divorce = self.family.divorced
        if datetime.datetime.strptime(self.death, '%Y-%m-%d') < datetime.datetime.strptime(divorce, '%Y-%m-%d'):
            doError("Divorce must be before death! (Individual ID " + self.id + ")")


    def __str__(self):
         return self.id

    def __repr__(self):
        return self.id

class Family:
    def __init__(self, id):
        self.id = id
        uniqueIdBuffer(id, "INDI")
        self.married = "N/A"
        self.divorced = "N/A"
        self.husbandId = "N/A"
        self.husbandName = "N/A"
        self.wifeId = "N/A"
        self.wifeName = "N/A"
        self.children = []
        self._wifeRef = None
        self._husbRef = None


    def addHusband(self, husband):
        if husband.family != "N/A":
            doError("Husband " + husband.id + " is already in a family and cannot be added to " + self.id + "!")
        self.husbandId = husband.id
        self.husbandName = husband.name
        self._husbRef = husband

    def addWife(self, wife):
        if wife.family != "N/A":
            doError("Wife " + wife.id + " is already in a family and cannot be added to " + self.id + "!")
        self.husbandId = wife.id
        self.husbandName = wife.name
        self._wifeRef = wife

    def addChild(self, child):
        if dateFromString(self.married) > dateFromString(child.birthday):
            doError("Child can't be born before parents were married!")
            
        # get last name of husbandName
        husbandLastName = self.husbandName.split(" ")[-1]
        # get last name of childName
        childLastName = child.name.split(" ")[-1]
        # if last name of husbandName == last name of childName
        if husbandLastName == childLastName:
            self.children.append(child.id)
        else:
            doError("Last name of husband and child must match!")
        
    # US15 Fewer than 15 siblings (Irakli)
    # There should be fewer than 15 siblings in a family
    def tooManySiblings(families):
        for fam in families:
            if len(fam.children) >= 15:
                doError("Too many siblings in family id " + fam.id)
        return True

    def setMarried(self, married):
        self.married = married
        self.validateMarriedDivorced()
    
    def setDivorced(self, divorced):
        self.divorced = divorced
        self.validateMarriedDivorced()

    def validateMarriedDivorced(self):
        if self.married == "N/A" or self.divorced == "N/A":
            pass
        else:
            if dateFromString(self.married) > dateFromString(self.divorced):
                 doError("FAMILY: US04: " + self.id + ": Marriage occurs after divorce")

    def __str__(self):
        return self.id
    
    def __repr__(self):
        return self.id

def toMonths(str):
    if str == "JAN":
        return "01"
    elif str == "FEB":
        return "02"
    elif str == "MAR":
        return "03"
    elif str == "APR":
        return "04"
    elif str == "MAY":
        return "05"
    elif str == "JUN":
        return "06"
    elif str == "JUL":
        return "07"
    elif str == "AUG":
        return "08"
    elif str == "SEP":
        return "09"
    elif str == "OCT":
        return "10"
    elif str == "NOV":
        return "11"
    elif str == "DEC":
        return "12"
    else:
        return "N/A"

def setFailMode(mode):
    global failMode
    failMode = mode

def runParser(lines, isFailMode):
    setFailMode(isFailMode)
    # Return a list of individuals and a list of families based on tags
    families = []
    # Initialize all families so that individuals can be inserted
    for line in lines:
        if line.tag == "FAM":
            families.append(Family(line.args[0]))
    individuals = []
    for i in range(len(lines)):
        # Lines represents each line of the input file, which is an object with a .tag and .args
        line = lines[i]
        if line.tag == "INDI":
            individuals.append(Individual(line.args[0], line.level))
            # Nested loop required as subsequent lines give information about the individual
            # For birth and death the next line holds the date value so i must be incremented
            for i in range(i+1, len(lines)):
                line = lines[i]
                if line.tag == "NAME":
                    # remove slashes from /lastname/ in args[1]
                    individuals[-1].name = line.args[0] + " " + line.args[1].replace("/", "")
                elif line.tag == "SEX":
                    individuals[-1].sex = line.args[0]
                elif line.tag == "BIRT":
                    i+=1
                    # individuals[-1].birthday = 'YYYY-MM-DD'
                    individuals[-1].setBirthday(lines[i].args[2] + "-" + toMonths(lines[i].args[1]) + "-" + lines[i].args[0].zfill(2))
                elif line.tag == "DEAT":
                    if line.args[0] == "Y":
                        individuals[-1].isAlive = False
                    i+=1
                    individuals[-1].setDeath(lines[i].args[2] + "-" + toMonths(lines[i].args[1]) + "-" + lines[i].args[0].zfill(2))
                elif line.tag == "FAMC":
                    # search families for args[0], in the family add to children
                    for fam in families:
                        if fam.id == line.args[0]:
                            individuals[-1].children.append(fam)
                elif line.tag == "FAMS":
                    # search families for family ID, add spouse ID & Name to family
                    for fam in families:
                        if fam.id == line.args[0]:
                            if individuals[-1].sex == "M":
                                individuals[-1].setSpouse(fam)
                                fam.husbandId = individuals[-1].id
                                fam.husbandName = individuals[-1].name
                            else:
                                individuals[-1].setSpouse(fam)
                                fam.wifeId = individuals[-1].id
                                fam.wifeName = individuals[-1].name
                elif line.level != 0:
                    pass
                else:
                    # Level is 0 when we are at the next individual
                    break
        elif line.tag == "FAM":
            families.append(Family(line.args[0]))
            # Nested loop required as subsequent lines give information about the family
            # For marriage and divorce the next line holds the date value so i must be incremented
            for i in range(i+1, len(lines)):
                line = lines[i]
                if line.tag == "MARR":
                    i+=1
                    families[-1].setMarried(lines[i].args[0] + " " + lines[i].args[1] + " " + lines[i].args[2])
                elif line.tag == "DIV":
                    i+=1
                    families[-1].setDivorced(lines[i].args[0] + " " + lines[i].args[1] + " " + lines[i].args[2])
                elif line.tag == "HUSB":
                    families[-1].husband_id = line.args[0]
                    for indi in individuals:
                        if indi.id == line.args[0]:
                            families[-1].husband_name = indi.name
                elif line.tag == "WIFE":
                    families[-1].wife_id = line.args[0]
                    for indi in individuals:
                        if indi.id == line.args[0]:
                            families[-1].wife_name = indi.name
                elif line.tag == "CHIL":
                    families[-1].children.append(line.args[0])
                elif line.level != 0:
                    pass
                else:
                    break
        else:
            pass

    # Merge families with the same id into one family
    mergedFamilies = []
    for fam in families:
        if fam.id not in [x.id for x in mergedFamilies]:
            mergedFamilies.append(fam)
        else:
            for mergedFam in mergedFamilies:
                if mergedFam.id == fam.id:
                    if fam.husband_id != "N/A":
                        mergedFam.husband_id = fam.husband_id
                        mergedFam.husband_name = fam.husband_name
                    if fam.wife_id != "N/A":
                        mergedFam.wife_id = fam.wife_id
                        mergedFam.wife_name = fam.wife_name
                    if fam.married != "N/A":
                        mergedFam.setMarried(fam.married)
                    if fam.divorced != "N/A":
                        mergedFam.setDivorced(fam.divorced)
                    if fam.children != []:
                        mergedFam.children.extend(fam.children)
    
    # datetime.datetime.strptime(indi.birthday, "%Y-%m-%d")

    # get the age of each individual alive or dead
    for indi in individuals:
        if indi.isAlive:
            indi.setAge((datetime.datetime.today() - datetime.datetime.strptime(indi.birthday, "%Y-%m-%d")).days // 365)
        else:
            indi.setAge((datetime.datetime.strptime(indi.death, "%Y-%m-%d") - datetime.datetime.strptime(indi.birthday, "%Y-%m-%d")).days // 365)

    # US09 Birth before death of parents
    # for each family make sure every child has a birthday before the death of the mother and father
    for fam in mergedFamilies:
        if fam.married != "N/A":
            for child in fam.children:
                for indi in individuals:
                    if indi.id == child:
                        # find the birthday of the father and mother
                        for indi2 in individuals:
                            if indi2.id == fam.husband_id:
                                fatherDeath = indi2.death
                            if indi2.id == fam.wife_id:
                                motherDeath = indi2.death
                        # if the child's birthday is before the death of the father or mother, print an error
                        if (fatherDeath != "N/A") and datetime.datetime.strptime(indi.birthday, "%Y-%m-%d") > datetime.datetime.strptime(fatherDeath, "%Y-%m-%d"):
                            doError("FAMILY: US09: " + fam.id + ": Child " + indi.id + " born " + indi.birthday + " after death of father " + fam.husband_id + " " + fatherDeath)
                        if (motherDeath != "N/A") and datetime.datetime.strptime(indi.birthday, "%Y-%m-%d") > datetime.datetime.strptime(motherDeath, "%Y-%m-%d"):
                            doError("FAMILY: US09: " + fam.id + ": Child " + indi.id + " born " + indi.birthday + " after death of mother " + fam.wife_id + " " + motherDeath)
    
    # US11 No Bigamy (Irakli)
    # Marriage should not occur during marriage to another spouse
    indis = {}
    for fam in mergedFamilies:
        if fam.wifeId in indis or fam.husbandId in indis:
            doError("Bigamy found in family id " + fam.id)
        else :
            indis[fam.wifeId] = 1
            indis[fam.husbandId] = 1

    # US13 Birth dates of siblings should be more than 8 months apart or less than 2 days apart
    # for each family, make sure that the birth dates of siblings are more than 8 months apart or less than 2 days apart
    for fam in mergedFamilies:
        if fam.children != []:
            for child in fam.children:
                for indi in individuals:
                    if indi.id == child:
                        # find the birthday of the child
                        childBirth = indi.birthday
                        # find the birthdays of the siblings
                        siblings = []
                        for sibling in fam.children:
                            if sibling != child:
                                for indi2 in individuals:
                                    if indi2.id == sibling:
                                        siblings.append(indi2.birthday)
                        # if the birthdays of the siblings greater than 2 days but less than 8 months apart, print an error
                        for sibling in siblings:
                            if (datetime.datetime.strptime(childBirth, "%Y-%m-%d") - datetime.datetime.strptime(sibling, "%Y-%m-%d")).days > 2 and (datetime.datetime.strptime(childBirth, "%Y-%m-%d") - datetime.datetime.strptime(sibling, "%Y-%m-%d")).days < 8*30:
                                doError("FAMILY: US13: " + fam.id + ": Sibling " + sibling + " born " + sibling + " more than 2 days apart from child " + child + " born " + childBirth)
    
    # US18 Siblings should not marry one another
    # for each family, make sure that the marriage of siblings should not occur
    for fam in mergedFamilies:
        if fam.children != []:
            for child in fam.children:
                for indi in individuals:
                    if indi.id == child:
                        # find the birthday of the child
                        childBirth = indi.birthday
                        # find the birthdays of the siblings
                        siblings = []
                        for sibling in fam.children:
                            if sibling != child:
                                for indi2 in individuals:
                                    if indi2.id == sibling:
                                        siblings.append(indi2.birthday)
                        # if the birthdays of the siblings are the same, print an error
                        for sibling in siblings:
                            if sibling == childBirth:
                                doError("FAMILY: US18: " + fam.id + ": Sibling " + sibling + " born " + sibling + " married to child " + child + " born " + childBirth)
    
    # US23 Unique name and birth date (Max) 
    # for each individual, make sure that everyone has a unique name
    for indi in individuals:
        for indi2 in individuals:
            if indi.name == indi2.name and indi.id != indi2.id:
                doError("INDIVIDUAL: US23: " + indi.id + ": " + indi.name + ": is the same name as " + indi2.id + ": " + indi2.name)

    return postvalidate(individuals, mergedFamilies)
def postvalidate(individuals, mergedFamilies):
    # US24 Unique families by spouses
    # No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file
    for fam in mergedFamilies:
      # US15 Fewer than 15 siblings (Irakli)
      # There should be fewere than 15 siblings in a family
        if len(fam.children) >= 15:
            doError("Too many siblings in family id " + fam.id)
        for fam2 in mergedFamilies:
            if fam.married == fam2.married and fam.husband_id == fam2.husband_id and fam.wife_id == fam2.wife_id and fam.id != fam2.id:
                doError("FAMILY: US24: " + fam.id + ": " + fam.married + ": " + fam.husband_id + " and " + fam.wife_id + ": are the same family")


    return individuals, mergedFamilies


def checkConsistency(individual, family):
    '''verifies that individual info is consistent with family info'''
    indiID = individual.id
    if indiID == family.husbandId or indiID == family.wifeId:
        return True
    for child in family.children:
        if indiID == child.id:
            return True
    doError("individual info is inconsistent with family info!")

def listOlderSpouses(families):
    '''checks if someone's spouse is at least twice their own age when they married'''
    L = []
    for fam in families:
        husband = fam._husbRef
        wife = fam._wifeRef
        husbandDiff = (datetime.datetime.strptime(fam.married, "%Y-%m-%d") - datetime.datetime.strptime(husband.birthday, "%Y-%m-%d")).days
        wifeDiff = (datetime.datetime.strptime(fam.married, "%Y-%m-%d") - datetime.datetime.strptime(wife.birthday, "%Y-%m-%d")).days
        if husbandDiff >= 2 * wifeDiff:
            L.append(fam.id)
            doListBuffer(f"{husband.name} ({husband.age}) is at least twice as old as {wife.name} ({wife.age})")
        elif wifeDiff >= 2 * husbandDiff:
            doListBuffer(f"{wife.name} ({wife.age}) is at least twice as old as {husband.name} ({husband.age})")
            L.append(fam.id)
    return L

def listRecentBirths(individuals, currentDate=None):
    '''returns individuals that were born in the last 30 days'''
    L = []
    now = datetime.datetime.today() if currentDate is None else currentDate
    for indi in individuals:
        if indi.birthday != "N/A" and indi.birthday != "" and indi.birthday != None:
            diff = (now - dateFromString(indi.birthday)).days
            if diff >= 0 and diff <= 30:
                L.append(indi.name)
    return L

def listRecentDeaths(individuals, currentDate=None):
    '''prints individuals that died in the last 30 days'''
    L = []
    now = datetime.datetime.today() if currentDate is None else currentDate
    for indi in individuals:
        if indi.death != "N/A" and indi.death != "" and indi.death != None:
            diff = (now - dateFromString(indi.death)).days
            if diff >= 0 and diff <= 30:
                L.append(indi.name)
    return L

def printer(individuals, families):
    # create a table of individuals and families using ljust to create whitespace and keep table aligned
    # 'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'
    print("INDIVIDUALS")
    print("ID".ljust(6), "Name".ljust(15), "Gender".ljust(7), "Birthday".ljust(15), "Age".ljust(4), "Alive".ljust(7), \
        "Death".ljust(15), "Children".ljust(15), "Spouse".ljust(15))

    for indi in individuals:
        print(str(indi.id).ljust(6), str(indi.name).ljust(15), str(indi.sex).ljust(7), str(indi.birthday).ljust(15), \
            str(indi.age).ljust(4), str(indi.isAlive).ljust(7), str(indi.death).ljust(15), str(indi.children).ljust(15), str(indi.spouse).ljust(15))

    # do the same for families with columns 'ID', 'Married', 'Divorced', 'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'
    print("\nFAMILIES")   
    print("ID".ljust(6), "Married".ljust(15), "Divorced".ljust(15), "Husband ID".ljust(15), "Husband Name".ljust(15), \
        "Wife ID".ljust(15), "Wife Name".ljust(15), "Children".ljust(15))
    for fam in families:
        print(str(fam.id).ljust(6), str(fam.married).ljust(15), str(fam.divorced).ljust(15), str(fam.husbandId).ljust(15), \
            str(fam.husbandName).ljust(15), str(fam.wifeId).ljust(15), str(fam.wifeName).ljust(15), str(fam.children).ljust(15))

    # print all in listBuffer
    for item in listBuffer:
        print(item)
    
    # print all in errorBuffer
    for item in errorBuffer:
        print(item)
