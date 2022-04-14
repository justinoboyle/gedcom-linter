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
