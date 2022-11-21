from colorama import Fore, init, Style
import json
from pandas import read_csv
from person import Person
from re import compile, match, split
from sys import argv, exit

def main(config: str) -> None:
   # Start color output
   init()
   print(Style.RESET_ALL, end='')

   # Load the configs
   with open(config, 'r') as f:
      config = json.load(f)

   # Make sure all the required keys are there
   for key in ['csv_path', 'name_column_header', 'regex', 'messages']:
      if key not in config:
         exit(
            f'{Fore.RED}{Style.BRIGHT}ERROR{Style.NORMAL}: Missing '
            f'`{Fore.MAGENTA}{key}{Fore.RED}` key in config file, '
            f'aborting{Style.RESET_ALL}')

   for k, v in {
      'find_name': 'regex',
      'contact_methods': 'regex',
      'matched': 'messages',
      'not_matched': 'messages'
   }.items():
      if k not in config[v]:
         exit(
            f'{Fore.RED}{Style.BRIGHT}ERROR{Style.NORMAL}: Missing '
            f'`{Fore.MAGENTA}{k}{Fore.RED}` key in the `{Fore.MAGENTA}{v}'
            f'{Fore.RED}` section of the config, aborting{Style.RESET_ALL}')

   for k in ['pre', 'post']:
      if k not in config['messages']['matched']:
         exit(
            f'{Fore.RED}{Style.BRIGHT}ERROR{Style.NORMAL}: Missing '
            f'`{Fore.MAGENTA}{k}{Fore.RED}` key in the `{Fore.MAGENTA}matched'
            f'{Fore.RED}` section of the config, aborting{Style.RESET_ALL}')

   # Load in the CSV of response data and remove the n/a values
   df = read_csv(
      config['csv_path'],
      sep=',',
      quotechar='"',
      skipinitialspace=True,
      engine='python',
      encoding='latin1').fillna('')

   if config['name_column_header'] not in df:
      exit(
         f'{Fore.RED}{Style.BRIGHT}ERROR{Style.NORMAL}: No column found '
         f"with the header `{Fore.MAGENTA}{config['name_column_header']}"
         f'{Fore.RED}`, aborting{Style.RESET_ALL}')

   # Make the cases consistent for all the names
   df[config['name_column_header']] = \
      df[config['name_column_header']].str.lower()

   # These forms can get confusing, but columns belong to a couple categories
   # Primarily, this will find the people columns and contact columns
   column_categories = ['find_name', 'contact_methods', 'identity_fields', 'interests']
   column_qs = {k: dict() for k in column_categories}
   for q in list(df.columns):
      for c in column_categories:
         if c in config['regex']:
            result = match(compile(config['regex'][c]), q.lower())
            if result:
               column_qs[c][q] = result.group(1).lower()
               break

   for c in column_categories:
      # Replace the column headers with more reasonable ones
      df.rename(columns=column_qs[c], inplace=True)
      # Convert the question dictionaries into simple sets
      column_qs[c] = set(column_qs[c].values())

   # Give some diagnostic data about the survey results
   print(
      f'{Style.BRIGHT}INFO:{Style.NORMAL} There were {Fore.GREEN}'
      f'{len(column_qs["find_name"])}{Style.RESET_ALL} event participants and '
      f'{Fore.GREEN if len(column_qs["find_name"]) == df.shape[0] else Fore.YELLOW}'
      f'{df.shape[0]}{Style.RESET_ALL} survey respondents.')

   # Fix the name column...
   df[config['name_column_header']] = df[config['name_column_header']].str.strip()

   # Convert the table data into Person objects
   # Organizing them with their name as their reference point in the
   #   dictionary. It's redundant information but makes life easier later
   people = dict()
   for i in df.index:
      # Warn for folks whose names weren't in the column headers and skip them
      #   The won't match with anyone if the name wasn't a column header
      responder = df[config['name_column_header']][i]
      if responder not in column_qs['find_name']:
         print(
            f'{Fore.YELLOW}{Style.BRIGHT}WARN:{Style.NORMAL} The name '
            f'`{Fore.MAGENTA}{responder.title()}{Fore.YELLOW}` does not match '
            'any names from the form. This person won\'t be matched!\nIs it '
            f'possible they were one of these people?:\n   {Style.RESET_ALL}-',
            '\n   - '.join([name.title()
               for name in sorted(list(column_qs['find_name']))
                  if responder in name]))
      else: # Their name was in a column, so they should be good
         # Make the new Person object with the validated name
         person = Person(responder)
         # Add all the contact methods they listed for themselves
         for method in column_qs['contact_methods']:
            if df[method][i] != '':
               # Everyone writes phone numbers differently, so check that it
               #   will work, then standardize them
               if method == 'phone':
                  result = match(
                     compile(config['regex']['phone_number']),
                     df[method][i])
                  if result:
                     person.add_contact_method(
                        method, 
                        '(' + result.group(1) + ') ' + result.group(2) + '-' \
                           + result.group(3))
                  else:
                     print(
                        f'{Fore.YELLOW}{Style.BRIGHT}WARN:{Style.NORMAL} '
                        f'{Fore.MAGENTA}{person.name.title()}{Fore.YELLOW} gave'
                        f' malformed contact information for `{Fore.MAGENTA}'
                        f'{method}{Fore.YELLOW}`: `{Fore.MAGENTA}'
                        f'{df[method][i]}{Fore.YELLOW}`{Style.RESET_ALL}')
               else: # Assume they entered the information correctly
                  person.add_contact_method(method, df[method][i])
         # Save all the names of the people this person likes
         for friend in column_qs['find_name']:
            if df[friend][i] == 'Yes':
               person.add_potential_friend(friend)
         # Add their identities, if that is what we are doing
         if 'identity_delim' in config['regex']:
            for c in column_qs['identity_fields']:
               person.add_identities(set(split(
                  compile(config['regex']['identity_delim']),
                  df[c][i])))
         # Add interest, if that's a thing.
         for c in column_qs['interests']:
            # I know this is ugly, and it needs fixing, just not right now.
            person.desired_relationship = df[c][i].lower()
            break
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

   if 'output_path' in config:
      filename = config['output_path']
   else:
      print(
         f'{Fore.YELLOW}{Style.BRIGHT}WARN:{Style.NORMAL} No `{Fore.MAGENTA}'
         f'output_path{Fore.YELLOW}` given in config, sending results to '
         f'`{Fore.MAGENTA}out.txt{Fore.YELLOW}`{Style.RESET_ALL}')
      filename = 'out.txt'

   # Prepare to report the people unmatched.
   unmatched = []

   # Prepare the output file
   with open(filename, 'w') as output:
      # Print the emails
      for name, person in people.items():
         output.write(
            f"***SEND TO: \t{person.contact_methods['email']}\t***\n\n\n")
         if len(person.mutual_friends) > 0:
            output.write(f"{config['messages']['matched']['pre']}\n")
            for friend in person.mutual_friends:
               output.write(f'\n\n{people[friend].name.title()}\n---\n')
               if len(people[friend].identities) > 0:
                  output.write('Identities: ' \
                     + ', '.join(list(people[friend].identities)) + '\n')
               if people[friend].desired_relationship:
                  output.write(
                     f'{people[friend].name.title()} ' \
                     + 'came to the event because they are interested in '
                     + f'{people[friend].desired_relationship}.\n---\n')
               for method, handle in people[friend].contact_methods.items():
                  output.write(f'{method.title()}: {str(handle)}\n')
            output.write(f"{config['messages']['matched']['post']}\n")
         else:
            unmatched.append(name.title())
            output.write(config['messages']['not_matched'])

   # Print diagnostic data
   print(
      f'{Style.BRIGHT}INFO:{Style.NORMAL} The following people did not take the'
      f' survey:\n   {Style.RESET_ALL}-',
      '\n   - '.join([name.title()
         for name in sorted(list(column_qs['find_name']))
            if name not in people]))

   n = len(unmatched)
   if n > 0:
      print(
         f'{Style.BRIGHT}INFO: {Fore.YELLOW}{n}{Fore.RESET}{Style.NORMAL} '
         f"{'people were' if n > 1 else 'person was'} not matched:\n   -"
         f"{Style.RESET_ALL}",
         '\n   - '.join(sorted(unmatched)))
   else:
      print(
         f'{Style.BRIGHT}INFO:{Style.NORMAL} {Fore.GREEN}Congrats! Everyone had'
         f' at least one match!{Style.RESET_ALL}')

# Execute the program
if __name__ == '__main__':
   if len(argv) < 2:
     exit(f'usage:\tpython3 {argv[0]} config.json\n')
   else:
      main(argv[1])
