from files import save_file, get_file


class Player:

    def __init__(self, uid, name):
        # set attributes
        self.uid = uid
        self.name = name
        # store self into Players dict
        Players = get_file('Players.pickle')
        Players[uid] = self
        save_file(Players, 'Players.pickle')

    def __str__(self):
        return self.name

# save_file({}, 'Players.pickle')
# Player(77, 'Breq')
# Players = get_file('Players.pickle')
