from typing import Set

class Person:
    def __init__(self, name: str) -> None:
        self.name = name
        self.contact_methods = dict()
        self.potential_friends = set()
        self.mutual_friends = set()
        self.desired_relationship = None
        self.identities = set()

    def add_contact_method(self, method: str, identifier: str) -> None:
        self.contact_methods[method] = identifier

    def add_potential_friend(self, person_name: str) -> None:
        self.potential_friends.add(person_name)

    def add_mutual_friend(self, person_name: str) -> None:
        self.mutual_friends.add(person_name)

    def add_identity(self, identity: str) -> None:
        if identity != '': self.identities.add(identity)

    def add_identities(self, identities: Set[str]) -> None:
        identities.discard('')
        self.identities = self.identities.union(identities)
