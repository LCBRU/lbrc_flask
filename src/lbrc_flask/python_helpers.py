from copy import deepcopy
import inspect


def get_concrete_classes(cls):
    result = [sub() for sub in cls.__subclasses__()
        if len(sub.__subclasses__()) == 0 and
        # If the constructor requires parameters
        # other than self (i.e., it has more than 1
        # argument), it's an abstract class
        len(inspect.getfullargspec(sub.__init__)[0]) == 1]

    for sub in [sub for sub in cls.__subclasses__()
                if len(sub.__subclasses__()) != 0]:
        result += get_concrete_classes(sub)

    return result


def dictlist_remove_key(dictlist: list[dict], key):
    def remove_key(dicts):
        result = deepcopy(dicts)
        result.pop(key)
    return list(map(remove_key, dictlist))


class sort_descending:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj    

