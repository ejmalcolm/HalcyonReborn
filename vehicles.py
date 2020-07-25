from regions import Region, Celestial, Planet, Territory
from players import Player

from botInterface import Payload, region_string_to_int, payload_manage

from files import get_file, save_file

from math import sqrt


def distance_between(x1, x2, y1, y2):
    distance = sqrt(((x1 - x2)**2) + ((y1 - y2)**2))
    return distance


class Vehicle:

    def __init__(self, owner, xy, celestial=None, territory=None, busy=False):
        self.owner = owner  # the Player ID who owns this
        self.xy = xy  # the initial coordinates of this vehicle
        self.celestial = celestial  # what celestial the vehicle is on, if any
        self.territory = territory  # what territory the vehicle is in
        self.busy = busy  # If the vehicle is doing something
        self.id = self.owner.name.upper() + (type(self).__name__).lower()  # e.g. EVANhalcyon
        # get all the functions that can be "cast"-- abilities in game terms
        self.abilities = [f[2:] for f in dir(type(self)) if f.startswith('A_')]
        # store self into Regions.pickle
        Regions = get_file('Regions.pickle')
        Regions[self.xy].content[self.id] = self
        save_file(Regions, 'Regions.pickle')

    def change_region(self, new_region_xy):
        # remove self from old region
        Regions = get_file('Regions.pickle')
        try:
            del Regions[self.xy].content[self.id]
        except KeyError:
            # triggered if the entity is on a celestial
            # therefore:
            Territories = get_file('Territories.pickle')
            # get the Territory ID from the celestial + territory name
            TID = self.celestial.upper() + self.territory.lower()
            del Territories[TID].content[self.id]
            
        # add self to new region
        new_region = Regions[new_region_xy]
        new_region.content[self.id] = self
        save_file(Regions, 'Regions.pickle')
        # managing output (what the bot should send)
        messages = [f'{self} has arrived in {new_region_xy}']
        return Payload(self, messages)

    def inspect(self):
        """Returns details describing the current state of this entity"""
        messages = [f'A {type(self).__name__} belonging to {self.owner}.',
                    f'It is currently in the region {self.xy}']
        if self.celestial:
            messages.append(f'It is currently on the celestial {self.celestial}, in the territory {self.territory}.')
        messages.append(f'It has the following abilities: {self.abilities}')
        return Payload(self, messages)


class Spaceship(Vehicle):
    """Any vessel capable of spacefaring travel

    speed_space -- Speed in space, in millions km/hr
    """

    def __init__(self, owner, xy, speed_space=1, speed_landing=1):
        self.speed_space = speed_space
        self.speed_landing = speed_landing
        super().__init__(owner, xy)

    def __str__(self):
        return f'{self.owner}\'s Spaceship'

    def A_move_region(self, adjacent_region):
        """Move to an adjacent region of space

        adjacent_region -- (x,y) coordinates of an adjacent region"""
        # get the two region objects
        Regions = get_file('Regions.pickle')
        r1 = Regions[self.xy]
        # this is a user-facing ability, so adjacent_region_str is a string
        adjacent_region_tup = region_string_to_int(adjacent_region)
        r2 = Regions[adjacent_region_tup]
        # calculate the distance between the two regions
        distance = distance_between(r1.xy[0], r2.xy[0], r1.xy[1], r2.xy[1])
        # calculate the time it would take in hours
        duration = distance / self.speed_space
        messages = [f'{self} is now moving towards {r2}.',
                    f'It will arrive in {duration} hours']
        return Payload(self, messages, isTaskMaker=True,
                       taskDuration=duration,
                       onCompleteFunc=self.change_region,
                       onCompleteArgs=[adjacent_region_tup])

    def A_land_on(self, target_celestial, target_territory):
        """Land on any celestial body capable of hosting a ship

        target_celestial -- The celestial to land on, must be in same region
        target_territory -- The territory the ship should land in
        (Territories can be viewed by ~inspect_entity <landing_target>"""
        duration = self.speed_landing
        # Get the landing_target object
        Regions = get_file('Regions.pickle')
        landing_target = Regions[self.xy].content[target_celestial]
        messages = [f'{self} is now preparing to land on {landing_target}.',
                    f'It will arrive in {duration} hours.']
        return Payload(self, messages, isTaskMaker=True,
                       taskDuration=duration,
                       onCompleteFunc=landing_target.landed_on,
                       onCompleteArgs=[self.id, target_territory])

    def A_take_off(self):
        """Takes off from the current celestial into the surrounding region"""
        duration = self.speed_landing
        messages = [f'{self} is now preparing to take off from the {self.territory} territory of {self.celestial}',
                    f'It will arrive in the {self.xy} region in {duration} hours.']
        return Payload(self, messages, isTaskMaker=True,
                       taskDuration=duration,
                       onCompleteFunc=self.change_region,
                       onCompleteArgs=[self.xy])


class Halcyon(Spaceship):

    def __init__(self, owner, xy):
        super().__init__(owner, xy, speed_space=1)

    def __str__(self):
        return f"{self.owner}'s Halcyon"

    def A_calculate_slingshot(self, celest_1, celest_2):
        # * bot-facing function * #
        # calculates a fast path between two celestials
        # first, we have to check that both celestials exist
        Celestials = get_file('Celestials.pickle')
        try:
            c1 = Celestials[celest_1]
            c2 = Celestials[celest_2]
        except KeyError as e:
            return f"The indicated celestial {e} does not exist"
        # now we send out a Payload object to the bot
        return Payload(self, ['Hello'], isTaskMaker=True, taskDuration=1,
                       onCompleteFunc=self.create_slingshot,
                       onCompleteArgs=[c1, c2])

    def create_slingshot(self, c1, c2):
        # get the starting and ending region of space
        Regions = get_file('Regions.pickle')
        start_region = Regions[c1.xy]
        end_region = Regions[c2.xy]
        # create a Slingshot Path Terminus in each spot
        start_region.content['Slingshot Path Terminus'] = self.SPathTerminus(c1.xy, end_region)
        end_region.content['Slingshot Path Terminus'] = self.SPathTerminus(c2.xy, start_region)
        save_file(Regions, 'Regions.pickle')

    class SPathTerminus:  # inner class woah fancy

        def __init__(self, xy, linkRegion):
            self.xy = xy
            self.linkRegion = linkRegion

        def __str__(self):
            return f"A Slingshot Path, linked to {self.linkRegion}"

        def on_landing(self, landing_obj):
            # get the distance between each celestial (in millions of miles)
            distance = distance_between(self.xy[0], self.linkRegion.xy[0], self.xy[1], self.linkRegion.xy[1])
            # divide that distance by the slingshot travel rate
            travel_time = distance / 25
            return Payload(self, ['Hello'], isTaskMaker=True,
                           taskDuration=travel_time,
                           onCompleteFunc=landing_obj.change_region,
                           onCompleteArgs=self.linkRegion)


# Region((0, 0))
# Region((1, 0))
# Primus = Planet('Primus', (0, 0))
# Evan = Player(155782008826494976, 'Evan')
# James = Player(155783768307793920, 'James')
# Eriq = Player(155560259065348097, 'Eriq')
# Emily = Player(612827918984413256, 'Em-Head')
# y = Halcyon(Evan, (0, 0))
# x = Halcyon(James, (0, 0))
# z = Halcyon(Eriq, (0, 0))
# a = Halcyon(Emily, (0, 0))

# Celestials = get_file('Celestials.pickle')
# Primus = Celestials['Primus']
# Primus.landed_on('EVANhalcyon', 'North')

# Tasks = get_file('Tasks.pickle')
# for thing in list(Tasks.values()):
#     thing = thing[0]
#     a = [thing.trigger_func, thing.trigger_args, thing.source]
#     for b in a:
#         print(type(b))

# b = get_file('Regions.pickle')[(0,0)].content['BREQhalcyon']
# c = b.A_space_travel((25,0))
# print(c)
# Region( (25, 0 ) )
# x = Halcyon( 'Breq', (0, 0) )
# Primus = Celestial( 'Primus', (0, 0) )
# Secondus = Celestial( 'Secondus', (25, 0) )

# x.create_slingshot(Primus, Secondus)

# Regions = get_file('Regions.pickle')
# a = Regions[ (0, 0) ].content[ "BREQhalcyon" ].abilities
# print(a)
# Regions = get_file('Regions.pickle')
# print(Regions[(0,0)].content, Regions[ (25,0) ].content)
