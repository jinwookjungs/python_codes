'''
    File name      : intersection_test.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 20:27:42 2017
    Last modified  : 2017-02-25 22:29:37
    Python version : 
'''

import sys
from intervaltree import Interval, IntervalTree
from copy import deepcopy


class PinReach(object):
    def __init__(self, name, llx, lly, urx, ury):
        """ A diamond shape defining reachable region from a pin. """
        self.name = name
        self.llx, self.lly = llx, lly
        self.urx, self.ury = urx, ury


    def __str__(self):
        return "%s: (%d,%d), (%d,%d)" \
                % (self.name, self.llx, self.lly, self.urx, self.ury)


    def __eq__(self, other):
        return self.name == other.name


    def __hash__(self):
        return hash(self.name)


class Bound(object):
    def __init__(self, sink, coord, is_left=True):
        """ lower/upper bound of a pin reach. """
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
    def __init__(self, sink_set, llx):
        self.sink_dict = {s.name : s for s in sink_set}

        self.llx, self.urx = llx, None
        self.lly, self.ury = None, None

    
    def add_sink(self, s):
        self.sink_dict[s.name] = s

    
    def remove_sink_by_name(self, name):
        try:
            del self.sink_dict[name]         
        except KeyError as ke:
            sys.stderr.write("%r" % ke)
            sys.stderr.write("\n")
   

    def __str__(self):
        name = '/'.join([s.name for s in self.sink_dict.values()])
        return "%s llx=%r lly=%r urx=%r ury=%r" \
                % (name, self.llx, self.lly, self.urx, self.ury)


    def __hash__(self):
        names = ''.join(self.sink_dict.keys())
        return hash(names)


    def __eq__(self, other):
        return self.__hash__() == other.__hash__()



class NodeSet(object):
    def __init__(self):
        self.node_set = set()
       

    def add_node(self, n):
        self.node_set.add(n)


    def remove_node(self, n):
        try:
            self.node_set.remove(n)
        except KeyError as ke:
            sys.stderr.write("%r" % ke)
            sys.stderr.write("\n")


    def get_nodes_by_sink_name(self, name):
        """ Return nodes associated with the sink. """
        return [v for v in self.node_set if name in v.sink_dict.keys()]
                

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
            self.sinks.append(PinReach(name, llx, lly, urx, ury))

        # Set source
        tokens = lines[-1].split()
        name = tokens[0]
        llx, lly, urx, ury = [int(t) for t in tokens[1:]]
        self.source = PinReach(name, llx, lly, urx, ury)

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

        print("#Sinks : %d" % len(self.sinks))
        print("#Bounds : %d/%d" % (len(self.x_bounds), len(self.y_bounds)))
        print("")

        for b in self.x_bounds:
            print(b)
        print("")
        for b in self.y_bounds:
            print(b)
        print("")


    def initialize_interval_trees(self):
        for s in self.sinks:
            self.T_x[s.llx:s.urx] = s
            self.T_y[s.lly:s.ury] = s

        print("Interval tree")
        for i in self.T_x:
            print(i)
        print("")
        for i in self.T_y:
            print(i)
        print("")

    
    def generate_nodes(self):
        print("-"*79)
        print("Generating nodes.")
        print("-"*79)

        crossed = list()
        active_nodes = NodeSet()
        Nx = NodeSet()

        #---------------------------------------
        # X-direction
        #---------------------------------------
        # Find intersection with the left-bound of the source
        for i in self.T_x[self.source.llx]:
            crossed.append(i.data)

        # If an intersection found, create corresponding node
        print("First nodes:")
        if len(crossed) != 0:
            n = Node(crossed, self.source.llx)
            active_nodes.add_node(n)

            print(n)
        print("")

        # Now, start searching toward x-direction
        for b in self.x_bounds:
            if b.is_left is False:
                # We meet the right boundary of a sink now.
                # Find the active nodes having the sink.
                nodes = active_nodes.get_nodes_by_sink_name(b.name)

                for n in nodes:
                    n_new = deepcopy(n)
                    n_new.remove_sink_by_name(b.name)
                    
                    active_nodes.add_node(n_new)
                    active_nodes.remove_node(n)

                    # Update its urx
                    n.urx = b.coord
                    Nx.add_node(n)

            else:
                # We meet the left boundary of a sink now.
                # Create the copies for active nodes and update their llx.
                new_nodes = list()
                for n in active_nodes.node_set:
                    n_new = deepcopy(n)
                    n_new.add_sink(b.sink)
                    n_new.llx = b.coord
                    new_nodes.append(n_new)

                # If there's no active node, create one
                if len(active_nodes.node_set) == 0:
                    n_new = Node()
                    n_new.add_sink(b.sink)
                    n_new.llx = b.coord
                    new_nodes.append(n_new)

                [active_nodes.add_node(n) for n in new_nodes]
        
        #2. Close all the active nodes
        for n in active_nodes.node_set:
            n.urx = self.source.urx
            Nx.add_node(n)

        # Check
        print("Done X-direction")
        [print(n) for n in Nx.node_set]
        print("")

        #---------------------------------------
        # Y-direction
        #---------------------------------------
        crossed_sink_names = list()
        active_nodes = NodeSet()
        Ny = NodeSet()

        # 0. Find intersection with the left-bound of the source
        for i in self.T_y[self.source.lly]:
            crossed_sink_names.append(i.data.name)

        for n in Nx.node_set:
            sink_names = {n.name for n in n.sink_dict.values()}

            if sink_names.issubset(crossed_sink_names):
                n.lly = self.source.lly
                active_nodes.add_node(n)

        [Nx.remove_node(n) for n in active_nodes.node_set]

        # 1. Search toward y-direction
        for b in self.y_bounds:
            if b.is_left is False:  
                # We meet the right boundary a sink
                # Close every node having the sink
                nodes = active_nodes.get_nodes_by_sink_name(b.name)

                for n in nodes:
                    n_new = deepcopy(n)
                    n_new.remove_sink_by_name(b.name)

                    if len(n_new.sink_dict) != 0:
                        active_nodes.add_node(n_new)

                    active_nodes.remove_node(n)
                    n.ury = b.coord
                    Ny.add_node(n)

                # Remove the sink as well in the nodes not inactivate currently
                nodes = Nx.get_nodes_by_sink_name(b.name)
                for n in nodes:
                    n.sink_dict = {k:v for k,v in n.sink_dict.items() 
                                       if k != b.name}

                    # If the inactive node no more has sink, remove it.
                    if len(n.sink_dict) == 0:
                        Nx.remove_node(n)

            else:
                # We meet the left boundary of a sink
                # Brings inactive nodes
                crossed_sink_names = list()

                for i in self.T_y[b.coord]:
                    crossed_sink_names.append(i.data.name)

                for n in Nx.node_dict.values():
                    names = set(n.sink_dict.keys())
                    if names.issubset(crossed_sink_names):
                        n.lly = self.source.lly
                        active_nodes.add_node(n)

        #2. Close all the active nodes
        for n in active_nodes.node_set:
            n.ury = self.source.ury
            Ny.add_node(n)

        print("")
        [print("\t%s" % (n)) for n in Ny.node_set]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', action='store', dest='src', required=True)
    opt = parser.parse_args()

    checker = Checker()
    checker.read_input(opt.src)
    checker.initialize_interval_trees()

    checker.generate_nodes()

