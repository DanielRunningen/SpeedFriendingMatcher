from person import Person
import sys
import json
import pandas as pd
import re

def main(config: str) -> None:
    # Load the configs
    config_file = open(config, "r")
    config = json.load(config_file)
    config_file.close()

    # Load in the CSV of response data and remove the n/a values
    df = pd.read_csv(config["csv_path"])
    df = df.fillna("")

    # Identify methods of contact and people available for matching
    methods_q = dict()
    friends_q = dict()
    for q in list(df.columns):
        match = re.match(re.compile(config["regex"]["find_name"]), q)
        if match:
            friends_q[q] = match.group(1).lower()
            continue
        match = re.match(re.compile(config["regex"]["contact_methods"]), q.lower())
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
                if method == "phone":
                    person.add_contact_method(method, str(int(df[method][i])))
                else:
                    person.add_contact_method(method, df[method][i])
        for friend in friends_q:
            if df[friend][i] == "Yes":
                person.add_potential_friend(friend)
        people[person.name] = person

    # Calculate the matches
    for person in people.values():
        for potential_friend in person.potential_friends:
            if potential_friend in people.keys()
                and person.name in people[potential_friend].potential_friends
                and person.name != potential_friend:
                
                people[person.name].add_mutual_friend(potential_friend)
                people[potential_friend].add_mutual_friend(person.name)

    # Prepare the output file
    output = open(config["output_path"], "w")

    # Print the emails
    for person in people.values():
        output.write("***SEND TO:\t" + person.contact_methods['email'] + "\t***\n\n\n")

        if len(person.mutual_friends) > 0:
            output.write(config["messages"]["matched"]["pre"] + "\n")
            for friend in person.mutual_friends:
                output.write("\n\n" + people[friend].name.title() + "\n-----\n")
                for method, handle in people[friend].contact_methods.items():
                    output.write(method.title() + ": " + str(handle))
            output.write(config["messages"]["matched"]["post"] + "\n")
        else:
            output.write(config["messages"]["not_matched"])
    
    # Close the output file nicely
    output.close()

# Execute the program
if len(sys.argv) < 2:
    sys.stdout.write(f"useage:\tpython3 {sys.argv[0]} config.json\n")
else:
    main(sys.argv[1])
