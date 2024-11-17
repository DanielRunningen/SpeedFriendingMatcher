from colorama import Fore, init, Style
from enum import Enum
from helpers import check_keys
from re import IGNORECASE, match
from typing import Dict, List

# Start color output
init()
print(Style.RESET_ALL, end = '')

class MatchMethod(Enum):
   REGEX = 'regex'
   SUBSTRING = 'substring'
   STARTS_WITH = 'starts with'
   ENDS_WITH = 'ends with'
   EXACT = 'exact'

   def __eq__(self, value: str) -> bool:
      return self.value == value

class Pattern:
   def __init__(self, json: Dict[str, str]) -> None:
      check_keys(
         json,
         ['query', 'method', 'case_sensitive'], 
         f'patterns.{json["for"]}')
      self.method = json['method']
      self.case_sensitive = json['case_sensitive']
      self.query = json['query'] \
         if json['method'] == MatchMethod.REGEX or json['case_sensitive'] \
            else json['query'].lower()

   # Check to see if a string matches the pattern.
   def match_exists(self, text: str) -> bool:
      text_str = text if self.case_sensitive else text.lower()
      match self.method:
         case MatchMethod.REGEX:
            return self.extract_match(text_str) is not None
         case MatchMethod.SUBSTRING:
            return self.query in text_str
         case MatchMethod.STARTS_WITH:
            return text_str.startswith(self.query)
         case MatchMethod.ENDS_WITH:
            return text_str.endswith(self.query)
         case MatchMethod.EXACT:
            return self.query == text_str

   # Extracts the match from a regex pattern, when available.
   def extract_match(self, text: str, all: bool = False) -> str | List[str] | None:
      if self.method != MatchMethod.REGEX:
         exit(
            f'{Fore.RED}{Style.BRIGHT}ERROR{Style.NORMAL}: Matching method '
            f'`{Fore.MAGENTA}{self.method}{Fore.RED}` does not support content '
            f'extraction. Please use `regex` instead and try again.'
            f'{Style.RESET_ALL}')
      # Make sure the case sensitivity is respected.
      text_str = text if self.case_sensitive else text.lower()
      # Do the search.
      result = match(
         self.query,
         text_str,
         flags = 0 if self.case_sensitive else IGNORECASE)
      # Return the result.
      if result:
         if all:
            return result.groups()
         else:
            return result.group(1) \
               if self.case_sensitive else result.group(1).lower()
      # Return `None` if we don't find anything.
      return None
