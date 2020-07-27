from regions import Region, Planet, Territory
from actors import Harvester
from files import get_file, save_file

# Region((0,0))
# Planet('Primus', (0,0))
# Harvester('Evan', celestial='Primus', territory='North')

Territories = get_file('Territories.pickle')
x = Territories['PRIMUSnorth']

print(x.resources)

x.resource_harvested('Stone', 'EVANharvester')

print(x.content['EVANharvester'].inventory)
print(x.resources)