'''
    File name      : priority_queue.py
    Author         : Jinwook Jung
    Created on     : Sat Feb 25 01:06:35 2017
    Last modified  : 2017-02-25 01:07:29
    Python version : 
'''

import heapq

class PriorityQueue: 
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item)) 
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def remove_item_by_name(self, name):
        print(set(self._queue))
        print(set(self._queue).remove(Item(name)))


if __name__ == '__main__':
    class Item:
        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return 'Item({!r})'.format(self.name)

        def __eq__(self, other):
            return self.name == other.name

        def __hash__(self):
            return hash(self.name)

    q = PriorityQueue()
    q.push(Item('foo'), 1) 
    q.push(Item('bar'), 5) 
    q.push(Item('spam'), 4) 
    q.push(Item('grok'), 1) 

    q.remove_item_by_name('foo')

    print(q.pop())
    print(q.pop())
    print(q.pop())

