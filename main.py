from person import Person
import numpy as np
import pandas as pd
import re

def main(csv: str) -> None:
    df = pd.read_csv(csv)
    df = df.fillna("")
    
    people = list()
    names = list()

    for header in list(df.columns):
        match = None
        match = re.match(r".*\[(\w+)\]", header)
        if match:
            names.append(match.group(1).lower())

    for i, record in df.iterrows():
        person = Person(record["Name"].lower())
        person.add_contact_method("Email", record["Email Address"])
        if record["facebook username (what you use in ***REMOVED***):"] != "":
            person.add_contact_method("Facebook", record["facebook username (what you use in ***REMOVED***):"])
        if record["discord username (include digits at end of username - ex. #1234):"] != "":
            person.add_contact_method("Discord", record["discord username (include digits at end of username - ex. #1234):"])
        if record["phone number for texing (include area code):"] != "":
            person.add_contact_method("Phone", int(record["phone number for texing (include area code):"]))
        if record["meetup username:"] != "":
            person.add_contact_method("Meetup", record["meetup username:"])

        for j, question in enumerate(list(df.columns)[3:-4]):
            if record[question] == "Yes":
                person.add_person_of_intrest(names[j])

        people.append(person)

    for i, pi in enumerate(people):
        for j, pj in enumerate(people[i+1:]):
            if pj.name.lower() in pi.people_of_interest and pi.name.lower() in pj.people_of_interest:
                pi.people_of_shared_interest.add(pj.name.lower())
                pj.people_of_shared_interest.add(pi.name.lower())

    for p in people:
        print(p.name)
        print(p.methods_of_contact)
        print(p.people_of_interest)
        print(p.people_of_shared_interest)
        print()

main("test_data.csv")
