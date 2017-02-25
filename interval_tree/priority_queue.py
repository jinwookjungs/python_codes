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
