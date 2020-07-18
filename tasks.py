from files import get_file, save_file

from time import time


class Task:
    """The class that manages time-delayed actions

    trigger_hour -- What hour (since epoch) the task will trigger on
    trigger_func -- The function to be called when the task triggers
    trigger_args -- any args the function needs"""

    def __init__(self, trigger_hour, trigger_func, trigger_args):
        self.trigger_hour = int(trigger_hour)
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
        """ Calls the task's associated trigger_func """
        return self.trigger_func(*self.trigger_args)


def check_tasks():
    '''Runs through all tasks and runs then removes the appropriate ones'''
    Tasks = get_file('Tasks.pickle')
    current_HSE = time() / 3600
    # check every hour that currently has tasks on it
    for key in Tasks:
        # if that hour is before/equal to the current hour
        if key <= current_HSE:
            # get the task list
            for t in Tasks[key]:
                t.complete()

# Tasks = {}
# save_file(Tasks, 'Tasks.pickle')

# def test():
#     print('test!!!')

# current_HSE = time() // 3600
# a = Task(current_HSE, test, [])
# b = Task(current_HSE-5, print, ['before'])
# c = Task(current_HSE+5, print, ['after'])

# check_tasks()
