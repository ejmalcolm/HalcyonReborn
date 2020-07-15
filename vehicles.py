from regions import Region, Regions, Celestial, Celestials
from bot import Payload

from math import sqrt

# TODO: come up with some sort of unique ID system
# TODO: maybe change all these xy attributes to just giving the Region

class Vehicle:

    def __init__(self, owner, xy):
        self.owner = owner # the Player object that owns this
        self.xy = xy # the initial coordinates of this halcyon
        # TODO: add file management here
        Regions[self.xy].content[str(self)] = self

    def change_region(self, new_region):
        # remove self from old region
        del Regions[self.xy].content[str(self)]
        # add self to new region
        new_region.content[str(self)] = self

class Halcyon(Vehicle):

    def __init__(self, owner, xy):
        super().__init__(owner, xy)

    def __str__(self):
        return "%s's Halcyon" % self.owner

    def calc_slingshot(self, celest_1, celest_2):
        ### * bot-facing function * ###
        # calculates a fast path between two celestials
        # first, we have to check that both celestials exist
        # TODO: need file management for loading Celestials
        try:
            c1 = Celestials[celest_1]
            c2 = Celestials[celest_2]
        except KeyError as e:
            return "The indicated celestial %s does not exist" % e
        # now we send out a Payload object to the bot
        return Payload(self, ['Hello',], isTaskMaker=True, taskDuration=1,
                        onCompleteFunc=self.create_slingshot, onCompleteArgs = [c1, c2])

    def create_slingshot(self, c1, c2):
        # get the starting and ending region of space
        start_region = Regions[c1.xy]
        end_region = Regions[c2.xy]
        # create a Slingshot Path Terminus in each spot
        start_region.content['Slingshot Path Terminus'] = self.SPathTerminus(c1.xy, end_region)
        end_region.content['Slingshot Path Terminus'] = self.SPathTerminus(c2.xy, start_region)

    class SPathTerminus: # inner class woah fancy

        def __init__(self, xy, linkRegion):
            self.xy = xy
            self.linkRegion = linkRegion

        def __str__(self):
            return "A Slingshot Path, linked to %s" % self.linkRegion

        def move_with(self, taker):
            # now, we get the distance between each celestial (in millions of miles)
            distance = sqrt( ((self.xy[0]-self.linkRegion.xy[0])**2)+((self.xy[1]-self.linkRegion.xy[1])**2) ) 
            # divide that distance by the slingshot travel rate
            travel_time = distance / 25
            return Payload(self, ['Hello'], isTaskMaker= True, taskDuration=travel_time,
                            onCompleteFunc = taker.change_region, onCompleteArgs = self.linkRegion)


a = Region( (0, 0) )
b = Region( (25, 0 ) )
x = Halcyon( 'Breq', (0, 0) )
Primus = Celestial( 'Primus', (0, 0) )
Secondus = Celestial( 'Secondus', (25, 0) )

x.create_slingshot(Primus, Secondus)

print(a.content, b.content)
print( Regions[ (0, 0) ].content[ "Breq's Halcyon" ].change_region(b) )
print(a.content, b.content)