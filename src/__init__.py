import fileinput
import csv
import os

tagNames = []

with open(os.path.realpath(__file__+ "/..") + '/tags.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    next(csvfile)
    for row in reader:
        tagNames.append(row[1])

def isValidTag(tag):
    return tag in tagNames

class ParsedGEDCOM:
    def __init__(self, line):
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

    def __str__(self):
        return str(self.level) + "|" + self.tag + "|" + ("Y" if self.valid else "N") + "|" + " ".join(self.args)

def runLinter():
    # Read from standard input and return an array of ParsedGEDCOM objects
    lines = []
    for line in fileinput.input():
        # print(ParsedGEDCOM(line))
        lines.append(ParsedGEDCOM(line))
    return lines

# Max's Additions

class Individual:
    def __init__(self, id, level):
        self.id = id
        self.level = level
        self.name = "N/A"
        self.sex = "N/A"
        self.birthday = "N/A"
        self.age = "N/A"
        self.isAlive = "N/A"
        self.death = "N/A"
        self.children = []
        self.spouse = "N/A"

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

def runParser(lines):
    # Return a list of individuals and a list of families based on tags
    families = []
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
                    individuals[-1].name = line.args[0]
                elif line.tag == "SEX":
                    individuals[-1].sex = line.args[0]
                elif line.tag == "BIRT":
                    i+=1
                    individuals[-1].birthday = lines[i].args[0]
                elif line.tag == "DEAT":
                    i+=1
                    individuals[-1].death = lines[i].args[0]
                elif line.tag == "FAMC":
                    # search families for args[0], in the family add to children
                    for fam in families:
                        if fam.id == line.args[0]:
                            individuals[-1].children.append(fam)
                elif line.tag == "FAMS":
                    # search families for args[0], in the family add to husband/wife based on individuals[-1].sex
                    for fam in families:
                        if fam.id == line.args[0]:
                            if individuals[-1].sex == "M":
                                fam.husbandId = individuals[-1].id
                                # may need to add individuals[-1].wife by accessing fam
                            else:
                                fam.wifeId = individuals[-1].id
                                # may need to add individuals[-1].husband by accessing fam
                elif line.tag == "Head" or line.tag == "NOTE":
                    pass
                else:
                    break
        elif line.tag == "FAM":
            families.append(Family(line.args[0]))
            # Nested loop required as subsequent lines give information about the family
            # For marriage and divorce the next line holds the date value so i must be incremented
            for i in range(i+1, len(lines)):
                line = lines[i]
                if line.tag == "MARR":
                    i+=1
                    families[-1].married = lines[i].args[0]
                elif line.tag == "DIV":
                    i+=1
                    families[-1].divorced = lines[i].args[0]
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
                elif line.tag == "Head" or line.tag == "NOTE":
                    pass
                else:
                    break
        else:
            pass
    return individuals, families

def printer(individuals, families):
    # convert over to prettyTable format later
    # indiTable = PrettyTable(field_names=['ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
    # replace print with indiTable.add_row
    print("Individuals")
    for indi in individuals:
        print([indi.id, indi.name, indi.sex, indi.birthday, indi.age, indi.isAlive, indi.death, indi.children, indi.spouse])

    # famTable = PrettyTable(field_names=['ID', 'Married', 'Divorced', 'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'])
    print("\nFamilies")
    for fam in families:
        print([fam.id, fam.married, fam.divorced, fam.husband_id, fam.husband_name, fam.wife_id, fam.wife_name, fam.children])
