# import the program code and execute it
from src import *

lines = runLinter()
individuals, families = runParser(lines)
printer(individuals, families)
