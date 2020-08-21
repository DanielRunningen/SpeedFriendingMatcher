class Person:
    def __init__(self, name: str) -> None:
        self.name = name
        self.methods_of_contact = dict()
        self.people_of_interest = set()
        self.people_of_shared_interest = set()

    def add_contact_method(self, method: str, identifier: str) -> None:
        self.methods_of_contact[method] = identifier

    def add_person_of_intrest(self, person_name: str) -> None:
        self.people_of_interest.add(person_name)

    def add_people_of_shared_interest(self, person_name: str) -> None:
        self.people_of_shared_interest.add(person_name)
