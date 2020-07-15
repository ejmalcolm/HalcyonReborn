from random import choice, random
from files import save_file, get_file
class Region:
    # each region is a cube of space along the galactic plane
    # 1milx1milx1mil KM
    # there are 500 regions in each cardinal direction from the sun
    def __init__(self, xy):
        self.xy = xy
        self.content = {}
        # add self to the "region book"
        # TODO: add file management here
        Regions = get_file('Regions.pickle')
        Regions[self.xy] = self
        save_file(Regions, 'Regions.pickle')
    
    def __str__(self):
        return str(self.xy)

Celestials = {}
class Celestial:
    # any sort of non-actively propelled object in space

    def __init__(self, name, xy):
        self.name = name
        self.xy = xy
        # add self to the region designated by xy
        # TODO: add file management here
        Regions[xy].content[name] = self
        # add self to celestial storage
        # TODO: add file management here
        Celestials[self.name] = self

    def __str__(self):
        return self.name

Planets = {}
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
            octants[lab] = Octant(self, lab) # create an Octant object (with random biomes) and append it
        return octants

class Octant:

        # TODO | UNIQUES: do later
        # TODO | special case for NONE: polar, desert, wastes

    def __init__(self, parent, label, hasBiomes = True):
        self.parent = parent # the object the octant is attached to
        self.label = label # the reference label of the octant
        self.description = ''
        self.hasBiomes = hasBiomes
        # now, we randomly select what resources this octant will have
        self.resources = {}
        RESOURCE_BIOMES = { 'Wood' : ('Forest', 'Jungle', 'Taiga'),
                            'Stone' : ('Hill', 'Steppe', 'Mountain'),
                            'Metal' : ('Cave', 'Crevice', 'Canyon')
                            }
        if self.hasBiomes:
            i = 0
            descs = set([]) # use a set to make sure there's no repeats
            while i <= 0.75:
                res = choice(list(RESOURCE_BIOMES)) # pick a random resource from the list to add
                descs.add(choice(RESOURCE_BIOMES[res])) # pick a random biome associated with that choice
                try: 
                    self.resources[res] += 5 # try to add 5 of the resource
                except KeyError:
                    self.resources[res] = 5 # if it fails, there's none of that resource
                                            # therefore we should set it to 5 instead 
                i += random()
            for d in sorted(list(descs), reverse=True):
                self.description += d
                self.description += ' '
            self.description = self.description[:-1] # remove the extraneous extra space and y
            self.description += 's'

# Region( (0,0) )
# Region( (1,0) )
# Celestial('Sol', (0,0) )
# Primus = Planet('Primus', (1, 0))
