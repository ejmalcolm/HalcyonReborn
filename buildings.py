from botInterface import Payload
from entities import Entity
from players import Player
from files import get_file, save_file
from regions import Region, Territory


class Tag():
    """Tags that can be added to building plans to give them different effects"""

    def __init__(self, category, name, attributes=[], statistics={}):
        self.category = category
        self.name = name
        self.attributes = attributes
        self.statistics = statistics
        # add self to Tags
        Tags = get_file('Tags.pickle')
        Tags[self.name] = self
        print(Tags)
        save_file(Tags, 'Tags.pickle')

    def __str__(self):
        return f'{self.name}: A {self.category} tag that conveys {self.attributes} and {self.statistics}'


class BuildingPlan(Entity):

    def __init__(self, owner, name, tags=[],
                 xy=None, celestial=None, territory=None):
        self.owner = owner
        self.name = name
        self.tags = tags
        self.construction_remaining = self.get_stat('UoC')
        super().__init__(owner, xy, celestial, territory)

    def __str__(self):
        return f'{self.eid}'

    def get_stat(self, stat):
        needed = 0
        Tags = get_file('Tags.pickle')
        for t in self.tags:
            try:
                needed += Tags[t].statistics[stat]
            except KeyError:
                # doesn't have the statistic
                pass
        return needed

    def worked_on(self, UoC):
        "Trigger func when this building plan is Built by an Actor"
        # need to save self
        LID = self.get_LID()
        Storage = get_file(LID['LocFile'])
        self.construction_remaining -= UoC
        Storage[LID['LocKey']].content[self.eid] = self
        save_file(Storage, LID['LocFile'])
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


class Building(Entity):
    pass


# Wood = Tag('Material', 'Wood', attributes=['Flammable', 'Organic'], statistics={'HP': 10, 'UoC': 1})
# Stone = Tag('Material', 'Stone', attributes=[], statistics={'HP': 15, 'UoC': 3})
# Metal = Tag('Material', 'Metal', attributes=['Electrical Conductivity', 'Thermal Conductivity'], statistics={'HP': 15, 'UoC': 5})
# Base = Tag('Structure', 'Base', attributes=[], statistics={'FS': 1})
# SPAWNERautomaton = Tag('Structure', 'SPAWNER|Automaton')
