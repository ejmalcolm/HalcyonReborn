from files import get_file, save_file

from time import time


class Task:

    def __init__(self, trigger_hour, trigger_func, trigger_args):
        self.trigger_hour = trigger_hour
        self.trigger_func = trigger_func
        self.trigger_args = trigger_args
        # add self to the task storage dictionary under the trigger hour
        Tasks = get_file('Tasks.pickle')
        try:
            # if there are other tasks for that hour, add self to the list
            Tasks[self.trigger_hour].append(self)
        except KeyError:
            # if not, make a new list with self
            Tasks[self.trigger_hour] = [self]
        save_file(Tasks, 'Tasks.pickle')
    
    def complete(self):
        pass
