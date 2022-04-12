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

def runLinter():
    # Read from standard input and return an array of ParsedGEDCOM objects
    lines = []
    for line in fileinput.input():
        # print(ParsedGEDCOM(line))
        lines.append(ParsedGEDCOM(line))
    return lines

class Individual:
    def __init__(self, id, level):
        self.id = id
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

    def setAge(self, age):
        if age >= 150:
            raise Exception("Age must be less than 130!")
        self.age = age

    def validateBirthDeath(self):
        if self.birthday == "N/A" or self.death == "N/A":
            pass
        else:
            if dateFromString(self.birthday) > dateFromString(self.death):
                raise Exception("Birthday must be before death!")

    def setBirthday(self, birthday):
        self.birthday = birthday
        self.validateBirthDeath()

    def setDeath(self, death):
        self.death = death
        self.validateBirthDeath()


    def __str__(self):
         return self.id

    def __repr__(self):
        return self.id

class Family:
    def __init__(self, id):
        self.id = id
        self.married = "N/A"
        self.divorced = "N/A"
        self.husbandId = "N/A"
        self.husbandName = "N/A"
        self.wifeId = "N/A"
        self.wifeName = "N/A"
        self.children = []

    def addHusband(self, husband):
        if husband.family != "N/A":
            raise Exception("Husband already has a family!")
        self.husbandId = husband.id
        self.husbandName = husband.name

    def addChild(self, child):
        if dateFromString(self.married) > dateFromString(child.birthday):
            raise Exception("Child can't be born before parents were married!")
            
        # get last name of husbandName
        husbandLastName = self.husbandName.split(" ")[-1]
        # get last name of childName
        childLastName = child.name.split(" ")[-1]
        # if last name of husbandName == last name of childName
        if husbandLastName == childLastName:
            self.children.append(child.id)
        else:
            raise Exception("Last name of husband and child must match!")

    
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

def runParser(lines):
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
                                individuals[-1].spouse = fam
                                fam.husbandId = individuals[-1].id
                                fam.husbandName = individuals[-1].name
                            else:
                                individuals[-1].spouse = fam
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
                    families[-1].married = lines[i].args[0] + " " + lines[i].args[1] + " " + lines[i].args[2]
                elif line.tag == "DIV":
                    i+=1
                    families[-1].divorced = lines[i].args[0] + " " + lines[i].args[1] + " " + lines[i].args[2]
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
                        mergedFam.married = fam.married
                    if fam.divorced != "N/A":
                        mergedFam.divorced = fam.divorced
                    if fam.children != []:
                        mergedFam.children.extend(fam.children)
    
    # datetime.datetime.strptime(indi.birthday, "%Y-%m-%d")

    # get the age of each individual alive or dead
    for indi in individuals:
        if indi.isAlive:
            indi.setAge((datetime.datetime.today() - datetime.datetime.strptime(indi.birthday, "%Y-%m-%d")).days // 365)
        else:
            indi.setAge((datetime.datetime.strptime(indi.death, "%Y-%m-%d") - datetime.datetime.strptime(indi.birthday, "%Y-%m-%d")).days // 365)

    # US04 Marriage before divorce (Max)
    # for each family, make sure that the date of marriage is before the date of divorce
    for fam in mergedFamilies:
        if fam.married != "N/A" and fam.divorced != "N/A":
            if datetime.datetime.strptime(fam.married, "%Y-%m-%d") > datetime.datetime.strptime(fam.divorced, "%Y-%m-%d"):
                print("ERROR: FAMILY: US04: " + fam.id + ": Marriage occurs after divorce")

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
                            print("ERROR: FAMILY: US09: " + fam.id + ": Child " + indi.id + " born " + indi.birthday + " after death of father " + fam.husband_id + " " + fatherDeath)
                        if (motherDeath != "N/A") and datetime.datetime.strptime(indi.birthday, "%Y-%m-%d") > datetime.datetime.strptime(motherDeath, "%Y-%m-%d"):
                            print("ERROR: FAMILY: US09: " + fam.id + ": Child " + indi.id + " born " + indi.birthday + " after death of mother " + fam.wife_id + " " + motherDeath)

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
                                print("ERROR: FAMILY: US13: " + fam.id + ": Sibling " + sibling + " born " + sibling + " more than 2 days apart from child " + child + " born " + childBirth)
    # US23 Unique name and birth date (Max) 
    # for each individual, make sure that everyone has a unique name
    for indi in individuals:
        for indi2 in individuals:
            if indi.name == indi2.name and indi.id != indi2.id:
                print("ERROR: INDIVIDUAL: US23: " + indi.id + ": " + indi.name + ": is the same name as " + indi2.id + ": " + indi2.name)

    # US04 Marriage before divorce (Max)
    # for each family, make sure that the date of marriage is before the date of divorce
    for fam in mergedFamilies:
        if fam.married != "N/A" and fam.divorced != "N/A":
            if datetime.datetime.strptime(fam.married, "%Y-%m-%d") > datetime.datetime.strptime(fam.divorced, "%Y-%m-%d"):
                print("ERROR: FAMILY: US04: " + fam.id + ": Marriage occurs after divorce")

    # US23 Unique name and birth date (Max) 
    # for each individual, make sure that everyone has a unique name
    for indi in individuals:
        for indi2 in individuals:
            if indi.name == indi2.name and indi.id != indi2.id:
                print("ERROR: INDIVIDUAL: US23: " + indi.id + ": " + indi.name + ": is the same name as " + indi2.id + ": " + indi2.name)

    # US11 No Bigamy (Irakli)
    # Marriage should not occur during marriage to another spouse
    indis = {}
    for fam in mergedFamilies:
        if fam.wifeId in indis or fam.husbandId in indis:
            print('bigamy')
        else :
            indis[fam.wifeId] = 1
            indis[fam.husbandId] = 1

        # US15 Fewer than 15 siblings (Irakli)
        # There should be fewere than 15 siblings in a family
        if len(fam.children) >= 15:
            print("too many siblings")

    return individuals, mergedFamilies

