from botInterface import Payload
from files import get_file, save_file


class Tag():
    """Tags that can be added to building plans to give them different effects"""

    def __init__(self, category, name, attributes=[], statistics=[]):
        self.category = category
        self.name = name
        self.attributes = attributes
        self.statistics = statistics

    def __str__(self):
        return f'{self.name}: A {self.category} tag that conveys {self.attributes} and {self.statistics}'


class BuildingPlan():

    def __init__(self, name, owner, tags=[],
                 xy=None, celestial=None, territory=None):
        self.name = name
        self.owner = owner
        self.tags = tags  # ! probably need to change the tag list to a strings then unpickle
        self.construction_remaining = self.get_stat('UoC')  

    def get_stat(self, stat):
        needed = 0
        # ! probably going to need unpickle a list of strings into tags first
        for t in self.tags:
            needed += t.statistics[stat]
        return needed

    def worked_on(self, UoC):
        "Trigger func when this building plan is Built by an Actor"
        self.construction_remaining -= UoC
        if self.construction_remaining > 0:
            # if there is still construction to be done
            messages = [f'The construction progress of {self.name} has advanced.',
                        f'It now requires {self.construction_remaining} units of Construction to be completed.']
            return Payload(self.get_LID(), messages)
        elif self.construction_remaining <= 0:
            # if construction_remaining is 0 or less
            return self.complete()

    def complete(self):
        # TODO: get self object, delete self
        # TODO: create building in same location
        return f'{self.name} completed!'

    def get_LID(self):
        # cute LID dict
        pass


Tags = get_file('Tags.pickle')
Wood = Tag('Material', 'Wood', attributes=['Flammable', 'Organic'], statistics={'HP': 10, 'UoC': 1})
Stone = Tag('Material', 'Stone', attributes=[], statistics={'HP': 15, 'UoC': 3})
Metal = Tag('Material', 'Metal', attributes=['Electrical Conductivity', 'Thermal Conductivity'], statistics={'HP': 15, 'UoC': 5})
Base = Tag('Structure', 'Base', attributes=[], statistics={'FS': 1})
SPAWNERautomaton = Tag('Structure', 'SPAWNER|Automaton')
Tags = [Wood, Stone, Metal, Base, SPAWNERautomaton]
save_file(Tags, 'Tags.pickle')

x = BuildingPlan('Plan', 1, [Wood, Wood])
print(x.construction_remaining)
print(x.worked_on(1))
print(x.construction_remaining)