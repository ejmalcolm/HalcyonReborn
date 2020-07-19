from regions import Region, Celestial

from botInterface import Payload

from files import get_file, save_file

from math import sqrt

# TODO: come up with some sort of unique ID system
# TODO: maybe change all these xy attributes to just giving the Region


def distance_between(x1, x2, y1, y2):
    distance = sqrt(((x1 - x2)**2) + ((y1 - y2)**2))
    return distance

# ! duplicate from botCommands, move both to botInterface? ! #
def region_string_to_int(region_string):
    """Converts a string '(x, y)' to a tuple (x, y)"""
    splitforms = region_string.split(',')
    nospaces = [x.replace(' ', '') for x in splitforms]
    noparens = [x.replace('(', '') for x in nospaces]
    noparens2 = [x.replace(')', '') for x in noparens]
    asints = [int(x) for x in noparens2]
    return (asints[0], asints[1])


class Vehicle:

    def __init__(self, owner_uid, xy):
        self.owner_uid = owner_uid  # the UID of the Player who owns this
        self.xy = xy  # the initial coordinates of this vehicle
        self.id = self.owner.upper() + (type(self).__name__).lower()  # e.g. EVANhalcyon
        # get all the functions that can be "cast"-- abilities in game terms
        self.abilities = [f[2:] for f in dir(type(self)) if f.startswith('A_')]
        # store self into Regions.pickle
        Regions = get_file('Regions.pickle')
        Regions[self.xy].content[self.id] = self
        save_file(Regions, 'Regions.pickle')

    def change_region(self, new_region_xy):
        # remove self from old region
        Regions = get_file('Regions.pickle')
        del Regions[self.xy].content[self.id]
        # add self to new region
        new_region = Regions[new_region_xy]
        new_region.content[self.id] = self
        save_file(Regions, 'Regions.pickle')
        # managing output (what the bot should send)
        messages = [f'{self} has arrived in {new_region_xy}']
        return Payload(self, messages)

    def A_inspect(self):
        '''Returns details describing the current state of this entity'''
        messages = [f'A {type(self).__name__} belonging to {self.owner}.',
                    f'It is currently in the region {self.xy}',
                    f'It has the following abilities: {self.abilities}']
        return Payload(self, messages)


class Spaceship(Vehicle):
    '''Any vessel capable of spacefaring travel

    speed_space -- Speed in space, in millions km/hr
    '''

    def __init__(self, owner, xy, speed_space=1):
        self.speed_space = speed_space
        super().__init__(owner, xy)

    def A_space_travel(self, adjacent_region_str):
        '''Move to an adjacent region of space

        adjacent_region_xy -- (x,y) coordinates of an adjacent region'''
        # get the two region objects
        Regions = get_file('Regions.pickle')
        r1 = Regions[self.xy]
        # this is a user-facing ability, so adjacent_region_str is a string
        adjacent_region_tup = region_string_to_int(adjacent_region_str)
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

        def landing_func(self, landing_obj):
            # get the distance between each celestial (in millions of miles)
            distance = distance_between(self.xy[0], self.linkRegion.xy[0], self.xy[1], self.linkRegion.xy[1])
            # divide that distance by the slingshot travel rate
            travel_time = distance / 25
            return Payload(self, ['Hello'], isTaskMaker=True,
                           taskDuration=travel_time,
                           onCompleteFunc=landing_obj.change_region,
                           onCompleteArgs=self.linkRegion)


# Region ( (0,0) )
# Region( (1, 0) )
# x = Halcyon( 'Storm', (0, 0) )
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
