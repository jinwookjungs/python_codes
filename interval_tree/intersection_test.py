'''
    File name      : intersection_test.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 20:27:42 2017
    Last modified  : 2017-02-25 18:34:15
    Python version : 
'''

from intervaltree import Interval, IntervalTree
from copy import deepcopy

class Rectangle(object):
    def __init__(self, name, llx, lly, urx, ury):
        self.name = name
        self.llx, self.lly = llx, lly
        self.urx, self.ury = urx, ury

    def __str__(self):
        return "%s: (%d,%d), (%d,%d)" % (self.name, self.llx, self.lly, self.urx, self.ury)


class Bound(object):
    def __init__(self, sink, coord, is_left=True):
        self.sink = sink
        self.coord = coord
        self.is_left = is_left      # True if it represents a left boundary

        self.name = sink.name

    def __str__(self):
        return "%s " % (self.__class__.__name__) \
               + "(%s, %d " % (self.name, self.coord) \
               + "%s)" % ("Left" if self.is_left else "Right")


class Level(object):
    def __init__(self):
        self.nodes = list()


class Node(object):
    def __init__(self):
        self.assoc_sinks = list()
        self.llx, self.urx = None, None
        self.lly, self.ury = None, None

    
    def __str__(self):
        name = '/'.join([s.name for s in self.assoc_sinks])
        return "%s llx=%r urx=%r lly=%r ury=%r" % (name, self.llx, self.urx, self.lly, self.ury)


class Checker(object):
    def __init__(self):
        self.source = None
        self.sinks = list()

        self.T_x = IntervalTree()
        self.T_y = IntervalTree()

        self.level = Level()

        self.x_bounds, self.y_bounds = list(), list()


    def read_input(self, file_name):
        # Read file        
        with open(file_name) as f:
            lines = [l.strip() for l in f if l.strip()]

        # Set sinks
        for line in lines[1:]:
            if line == 'Source':
                break

            tokens = line.split()
            name = tokens[0]
            llx, lly, urx, ury = [int(t) for t in tokens[1:]]
            self.sinks.append(Rectangle(name, llx, lly, urx, ury))

        # Set source
        tokens = lines[-1].split()
        name = tokens[0]
        llx, lly, urx, ury = [int(t) for t in tokens[1:]]
        self.source = Rectangle(name, llx, lly, urx, ury)

        # Identify all the bounds of sinks
        src_llx, src_lly = self.source.llx, self.source.lly
        src_urx, src_ury = self.source.urx, self.source.ury

        for s in self.sinks:
            # I don't need bound coordinates that are either on the left or
            # on the right of the source
            if s.llx > src_llx and s.llx < src_urx:
                self.x_bounds.append(Bound(s, s.llx, is_left=True))

            if s.urx > src_llx and s.urx < src_urx:
                self.x_bounds.append(Bound(s, s.urx, is_left=False))

            # Y bounds
            if s.lly > src_lly and s.lly < src_ury:
                self.y_bounds.append(Bound(s, s.lly, is_left=True))

            if s.ury > src_lly and s.ury < src_ury:
                self.y_bounds.append(Bound(s, s.ury, is_left=False))
                
        self.x_bounds = sorted(self.x_bounds, key=lambda b: (b.coord, b.sink.urx))
        self.y_bounds = sorted(self.y_bounds, key=lambda b: (b.coord, b.sink.ury))

#        print("#Sinks : %d" % len(self.sinks))
#        print("#Bounds : %d/%d" % (len(self.x_bounds), len(self.y_bounds)))
#        print("")
#
#        for b in self.x_bounds:
#            print(b)
#        print("")
#        for b in self.y_bounds:
#            print(b)
#        print("")


    def initialize_interval_trees(self):
        for s in self.sinks:
            self.T_x[s.llx:s.urx] = s
            self.T_y[s.lly:s.ury] = s

    
    def generate_nodes(self):
        active_nodes, nodes = list(), list()
        crossed_intervals = list()

        #---------------------------------------
        # X-direction
        #---------------------------------------
        # 0. Find intersection with the left-bound of the source
        for i in self.T_x[self.source.llx]:
            crossed_intervals.append(i)

        print("Crossed")
        [print("\t%s" % (i.__str__())) for i in crossed_intervals]

        if len(crossed_intervals) != 0:
            n = Node()
            [n.assoc_sinks.append(i.data) for i in crossed_intervals]
            n.llx = self.source.llx
            active_nodes.append(n)

        [print("\t%s" % (n)) for n in active_nodes]

        # 1. Search toward x-direction
        for b in self.x_bounds:
            if b.is_left is False:      # right boundary
                # Note that we don't need to compute intersection again.
                _nodes = [n for n in active_nodes if b.name in [s.name for s in n.assoc_sinks]]
                new_nodes = list()

                for n in _nodes:
                    n_new = deepcopy(n)
                    
                    for s in n_new.assoc_sinks:
                        if s.name == b.name:
                            n_new.assoc_sinks.remove(s)

                    active_nodes.append(n_new)
                    active_nodes.remove(n)
                    n.urx = b.coord
                    nodes.append(n)

            if b.is_left:       # left boundary
                # Create the copies for active nodes and update their llx.
                new_nodes = list()
                for n in active_nodes:
                    n_new = deepcopy(n)
                    n_new.assoc_sinks.append(b.sink)
                    new_nodes.append(n_new)

                [active_nodes.append(n) for n in new_nodes]
        
        #2. Close every active nodes
        for n in active_nodes:
            n.urx = self.source.urx
            nodes.append(n)

        # Check
        [print(n) for n in nodes]


        #---------------------------------------
        # Y-direction
        #---------------------------------------



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', action='store', dest='src', required=True)
    opt = parser.parse_args()

    checker = Checker()
    checker.read_input(opt.src)
    checker.initialize_interval_trees()

    checker.generate_nodes()

