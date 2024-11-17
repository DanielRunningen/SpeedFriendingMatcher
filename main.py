from app_config import Config
from argparse import ArgumentParser
from colorama import Fore, init, Style
from pandas import read_csv
from person import Person
from typing import Dict

# Start color output
init()
print(Style.RESET_ALL, end = '')

def import_results(csv_path: str, config: Config) -> Dict[str, Person]:
   # Load in the CSV of response data and remove the n/a values
   df = read_csv(
      csv_path,
      sep = ',',
      quotechar = '"',
      skipinitialspace = True,
      engine = 'python',
      encoding = 'latin1').fillna('')

   # Find all of the people who registered for the event
   registrants = config.create_map('find_name', list(df.columns))
   # Simplify the columns with each of their names
   df.rename(columns = registrants, inplace = True)
   # Save the names for later reporting
   registrants = set(registrants.values())

   # Find all the contact methods we are collecting
   contacts = config.create_map('contact_methods', list(df.columns))
   # Simplify those columns too...
   df.rename(columns = contacts, inplace = True)
   # Save this for people construction
   contacts = set(contacts.values())

   # Find simplify the names of all the other stuff we care about
   df.rename(
      columns = {
         config.find_match('participant_name', list(df.columns)): 'name',
         config.find_match('participant_gender', list(df.columns)): 'gender',
         config.find_match('participant_orientation', list(df.columns)): 'orientation',
      },
      inplace = True
   )

   # Remove duplicate entries
   most_recent = df.groupby(['name', 'email'])['Timestamp'].idxmax().reset_index()
   df = df.merge(most_recent, how = 'left', on = ['name', 'email'])
   df = df.query('index == Timestamp_y')
   df = df.drop(columns = ['Timestamp_x', 'Timestamp_y'])

   # Format the phone numbers, if they exist.
   if 'phone' in list(df.columns):
      def format_phone(raw: str) -> str:
         if raw == '':
            return raw
         results = config.patterns['phone_number'].extract_match(raw, all = True)
         if results:
            return f'({results[0]}) {results[1]}-{results[2]}'
         else:
            print(
               f'{Fore.YELLOW}{Style.BRIGHT}WARN: phone number `{Fore.MAGENTA}'
               f'{raw}{Fore.YELLOW}` is incomplete {Style.RESET_ALL}')
            return raw
      df['phone'] = df['phone'].apply(lambda r: format_phone(r))

   # Make the independent People objects
   records = df.to_dict('records')
   people = [Person(r, contacts, registrants) for r in records]
   people = {p.name: p for p in people}

   # Give some diagnostic data about the survey results
   print(
      f'{Style.BRIGHT}INFO:{Style.NORMAL} There were {Fore.GREEN}'
      f'{len(registrants)}{Style.RESET_ALL} event participants and '
      f'{Fore.GREEN if len(registrants) == len(people) else Fore.YELLOW}'
      f'{len(people)}{Style.RESET_ALL} survey respondents.')

   # Do all of the exchanges for everyone
   for _, p in people.items():
      p.eval_matches(people)

   # Print diagnostic data
   print(
      f'{Style.BRIGHT}INFO:{Style.NORMAL} The following people did not take the'
      f' survey:\n   {Style.RESET_ALL}-',
      '\n   - '.join([f'`{name.title()}`'
         for name in registrants
            if name not in people]))

   unmatched = [n for n, p in people.items() if (len(p.friends) + len(p.dates) + len(p.both)) < 1]
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

   # Send back the finished objects
   return people


# Execute the program
if __name__ == '__main__':
   parser = ArgumentParser()
   parser.add_argument(
      'csv_path',
      type = str,
      help = 'The name and path of the CSV data to compute.'
   )
   parser.add_argument(
      'config_path',
      type = str,
      help = 'The name and path of the JSON file to reference for advanced ' \
         + 'configuration.'
   )
   parser.add_argument(
      '-o', '--out_file',
      dest = 'out_file',
      type = str,
      default = 'results',
      help = 'The base filename for the exported data. Do not include the ' \
         + 'extension, this is controlled by the -t option.'
   )
   parser.add_argument(
      '-t', '--out_type',
      dest = 'out_type',
      type = str,
      choices = ['csv', 'txt'],
      default = 'csv',
      help = 'The file type for output. The default outputs a CSV.'
   )
   args = parser.parse_args()
   config = Config(args.config_path)
   people = import_results(args.csv_path, config)

   # Prepare the output file
   with open(f'{args.out_file}.{args.out_type}', 'w') as output:
      output.write('Name,Email Address,Message\n')
      for name, p in people.items():
         output.write(f'{name},{p.email},"{p.compose(people, config)}"\n')
