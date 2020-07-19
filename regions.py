from random import choice, random
from files import save_file, get_file
from botInterface import Payload
from players import Player


class Region:
    # each region is a cube of space along the galactic plane
    # 1milx1milx1mil KM
    # there are 500 regions in each cardinal direction from the sun
    def __init__(self, xy):
        self.xy = xy
        self.content = {}
        # add self to the Regions dict
        Regions = get_file('Regions.pickle')
        Regions[self.xy] = self
        save_file(Regions, 'Regions.pickle')

    def __str__(self):
        return str(self.xy)

    def scan(self):
        prefix = ['This region contains the following entities:']
        content_list = [str(obj) for obj in self.content.values()]
        messages = prefix + content_list
        return Payload(self, messages)

    def check_vision(self, viewer_uid):
        '''Checks each entity in region, returns if <viewer_uid> owns any'''
        Players = get_file('Players.pickle')
        try:
            viewer = Players[viewer_uid]
        except KeyError as e:
            # generally if that player object hasn't been created
            print(f'check_vision KeyError {e}')
            return False
        for entity in self.content.values():
            if entity.owner.uid == viewer.uid:
                return True
        return False


class Celestial:
    # any sort of non-actively propelled object in space

    def __init__(self, name, xy):
        self.name = name
        self.xy = xy
        # add self to the region designated by xy
        Regions = get_file('Regions.pickle')
        Regions[xy].content[name] = self
        save_file(Regions, 'Regions.pickle')
        # add self to celestial storage
        # TODO: add file management here
        Celestials = get_file('Celestials.pickle')
        Celestials[self.name] = self
        save_file(Celestials, 'Celestials.pickle')

    def __str__(self):
        return self.name


class Planet(Celestial):

    def __init__(self, name, xy):
        super().__init__(name, xy)
        self.octants = self.gen_octants()

    def gen_octants(self):
        OCTANT_LABELS = ('North', 'Northeast', 'East', 'Southeast',
                         'South', 'Southwest', 'West', 'Northwest')
        # this is the part that randomly assigns the biomes to octants
        octants = {}
        for lab in OCTANT_LABELS:
            # create an Octant object (with random biomes) and append it
            octants[lab] = Octant(self, lab)
        return octants


class Octant:

    # TODO | UNIQUES: do later
    # TODO | special case for NONE: polar, desert, wastes

    def __init__(self, parent, label, has_biomes=True):
        self.parent = parent  # the object the octant is attached to
        self.label = label  # the reference label of the octant
        self.description = ''
        self.has_biomes = has_biomes
        # now, we randomly select what resources this octant will have
        self.resources = {}
        RESOURCE_BIOMES = {'Wood': ('Forest', 'Jungle', 'Taiga'),
                           'Stone': ('Hill', 'Steppe', 'Mountain'),
                           'Metal': ('Cave', 'Crevice', 'Canyon')
                           }
        if self.has_biomes:
            i = 0
            descs = set([])  # use a set to make sure there's no repeats
            while i <= 0.75:
                # pick a random resource from the list to add
                res = choice(list(RESOURCE_BIOMES))
                # pick a random biome associated with that choice
                descs.add(choice(RESOURCE_BIOMES[res]))
                try:
                    # try to add 5 of the resource
                    self.resources[res] += 5
                except KeyError:
                    # if it fails, there's none of that resource
                    # therefore we should set it to 5 instead
                    self.resources[res] = 5
                i += random()
            for d in sorted(list(descs), reverse=True):
                self.description += d
                self.description += ' '
            # remove the extraneous extra space and 'y'
            self.description = self.description[:-1]
            self.description += 's'


# Region( (0,0) )
# Region( (1,0) )
# print(get_file('Regions.pickle'))
# Celestial('Sol', (0,0) )
# Primus = Planet('Primus', (1, 0))
