from colorama import Fore, init, Style
from typing import Dict, List

# Start color output
init()
print(Style.RESET_ALL, end = '')

def check_keys(obj: Dict[str, any], keys: List[str], name: str) -> bool:
   # Make sure all the required keys are there
   for key in keys:
      if key not in obj:
         exit(
            f'{Fore.RED}{Style.BRIGHT}ERROR{Style.NORMAL}: Missing '
            f'`{Fore.MAGENTA}{key}{Fore.RED}` key in `{Fore.MAGENTA}{name}'
            f'{Fore.RED}`, aborting{Style.RESET_ALL}')
   return True
