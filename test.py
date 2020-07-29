from regions import Region, Planet, Territory
from actors import Harvester
from files import get_file, save_file

# Region((0,0))
# Planet('Primus', (0,0))
# Harvester('Evan', celestial='Primus', territory='North')

class A():

    def __init__(self):
        print(1)

    def change(self):
        print(5)


x = A()
print(x.c)