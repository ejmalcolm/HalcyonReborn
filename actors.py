from entities import Entity
from players import Player
from botInterface import Payload, region_string_to_int

# TODO: actor, organisms, automatons, laborers


class Actor(Entity):
    """Any singular, self-propelled entity that can move between territories

    speed_land -- The amount of hours it takes to move from one territory to another"""

    def __init__(self, owner, xy=None,
                 celestial=None, territory=None, busy=False,
                 speed_land=1):
        self.speed_land = speed_land
        super().__init__(owner, xy, celestial=celestial, territory=territory, busy=busy)

    def A_move_territory(self, new_territory):
        """Move to another territory on the same celestial

        EXAMPLE move_territory South

        new_territory -- The territory on the same celestial to move to
        Territories can be found by ~scanning the celestial
        """
        # check to make sure in territory, not region
        if self.xy:
            message = [f'{self} is currently in the space region {self.xy}, not a territory.']
            return Payload(self.get_LID(), message)
        # this is a user-facing ability, so convert to TID
        new_TID = self.celestial.upper() + new_territory.lower()
        # calculate the time it would take in hours
        duration = self.speed_land
        messages = [f'{self} is now moving towards the {new_territory} territory of {self.celestial}.',
                    f'They will arrive in {duration} hours']
        return Payload(self.get_LID(), messages, isTaskMaker=True,
                       taskDuration=duration,
                       onCompleteFunc=self.set_new_territory,
                       onCompleteArgs=[new_TID])


class Gatherer(Actor):
    """An Actor that can harvest resources"""
    pass
