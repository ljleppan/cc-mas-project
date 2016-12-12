class LimitedMemory():
    '''Simple LeastRecentlyAdded limited list, modified from the example used in the course.
    '''
    def __init__(self, capacity):
        self._capacity = capacity
        self._items = []

    @property
    def capacity(self):
        return self._capacity

    @property
    def items(self):
        return self._items

    def append(self, item):
        self._items.insert(0, item)
        if len(self._items) > self.capacity:
            self._items = self._items[:self.capacity]
