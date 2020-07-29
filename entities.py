from files import get_file, save_file
from botInterface import Payload


class Entity:
    """All controllable units that can move between different areas."""

    def __init__(self, owner, xy=None, celestial=None, territory=None, busy=False):
        self.owner = owner  # the Player ID who owns this ('Evan')
        self.xy = xy  # LID of region (0,0) (tuple)
        self.celestial = celestial
        self.territory = territory  # LID of territory ('North')
        self.busy = busy  # If the vehicle is doing something
        self.id = self.owner.upper() + (type(self).__name__).lower()  # e.g. EVANhalcyon
        # get all the functions that can be "cast"-- abilities in game terms
        self.abilities = [f[2:] for f in dir(type(self)) if f.startswith('A_')]
        if self.xy:
            # store self into Regions.pickle
            Regions = get_file('Regions.pickle')
            Regions[self.xy].content[self.id] = self
            save_file(Regions, 'Regions.pickle')
        if self.territory:
            # store self into Territories.pickle
            Territories = get_file('Territories.pickle')
            TerrKey = self.celestial.upper() + self.territory.lower()
            Territories[TerrKey].content[self.id] = self
            save_file(Territories, 'Territories.pickle')

    def __str__(self):
        return f"{self.owner}'s {type(self).__name__}"

    def set_new_region(self, new_region_xy):
        """Trigger function used to move the entity into a new region

        First, deletes the entity from its old region or territory
        Then places the entity in the new region

        new_region_xy -- The tuple (x,y) of the new region
        """
        # get the region storage file
        Regions = get_file('Regions.pickle')
        if self.id in Regions[self.xy].content:
            # remove self from old region
            del Regions[self.xy].content[self.id]
        else:
            # triggered if the entity is on a celestial
            # therefore:
            Territories = get_file('Territories.pickle')
            # get the Territory ID from the celestial + territory name
            TID = self.celestial.upper() + self.territory.lower()
            # remove self from the territory and celestial
            self.territory = None
            self.celestial = None
            del Territories[TID].content[self.id]
            save_file(Territories, 'Territories.pickle')
        # add self to new region
        self.xy = new_region_xy
        new_region = Regions[new_region_xy]
        new_region.content[self.id] = self
        save_file(Regions, 'Regions.pickle')
        # managing output (what the bot should send)
        messages = [f'{self} has arrived in {new_region_xy}']
        return Payload(self.get_LID(), messages)

    # ! the first part of the set_news is probably repeatable

    def set_new_territory(self, new_territory_ID):
        """Trigger function used to place the entity in a new territory

        First, deletes from the old region or territory
        Then, places in the new territory

        new_territory_ID -- The territory ID string, e.g. EARTHnorth
        """
        if self.xy:
            # delete self, if in a region
            Regions = get_file('Regions.pickle')
            old_region = Regions[self.xy]
            del old_region.content[self.id]
            save_file(Regions, 'Regions.pickle')
        if self.territory:
            # delete self, if in a territory
            Territories = get_file('Territories.pickle')
            TID = self.celestial.upper() + self.territory.lower()
            old_territory = Territories[TID]
            del old_territory.content[self.id]
            save_file(Territories, 'Territories.pickle')
        # now we add to new territory
        Territories = get_file('Territories.pickle')
        new_territory = Territories[new_territory_ID]
        new_territory.content[self.id] = self
        # change self.territory
        self.territory = new_territory.label
        save_file(Territories, 'Territories.pickle')
        # bot output
        messages = [f'{self} has arrived in {new_territory}']
        return Payload(self.get_LID(), messages)

    def inspect(self):
        """Returns details describing the current state of this entity"""
        messages = [f'A {type(self).__name__} belonging to {self.owner}.']
        if self.xy:
            messages.append(f'It is currently in the region {self.xy}')
        if self.celestial:
            messages.append(f'It is currently on the celestial {self.celestial}, in the {self.territory} territory.')
        messages.append(f'It has the following abilities: {self.abilities}')
        return Payload(self.get_LID(), messages)

    def get_LID(self):
        """Returns the Location ID of this object

        Used for creating Payloads to send to botInterface"""
        LID = {'EID': self.id}
        if self.territory:
            LID['LocFile'] = 'Territories.pickle'
            LID['LocKey'] = self.celestial.upper() + self.territory.lower()
        elif self.xy:
            LID['LocFile'] = 'Regions.pickle'
            LID['LocKey'] = self.xy
        return LID
