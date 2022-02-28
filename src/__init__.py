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
    # Read from standard input
    for line in fileinput.input():
        print("<-- " + line.strip())
        parsed = ParsedGEDCOM(line)
        print("--> " + str(parsed))
        pass