from regions import Region

class Rabbit:

    def __init__(self):
        pass

    def one(self):
        print('1')


a = Region((15, 15))
print(getattr(a, 'scan'))