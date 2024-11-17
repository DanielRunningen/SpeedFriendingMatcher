from app_config import Config
from helpers import check_keys
from typing import Dict, List

class Dynamic:
   def __init__(self, target: str, sentiment: str) -> None:
      self.target = target
      self.friend = sentiment in ['Friendship', 'Open to either']
      self.date = sentiment in ['Dating', 'Open to either']
      self.type = None

   def exchange(self, other: 'Dynamic') -> None:
      # Only need to do this once for each
      if self.type and other.type:
         return
      # Chose the category
      if self.friend and other.friend: # f+f, f+b, b+b
         if self.date and other.date:  # b+b
            self.type = other.type = 'both'
         else:                         # f+f, f+b
            self.type = other.type = 'friend'
      elif self.date and other.date:   # d+d, d+b
         self.type = other.type = 'date'
      else:                            # f+d -> no match?
         self.type = other.type = 'none'

class Person:
   def __init__(
      self,
      record: Dict[str, str],
      contact_methods: List[str],
      people: List[str]
   ) -> None:
      check_keys(record, ['name', 'email', 'gender', 'orientation'], 'record')
      self.name = record['name']
      self.email = record['email']
      self.contact_methods = {
         m: record[m] for m in contact_methods if len(record[m]) > 0 }
      self.identities = record['gender'].split(',') + record['orientation'].split(',')
      self.potentials = {
         k: Dynamic(k, v) for k, v in record.items() \
            if k in people and v != 'Not interested'}
      self.friends = []
      self.dates = []
      self.both = []
      self.mismatch = []

   def __eq__(self, other: 'Person') -> bool:
      return self.name == other.name and self.email == other.email

   def __hash__(self) -> int:
      return hash(self.name) * hash(self.email)

   def __repr__(self) -> str:
      return f'Name: {self.name}, Email: {self.email}\n\t' \
         + f'f: {len(self.friends)}, d: {len(self.dates)}, b: {len(self.both)}, n: {len(self.mismatch)}'

   def compose(self, others: Dict[str, 'Person'], config: Config) -> str:
      if len(self.potentials) > 0:
         msg = f'{config.matched}'
         if len(self.friends) > 0:
            msg += '\n\n----- Friend Matches -----\n\n'
            msg += '\n\n'.join([others[f].profile() for f in self.friends])
         if len(self.dates) > 0:
            msg += '\n\n----- Date Matches -----\n\n'
            msg += '\n\n'.join([others[d].profile() for d in self.dates])
         if len(self.both) > 0:
            msg += '\n\n----- Friend OR Date Matches -----\n\n'
            msg += '\n\n'.join([others[b].profile() for b in self.both])
         return msg
      else:
         return config.no_match

   def eval_matches(self, others: Dict[str, 'Person']) -> None:
      to_remove = []
      for name, p in self.potentials.items():
         if name in others and self.name in others[name].potentials:
            p.exchange(others[name].potentials[self.name])
         else:
            to_remove.append(name)
      for n in to_remove:
         self.potentials.pop(n, None)
      self.friends = [name for name, p in self.potentials.items() if p.type == 'friend']
      self.dates = [name for name, p in self.potentials.items() if p.type == 'date']
      self.both = [name for name, p in self.potentials.items() if p.type == 'both']
      self.mismatch = [name for name, p in self.potentials.items() if p.type == 'none']

   def profile(self) -> str:
      return f'{self.name}\n---\nIdentities: { \
            ", ".join(self.identities) if len(self.identities) > 0 else "None specified" \
         }\n' + '\n'.join([f'{k}: {v}' for k, v in self.contact_methods.items()])
