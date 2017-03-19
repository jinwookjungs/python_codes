'''
    File name      : intersection_test.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 20:27:42 2017
    Last modified  : 2017-03-18 21:00:42
    Python version : 
'''

import sys
from intervaltree import Interval, IntervalTree
from copy import deepcopy
from functools import total_ordering
from collections import OrderedDict
from itertools import count as iter_count


@total_ordering
class SinkReach(object):
    ''' A sink pin reach. '''
    def __init__(self, name, llx, lly, urx, ury):
        self.name = name
        self.llx, self.lly = llx, lly
        self.urx, self.ury = urx, ury
    
    @property
    def width(self):
        return self.urx-self.llx

    @property
    def height(self):
        return self.ury-self.lly

    @property
    def area(self):
        return self.width * self.height

    def __repr__(self):
        return "SinkReach(name=%r, box={(%r,%r), (%r,%r)}" \
                % (self.name, self.llx, self.lly, self.urx, self.ury)

    __str__ = __repr__

    def __eq__(self, other):
        # TODO: A sink can have only one sink reach, since we are assuming
        # only one layer trait is used. So equality is checked by only using
        # the name of sinks currently.
        return self.name == other.name
    
    def __lt__(self, other):
        return self.area < other.area

    def __hash__(self):
        return hash(self.name)


class Bound(object):
    ''' Lower/upper bound of a sink reach either in x-axis or in y-axis (So, 
    a sink reach has 4 bounds; lower and upper bounds in x-axis, and 
    corresponding bounds in y-axis. This bounds are used to identify partitions
    using interval trees.
    '''
    def __init__(self, sinks, coord, bound_type='lower'):
        self.sinks = sinks              # A set of sinks
        self.coord = coord
        self.bound_type= bound_type     # 'lower' or 'upper'
        self.name = ' && '.join([s.name for s in sinks])

    @property
    def is_lower_bound(self):
        ''' Return true if this bound is a lower bound. '''
        return True if self.bound_type == 'lower' else False

    @property
    def sink_name_set(self):
        return {s.name for s in self.sinks}

    def __str__(self):
        return "%s " % (self.__class__.__name__) \
               + "(%s, %d " % (self.name, self.coord) \
               + "%s)" % ("Left" if self.is_left else "Right")


class BoundPool(object):
    def __init__(self):
        ''' A set of bounds. We will keep two kinds of bound pool, one for 
        x-axis and the other for y-axis.
        '''
        self.bound_dict = dict()    # Key: a tuple (coord, 'lower'/'upper')
                                    # Value: a list of sinks

    def add_bound(self, sink, coord, bound_type='lower'):
        print("\t%s - %d - %s" % (sink, coord, bound_type))
        assert bound_type in ('lower', 'upper')
        
        dict_key = (coord, bound_type)
        if dict_key not in bound_dict:
            self.bound_dict[dict_key] = list()

        self.bound_dict[dict_key].append(sink)

    def get_sorted_bounds(self):
        ''' Return a list of bounds, sorted in ascending order of coordinate.
        If there are multiple bounds having the same coordinate, lower bound 
        will come first in the list.
        '''
        d = OrderedDict(sorted(self.bound_dict.items(), key=lambda t:t[0]))
        return [Bound(v,k[0],k[1]) for k,v in d.items()]

    def __len__(self):
        return len(self.bound_dict)

    def __iter__(self):
        return iter(self.bound_dict.items())


class Node(object):
    ''' This class represents a node in a topology search graph. Each node has 
    a unique id, a list of sinks (essentially a map), and bounding box of its
    movable region.
    '''
    id_generator = iter_count(0)
    def __init__(self, sink_set, llx):
        self.sink_dict = {s.name : s for s in sink_set}

        self.llx, self.urx = llx, None
        self.lly, self.ury = None, None

        self.id = next(Node.id_generator)
    
    def add_sink(self, s):
        self.sink_dict[s.name] = s
    
    def remove_sink_by_name(self, name_set):
        for name in name_set:
            if name in self.sink_dict:
                del self.sink_dict[name]
            else:
                pass  # the sink is not included in this node.

    @property
    def area(self):
        try:
            return (self.urx-self.llx) * (self.ury-self.lly)
        except TypeError:
            return 0 

    @property
    def sink_name_list(self):
        return sorted(list(self.sink_dict.keys()))

    @property
    def name(self):
        return '&&'.join(self.sink_name_list)

    def __repr__(self):
        return "Node(name=%r, box={(%r,%r), (%r,%r)}, area=%r" \
                % (self.name, self.llx, self.lly, self.urx, self.ury, self.area)

    __str__ == __repr__

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __len__(self):
        return len(self.sink_dict)

    def __iter__(self):
        # return iter(self.sink_dict.items())
        return iter(self.sink_dict.values())


class NodePool(object):
    ''' A set of nodes. '''
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
        ''' Return the nodes containing the given sink. '''
        return [v for v in self.node_set \
                if len(name.intersection(set(v.sink_dict.keys())))!=0]

    def get_nodes_sorted(self):
        return sorted(self.node_set, 
                      key=lambda t: (len(t.sink_dict), t.area), 
                      reverse=True)

    def __iter__(self):
        return iter(self.node_set)


class Partitioner(object):
    def __init__(self):
        self.source = None
        self.sinks = list()

        self.T_x = IntervalTree()
        self.T_y = IntervalTree()

        self.x_bounds, self.y_bounds = BoundPool(), BoundPool()

        self.nodes = None
        self.selected = None

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
            llx, lly, urx, ury = [float(t) for t in tokens[1:]]
            self.sinks.append(SinkReach(name, llx, lly, urx, ury))

        # Set source
        tokens = lines[-1].split()
        name = tokens[0]
        llx, lly, urx, ury = [float(t) for t in tokens[1:]]
        self.source = SinkReach(name, llx, lly, urx, ury)

        # Identify all the bounds of sinks
        src_llx, src_lly = self.source.llx, self.source.lly
        src_urx, src_ury = self.source.urx, self.source.ury

        print("Generating bounds.")
        for s in self.sinks:
            # I don't need bound coordinates that are either on the left or
            # on the right of the source
            print("%r - X" % (s))
            if s.llx > src_llx and s.llx < src_urx:
                self.x_bounds.add_bound(s, s.llx, 'lower')

            if s.urx > src_llx and s.urx < src_urx:
                self.x_bounds.add_bound(s, s.urx, 'upper')

            # Y bounds
            print("%r - Y" % (s))
            if s.lly > src_lly and s.lly < src_ury:
                self.y_bounds.add_bound(s, s.lly, 'lower')

            if s.ury > src_lly and s.ury < src_ury:
                self.y_bounds.add_bound(s, s.ury, 'upper')
               
        print("")
        print("#Sinks : %d" % len(self.sinks))
        print("#Bounds : %d/%d" % (len(self.x_bounds), len(self.y_bounds)))
        print("")

        for b in self.x_bounds.get_sorted_bounds():
            print(b)
        print("")
        for b in self.y_bounds.get_sorted_bounds():
            print(b)
        print("")

    def initialize_interval_trees(self):
        for s in self.sinks:
            self.T_x[s.llx:s.urx] = s
            self.T_y[s.lly:s.ury] = s

#        print("Interval tree")
#        for i in self.T_x:
#            print(i)
#        print("")
#        for i in self.T_y:
#            print(i)
#        print("")
    
    def generate_nodes(self):
        print("-"*79)
        print("Generating nodes.")
        print("-"*79)

        crossed = list()
        active_nodes = NodePool()
        Nx = NodePool()

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

        print("")

        # Now, start searching toward x-direction
        for b in self.x_bounds.get_sorted_bounds():
            print(b)
            if b.is_left is False:
                # We meet the right boundary of a sink now.
                # Find the active nodes having the sink.
                nodes = active_nodes.get_nodes_by_sink_name(b.sink_name_set)

                for n in nodes:
                    n_new = deepcopy(n)
                    n_new.remove_sink_by_name(b.sink_name_set)
                    
                    if len(n_new.sink_dict) != 0:
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
                    print(n)
                    n_new = deepcopy(n)
                    [n_new.add_sink(s) for s in b.sinks]
                    n_new.llx = b.coord
                    new_nodes.append(n_new)

                # If there's no active node, create one
                if len(active_nodes.node_set) == 0:
                    n_new = Node(b.sinks, b.coord)
                    new_nodes.append(n_new)

                [active_nodes.add_node(n) for n in new_nodes]
        
        #2. Close all the active nodes
        for n in active_nodes.node_set:
            n.urx = self.source.urx
            Nx.add_node(n)

        # Check
        print("Done X-direction")
        [print(n) for n in Nx]
        print("")

        #---------------------------------------
        # Y-direction
        #---------------------------------------
        print("Search toward y-direction")
        crossed_sink_names = list()
        active_nodes = NodePool()
        Ny = NodePool()

        # 0. Find intersection with the left-bound of the source
        for i in self.T_y[self.source.lly]:
            crossed_sink_names.append(i.data.name)

        for n in Nx.node_set:
            sink_names = {sink.name for sink in n}

            if sink_names.issubset(crossed_sink_names):
                n.lly = self.source.lly
                active_nodes.add_node(n)

        [Nx.remove_node(n) for n in active_nodes.node_set]

        # 1. Search toward y-direction
        for b in self.y_bounds.get_sorted_bounds():
            print(b)
            if b.is_left is False:  
                print(b.is_left)
                # We meet the right boundary of a sink.
                # Close every node having the sink.
                nodes = active_nodes.get_nodes_by_sink_name(b.sink_name_set)

                for n in nodes:
                    print("\t%r" % (n))
                    n_new = deepcopy(n)
                    n_new.remove_sink_by_name(b.sink_name_set)

                    if len(n_new.sink_dict) != 0:
                        active_nodes.add_node(n_new)

                    active_nodes.remove_node(n)
                    n.ury = b.coord
                    Ny.add_node(n)

                # Remove the sink in the nodes not inactivted currently too
                nodes = Nx.get_nodes_by_sink_name(b.sink_name_set)
                for n in nodes:
                    new_dict = {k:v for k,v in n.sink_dict.items() 
                                       if k != b.name}

                    # If the inactive node no more has sink, remove it.
                    if len(new_dict) == 0:
                        Nx.remove_node(n)

            else:
                print(b.is_left)
                # We meet the left boundary of a sink
                # Brings inactive nodes
                crossed_sink_names = list()
                
                for i in self.T_y[b.coord]:
                    crossed_sink_names.append(i.data.name)

                print(crossed_sink_names)
                for n in Nx:
                    names = set(n.sink_dict.keys())
                    print(names.issubset(crossed_sink_names))
                    if names.issubset(crossed_sink_names) and n.lly is None:
                        n.lly = b.coord
                        active_nodes.add_node(n)

        #2. Close all the active nodes
        for n in active_nodes.node_set:
            n.ury = self.source.ury
            Ny.add_node(n)

        self.nodes = Ny.get_nodes_sorted()
        print("")
        [print("\t%s" % (n)) for n in self.nodes]

    def select_nodes(self):
        import heapq

        selected = list()
        sink_names = {s.name for s in self.sinks}
        candidates = deepcopy(self.nodes)

        print("Num candidates: %d" % (len(candidates)))

        # Priority: #sinks, area. 
        # If they are the same, use the one created earlir.
        heap = [(-len(n), -n.area, n.id, n) for n in candidates]

        while len(sink_names) > 0:
            heapq.heapify(heap)

            selected.append(heapq.heappop(heap)[-1])
            print(selected[-1])

            sink_covered = selected[-1].sink_name_list
            sink_names = set(sink_names) - set(sink_covered)
            
            candidates = list()
            for n in heap:
                n[-1].remove_sink_by_name(sink_covered)
                if len(n) > 0:
                    candidates.append(n[-1])

            heap = [(-len(n), -n.area, n.id, n) for n in candidates]

    def plot_generated_nodes(self):
        import matplotlib.cm as cm
        import matplotlib.pyplot as plt
        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Rectangle
        from numpy import array as np_array

        areas = list()
        
        fig = plt.figure()
        fig.set_size_inches(15,20)
        ax1 = fig.add_subplot(211)

        xs = [(s.llx, s.urx) for s in self.sinks + [self.source]]
        ys = [(s.lly, s.ury) for s in self.sinks + [self.source]]

        x_max, y_max = max([x[1] for x in xs]), max([y[1] for y in ys])
        x_min, y_min = min([x[0] for x in xs]), min([y[0] for y in ys])

        for s in self.sinks:
            x,y = s.llx, s.lly
            w,h = s.width, s.height
            rectangle = Rectangle((x,y), w, h, alpha=0.3)
            ax1.add_patch(rectangle)

        x,y = self.source.llx, self.source.lly
        w,h = self.source.width, self.source.height
        rectangle = Rectangle((x,y), w, h, facecolor='red', alpha=0.3)
        ax1.add_patch(rectangle)

        ax1.set_xlim([x_min,x_max])
        ax1.set_ylim([x_min,y_max])

        patches = list()
        for n in self.nodes:
            x,y = n.llx, n.lly
            w,h = n.width, n.height
            rectangle = Rectangle((x,y), w, h)
            patches.append(rectangle)
            areas.append(n.area)


        ax2 = fig.add_subplot(212)
        col = PatchCollection(patches, alpha=0.4)
        col.set(array=np_array(areas), cmap='jet')

        ax2.add_collection(col)
        ax2.set_xlim([x_min,x_max])
        ax2.set_ylim([x_min,y_max])
        # plt.colorbar(col)

        fig.savefig('test.png', dpi=200)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', action='store', dest='src', required=True)
    opt = parser.parse_args()

    partitioner = Partitioner()
    partitioner.read_input(opt.src)
    partitioner.initialize_interval_trees()

    partitioner.generate_nodes()
    print("")
    partitioner.select_nodes()
    partitioner.plot_generated_nodes()

