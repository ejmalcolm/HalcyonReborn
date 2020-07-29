# from regions import Region, Planet, Territory
# from actors import Harvester
# from files import get_file, save_file

# Region((0,0))
# Planet('Primus', (0,0))
# Harvester('Evan', celestial='Primus', territory='North')

class A():

    def __init__(self):
        print('A init')

    def change(self):
        print(5)


class B():

    def __init__(self):
        print('B init')

    def change(self):
        print(10)


class C(B, A):

    def __init__(self):
        A.__init__(self)
        B.__init__(self)


x = C()

x.change()
