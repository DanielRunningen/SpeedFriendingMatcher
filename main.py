from person import Person
import sys
import pandas as pd
import re
import itertools

def main(csv: str) -> None:
    # Load in the CSV of response data and remove the n/a values
    df = pd.read_csv(csv)
    df = df.fillna("")

    # Identify methods of contact and people available for matching
    methods_q = dict()
    friends_q = dict()
    for q in list(df.columns):
        match = None
        match = re.match(r".*\[([^\]]+)\]", q)
        if match:
            friends_q[q] = match.group(1).lower()
        else:
            match = re.match(r"(email|facebook|discord|phone|meetup)", q.lower())
            if match:
                methods_q[q] = match.group(1).lower()

    # Replace the column headers with more reasonable ones
    df.rename(columns=methods_q, inplace=True)
    df.rename(columns=friends_q, inplace=True)

    # Convert the question dictionaries into simple lists
    methods_q = methods_q.values()
    friends_q = friends_q.values()

    # Convert the table data into Person objects
    # Organizing them with their name as their reference point in the dictionary
    #   is redundant information but makes life easier later
    people = dict()
    for i in df.index:
        person = Person(df["Name"][i].lower())
        for method in methods_q:
            if df[method][i] != "":
                person.add_contact_method(method, df[method][i])
        for friend in friends_q:
            if df[friend][i] == "Yes":
                person.add_potential_friend(friend)
        people[person.name] = person

    # Calculate the matches
    for person in people.values():
        for potential_freind in person.potential_friends:
            if potential_freind in people.keys() and person.name in people[potential_freind].potential_friends and person.name != potential_freind:
                people[person.name].add_mutual_friend(potential_freind)
                people[potential_freind].add_mutual_friend(person.name)

    # Print the emails
    for person in people.values():
        print(
            "SEND TO:\t"
            + person.contact_methods['email']
            + "\n\nHello!\n\nThanks for joining ***REMOVED*** for our Virtual Speed Friending event!"
            + "  Below are the people that would like to make a friend connection with you and the ways in which they preferred to be contacted."
            + "  If you have further questions don’t hesitate to reach out to ***REMOVED*** on facebook, meetup, or discord (***REMOVED***).\n\n"
        )

        for friend in person.mutual_friends:
            print(people[friend].name.title() + "\n-----")
            for method, handle in people[friend].contact_methods.items():
                print(method.title() + ": " + str(handle))
            print("\n")

        print("-----------------------\n\n\n\n")

# Execute the program
if len(sys.argv) < 2:
    print("Useage:\n\tpython3 {0} my_input.csv\n".format(sys.argv[0]))
else:
    main(sys.argv[1])
