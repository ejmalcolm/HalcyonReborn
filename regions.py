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
        messages = [f'This is the region of space denoted by the coordinates {self.xy}',
                    'This region contains the following entities:']
        for obj in self.content.values():
            try:
                messages.append(f'  {str(obj)} | {obj.owner}')
            except AttributeError:
                messages.append(f'  {str(obj)} | {type(obj).__name__}')
        return Payload(None, messages)

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
            try:
                if entity.owner == viewer.name:
                    return True
            except AttributeError as e:
                # generally, because there's an entity with no owner
                pass
        return False


class Celestial:
    # any sort of non-actively propelled object in space

    def __init__(self, name, xy, territories={}):
        self.name = name
        self.xy = xy
        self.territories = territories
        # add self to the region designated by xy
        Regions = get_file('Regions.pickle')
        Regions[xy].content[name] = self
        save_file(Regions, 'Regions.pickle')
        # add self to celestial storage
        Celestials = get_file('Celestials.pickle')
        Celestials[self.name] = self
        save_file(Celestials, 'Celestials.pickle')

    def __str__(self):
        return self.name

    def landed_on(self, entity_id, target_territory):
        '''Function that is called when this celestial is landed on

        entity_id -- The ID of the entity that is lending on this celestial
        target_territory -- The territory this entity will land'''
        # * Note that this "sucks in" the landing_entity * #
        # * Vs. the entity actually landing * #
        # * The celestial is doing all the work * #
        Regions = get_file('Regions.pickle')
        # get the region object
        Region = Regions[self.xy]
        # get the entity object from the region dict
        entity_obj = Region.content[entity_id]
        # get the territory object from Territories.pickle
        Territories = get_file('Territories.pickle')
        territory_obj = Territories[self.name.upper() + target_territory.lower()]
        # add the entity to the territory
        territory_obj.content[entity_id] = entity_obj
        # set the attributes of the vehicle
        entity_obj.celestial = self.name
        entity_obj.territory = target_territory
        save_file(Territories, 'Territories.pickle')
        # delete the entity from the region
        del Region.content[entity_id]
        save_file(Regions, 'Regions.pickle')
        # return the payload for the landing
        messages = [f'{entity_obj} has landed on the {target_territory} region of {self}.']
        return Payload(self, messages)


class Planet(Celestial):

    def __init__(self, name, xy):
        territories = self.gen_territories(name)
        super().__init__(name, xy, territories=territories)

    def __str__(self):
        return self.name

    def inspect(self):
        messages = [f'The planet {self.name}, located in {self.xy}.',
                    f'Contains the territories {list(self.territories.keys())}.']
        return Payload(self, messages)

    def gen_territories(self, parent_name):
        TERRITORY_LABELS = ['North', 'Northeast', 'East', 'Southeast',
                            'South', 'Southwest', 'West', 'Northwest']
        # this is the part that randomly assigns the biomes to territories
        territories = {}
        for lab in TERRITORY_LABELS:
            # create an Territory object (with random biomes) and append it
            territories[lab] = Territory(parent_name, lab)
        return territories


class Territory:

    # TODO | UNIQUES: do later
    # TODO | special case for NONE: polar, desert, wastes

    def __init__(self, parent, label, content={}, has_biomes=True):
        self.parent = parent  # the string ID the territory is attached to
        self.label = label  # the reference label of the territory
        self.id = str(parent).upper() + label.lower()
        self.content = {}  # what's in this territory
        self.description = ''
        self.has_biomes = has_biomes
        # now, we randomly select what resources this territory will have
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
        # save file management
        Territories = get_file('Territories.pickle')
        Territories[self.id] = self
        save_file(Territories, 'Territories.pickle')

    def __str__(self):
        return f'{self.label} region of {self.parent}'

    def check_vision(self, viewer_uid):
        """Checks if the given UID owns at least 1 entity in the region
        """
        Players = get_file('Players.pickle')
        try:
            viewer = Players[viewer_uid]
        except KeyError as e:
            # generally if that player object hasn't been created
            print(f'check_vision KeyError {e}')
            return False
        for entity in self.content.values():
            try:
                if entity.owner == viewer.name:
                    return True
            except AttributeError as e:
                # generally, because there's an entity with no owner
                print(e)
        return False

    def scan(self):
        messages = [f'The {self.label} territory of the celestial {self.parent}.',
                    f'It is a {self.description} biome.',
                    f'It currently hosts the following resources: {self.resources}']
        if self.content:
            messages.append(f'It currently contains the following entities:')
        for obj in self.content.values():
            try:
                messages.append(f'  {str(obj)} | {obj.owner}')
            except AttributeError:
                messages.append(f'  {str(obj)} | {type(obj).__name__}')
        return Payload(self, messages)

    def resource_harvested(self, resource_name, harvester_ID):
        # need to do this so we can save
        Territories = get_file('Territories.pickle')
        self_territory = Territories[self.id] 
        harvester = self_territory.content[harvester_ID]
        try:
            # decrease resource by 1
            self_territory.resources[resource_name] -= 1
        except KeyError as e:
            # double-check that the resource is actually here
            print(f'{e} not found in {self} when harvest was attempted by {self.content[harvester_ID]}.')
            messages = [f'{resource_name} in {self} was depleted before {self.content[harvester_ID]} could complete harvest.']
            return Payload(None, messages)
        # add the resource to the harvester's inventory
        if resource_name in self.content[harvester_ID].inventory:
            # increment if already exists
            self_territory.content[harvester_ID].inventory[resource_name] += 1
        else:
            # set if it doesn't exist
            self_territory.content[harvester_ID].inventory[resource_name] = 1
        # save inventory and resource changes
        save_file(Territories, 'Territories.pickle')
        messages = [f'{harvester} has harvested 1 {resource_name}.']
        return Payload(None, messages)
