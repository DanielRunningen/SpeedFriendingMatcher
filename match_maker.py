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
   df = pd.read_csv(config['csv_path'])
   df = df.fillna("")

   # Make the cases consistent for all the names
   df[config['name_column_header']] = df[config['name_column_header']].str.lower()

   # Identify methods of contact and people available for matching
   methods_q = dict()
   friends_q = dict()
   for q in list(df.columns):
      match = re.match(re.compile(config['regex']['find_name']), q)
      if match:
         friends_q[q] = match.group(1).lower()
         continue
      match = re.match(
         re.compile(config['regex']['contact_methods']),
         q.lower()
      )
      if match:
         methods_q[q] = match.group(1).lower()

      # While I'm here, also strip leading and trailing whitespaces.
      df[q] = df[q].str.strip()

   # Replace the column headers with more reasonable ones
   df.rename(columns=methods_q, inplace=True)
   df.rename(columns=friends_q, inplace=True)

   # Convert the question dictionaries into simple sets
   methods_q = set(methods_q.values())
   friends_q = set(friends_q.values())

   # Give some diagnostic data about the survey results
   print(
      f"There were {len(friends_q)} event participants and {df.shape[0]}",
      "survey respondants"
   )

   # Convert the table data into Person objects
   # Organizing them with their name as their reference point in the
   #   dictionary. It's redundant information but makes life easier later
   people = dict()
   for i in df.index:
      # Warn for folks whose names weren't in the column headers and skip them
      #   The won't match with anyone if the name wasn't a column header
      if df[config['name_column_header']][i] not in friends_q:
         print(
            f"WARN: The name `{df[config['name_column_header']][i]}`",
            "does not match any names from the list below.",
            "This person won't be matched!\n",
            list(friends_q).sort()
         )
      else: # Their name was in a column, so they should be good
         # Make the new Person object with the validated name
         person = Person(df[config['name_column_header']][i])
         # Add all the contact methods they listed for themselves
         for method in methods_q:
            if df[method][i] != "":
               # Everyone writes phone numbers differently, so check that it
               #   will work, then standardize them
               if method == "phone":
                  match = re.match(
                     re.compile(config['regex']['phone_number']),
                     df[method][i]
                  )
                  if match:
                     person.add_contact_method(
                        method, 
                        "(" + match.group(1) + ") " + match.group(2) + "-" \
                           + match.group(3)
                     )
                  else:
                     print(
                        f"{person.name.title()} gave malformed contact",
                        f"information for `{method}`: `{df[method][i]}`"
                     )
               else: # Assume they entered the information correctly
                  person.add_contact_method(method, df[method][i])
         # Save all the names of the people this person likes
         for friend in friends_q:
            if df[friend][i] == "Yes":
               person.add_potential_friend(friend)
         # Add the person to the dictionary to look-up later
         people[person.name] = person

   # Calculate the matches
   for person in people.values():
      for potential_friend in person.potential_friends:
         if potential_friend in people.keys() \
            and person.name in people[potential_friend].potential_friends \
            and person.name != potential_friend \
         :
            people[person.name].add_mutual_friend(potential_friend)
            people[potential_friend].add_mutual_friend(person.name)

   # Prepare the output file
   output = open(config['output_path'], "w")

   # Print the emails
   for person in people.values():
      output.write(
         "***SEND TO:\t" + person.contact_methods['email'] + "\t***\n\n\n"
      )
      if len(person.mutual_friends) > 0:
         output.write(config['messages']['matched']['pre'] + "\n")
         for friend in person.mutual_friends:
            output.write("\n\n" + people[friend].name.title() + "\n---\n")
            for method, handle in people[friend].contact_methods.items():
               output.write(method.title() + ": " + str(handle) + "\n")
         output.write(config['messages']['matched']['post'] + "\n")
      else:
         output.write(config['messages']['not_matched'])

   # Close the output file nicely
   output.close()

# Execute the program
if __name__ == '__main__':
   if len(sys.argv) < 2:
     sys.stdout.write(f"usage:\tpython3 {sys.argv[0]} config.json\n")
   else:
      main(sys.argv[1])
