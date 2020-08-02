from entities import Entity
from players import Player
from botInterface import Payload, region_string_to_int
from files import get_file, save_file

# TODO: actor, organisms, automatons, laborers


class Actor(Entity):
    """Any singular, self-propelled entity that can move between territories

    speed_land -- The amount of hours it takes to move from one territory to another
    inventory -- Any items the entity is carrying. Key=item, value = amount."""

    def __init__(self, owner, xy=None,
                 celestial=None, territory=None, busy=False,
                 speed_land=1, inventory={}):
        self.speed_land = speed_land
        self.inventory = inventory
        super().__init__(owner, xy, celestial=celestial, territory=territory, busy=busy)

    def inspect(self):
        """Returns details describing the current state of this entity

        Includes inventory, unlike Entity.inspect()"""
        messages = [f'A {type(self).__name__} belonging to {self.owner}.']
        if self.xy:
            messages.append(f'It is currently in the region {self.xy}')
        if self.celestial:
            messages.append(f'It is currently on the celestial {self.celestial}, in the {self.territory} territory.')
        if self.inventory:
            messages.append(f'It currently is carrying {self.inventory}')
        messages.append(f'It has the following abilities: {self.abilities}')
        return Payload(self.get_LID(), messages)

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


class Harvester(Actor):
    """An Actor that can harvest resources

    harvest_time -- Time, in hours, to harvest 1 unit of a resource
    """

    def __init__(self, owner, xy=None,
                 celestial=None, territory=None, busy=False,
                 speed_land=1, harvest_time=1):
        self.harvest_time = harvest_time
        super().__init__(owner, xy, celestial=celestial, territory=territory, busy=busy)

    def A_harvest_resource(self, resource_name):
        """Harvest a resource in the same territory as this Harvester

        resource_name -- The name of the resource to harvest
        You can see the resources in a territory with ~scan.
        """
        # get the territory of self
        TID = self.celestial.upper() + self.territory.lower()
        Territories = get_file('Territories.pickle')
        terr_obj = Territories[TID]
        try:
            if terr_obj.resources[resource_name] != 0:
                # harvest the resource
                duration = self.harvest_time
                messages = [f'{self} is now harvesting 1 {resource_name} from {self.territory} {self.celestial}.',
                            f'It will be completed in {duration} hours.']
                return Payload(self.get_LID(), messages, isTaskMaker=True,
                               taskDuration=duration,
                               onCompleteFunc=terr_obj.resource_harvested,
                               onCompleteArgs=[resource_name, self.eid])
            elif terr_obj.resource[resource_name] == 0:
                messages = [f'The {resource_name} in {self.territory} is depleted.',
                            f'Wait for Evan to implement the regeneration mechanic.']
                return Payload(self.get_LID(), messages)
        except KeyError:
            # if the resource doesn't exist at all in the territory
            messages = [f'There is no {resource_name} in {self.territory}']
            return Payload(self.get_LID(), messages)


class Builder(Actor):
    """An Actor that can help construct Building Plans

    build_time -- Time, in hours, to contribute 1 unit of Construction to a building plan
    """

    def __init__(self, owner, xy=None,
                 celestial=None, territory=None, busy=False,
                 speed_land=1, build_time=1):
        self.build_time = build_time
        super().__init__(owner, xy, celestial=celestial, territory=territory, busy=busy)

    def A_construct_building(self, plan_name):
        """Help construct a building plan in the same territory as this Builder

        plan_name -- The name of the building plan to construct
        You can see plans in the territory with ~scan
        """
        # get the territory of self
        TID = self.celestial.upper() + self.territory.lower()
        Territories = get_file('Territories.pickle')
        terr_obj = Territories[TID]
        try:
            # get the building plan obj
            bpan = terr_obj.content[plan_name]
            messages = [f'{bpan} is now being worked on by {self}.',
                        f"The {bpan}'s progress will be advanced in {self.build_time} hours."]
            return Payload(self.get_LID(), messages,
                           isTaskMaker=True, taskDuration=self.build_time,
                           onCompleteFunc=bpan.worked_on,
                           onCompleteArgs=[1])
        except KeyError:
            # if the name doesn't exist in the territory
            messages = [f'There is no plan named "{plan_name}" in {self.territory}.']
            return Payload(self.get_LID(), messages)


class Automaton(Builder, Harvester):

    def __init__(self, owner, xy=None,
                 celestial=None, territory=None):
        Harvester.__init__(self, owner, harvest_time=(1/6))
        Builder.__init__(self, owner, build_time=(1/3))
        Actor.__init__(self, owner, xy=xy, celestial=celestial, territory=territory)


class Engineer(Actor):

    def __init__(self, owner, xy=None,
                 celestial=None, territory=None):
        super().__init__(self, owner, xy=xy, celestial=celestial, territory=territory)
    
    # def A_create_plan(self):

