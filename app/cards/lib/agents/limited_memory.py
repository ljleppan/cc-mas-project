class LimitedMemory():
    '''Simple LeastRecentlyAdded limited list, modified from the example used in the course.
    '''
    def __init__(self, capacity):
        """
        Creates a new :class:`.LimitedMemory`.

        :param capacity: Number of items this :class:`.LimitedMemory` can hold.
        """
        self._capacity = capacity
        self._items = []

    @property
    def capacity(self):
        """:return: The maximum capacity of this :class:`.LimitedMemory`"""
        return self._capacity

    @property
    def items(self):
        """:return: The items stores in this :class:`.LimitedMemory`"""
        return self._items

    def append(self, item):
        """
        Adds a new item to this :class:`.LimitedMemory`. If this :class:`.LimitedMemory`
        already contains `capacity` items, the oldest item is removed.

        :param card: The item to add this this :class:`.LimitedMemory`.
        """
        self._items.insert(0, item)
        if len(self._items) > self.capacity:
            self._items = self._items[:self.capacity]
