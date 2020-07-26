from time import time

from files import get_file, save_file


class Task:
    """The class that manages time-delayed actions

    trigger_hour -- What hour (since epoch) the task will trigger on
    trigger_func -- The function to be called when the task triggers
    trigger_args -- any args the function needs"""

    def __init__(self, sourceLID, trigger_hour, trigger_func, trigger_args):
        self.sourceLID = sourceLID
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
        # set the task user to not busy anymore
        sourceLID = self.sourceLID
        sourceFile = sourceLID['LocFile']
        sourceKey = sourceLID['LocKey']
        sourceEID = sourceLID['EID']
        storageDict = get_file(sourceFile)
        source = storageDict[sourceKey].content[sourceEID]
        source.busy = False
        save_file(storageDict, sourceFile)
        # trigger the func
        return self.trigger_func(*self.trigger_args)


def check_tasks():
    """Runs through all tasks and runs then removes the appropriate ones"""
    Tasks = get_file('Tasks.pickle')
    current_MSE = int(time() / 60)
    print(f'CURRENT TIME: {current_MSE}')
    print(f'TASKS BEFORE: {Tasks}')
    payloads = []
    # check every minute that currently has tasks on it
    for key in Tasks:
        # if that minute is before/equal to the current minute
        if key <= current_MSE:
            # complete all tasks under that minute
            for t in Tasks[key]:
                task_return = t.complete()
                payloads.append(task_return)
    # then, we create a new tasks dictionary with only the minute yet to come
    Tasks = {key: value for (key, value) in Tasks.items() if key > current_MSE}
    save_file(Tasks, 'Tasks.pickle')
    # send the output to the botCommands background loop
    return payloads


def manual_complete_all_tasks():
    """Automatically completes all tasks in queue, regardless of time"""
    Tasks = get_file('Tasks.pickle')
    payloads = []
    for sublist in Tasks.values():
        for item in sublist:
            task_return = item.complete()
            payloads.append(task_return)
    Tasks = {}
    save_file(Tasks, 'Tasks.pickle')
    return payloads
