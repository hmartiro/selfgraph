"""

"""

import yaml
from collections import OrderedDict
from functools import total_ordering


class UnsortableList(list):

    def sort(self, *args, **kwargs):
        print('sort called')
        pass


class UnsortableOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))


yaml.add_representer(
    UnsortableOrderedDict,
    yaml.representer.SafeRepresenter.represent_dict
)


def serialize(data):

    return yaml.dump(data, width=10000)


if __name__ == '__main__':

    out = list()
    out.append(UnsortableOrderedDict((('B', 3), ('A', 5))))

    d = [
        ['type', 'email'],
        ['date', 1],
        ['from', 2],
        ['to', 3],
        ['cc', 4],
        ['bcc', 5],
        ['text', 6]
    ]

    out.append(d)

    print(serialize(out))
