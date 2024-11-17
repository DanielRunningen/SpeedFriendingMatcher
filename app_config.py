from app_pattern import Pattern
from json import load
from helpers import check_keys
from typing import Dict, List

class Config:
   def __init__(self, path: str) -> None:
      # Load the configs from the path provided.
      with open(path, 'r') as f:
         json = load(f)

      # Save all the patterns
      check_keys(json, ['patterns', 'messages'], path)
      self.patterns = {p['for']: Pattern(p) for p in json['patterns']
                       if check_keys(p, ['for'], 'patterns')}

      # Save the messages
      check_keys(json['messages'], ['matched', 'no_match'], 'messages')
      self.matched = json['messages']['matched']
      self.no_match = json['messages']['no_match']

      # Make sure all the necessary patterns exist
      check_keys(
         self.patterns,
         ['participant_name', 'find_name', 'contact_methods', 'phone_number'],
         'patterns')

   def create_map(self, pattern: str, strings: List[str]) -> Dict[str, str]:
      return {
         c: self.patterns[pattern].extract_match(c)
            for c in self.find_all(pattern, strings)}

   def find_all(self, pattern: str, strings: List[str]) -> str:
      return [s for s in strings if self.patterns[pattern].match_exists(s)]

   def find_match(self, pattern: str, strings: List[str]) -> str | None:
      for s in strings:
         if self.patterns[pattern].match_exists(s):
            return s
      return None
