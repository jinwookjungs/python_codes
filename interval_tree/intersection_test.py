'''
    File name      : intersection_test.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 20:27:42 2017
    Last modified  : 2017-03-20 15:21:23
    Python version : 3.4
'''

import sys
from intervaltree import Interval, IntervalTree
from copy import deepcopy
from functools import total_ordering
from collections import OrderedDict
from itertools import count as iter_count
from itertools import product as iter_product


@total_ordering
class Reach:
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
        return "Reach(name=%r, box={(%r,%r), (%r,%r)}" \
                % (self.name, self.llx, self.lly, self.urx, self.ury)

    __str__ = __repr__

    def __eq__(self, other):
        # FIXME: A sink can have only one sink reach in current version of the
        # algorithm, since we are assuming only one layer trait is used. So 
        # equality can be checked by only using the name of sinks.
        return self.name == other.name
    
    def __lt__(self, other):
        return self.area < other.area

    def __hash__(self):
        return hash(self.name)


class Bound:
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
               + "%s)" % ("Left" if self.is_lower_bound else "Right")


class BoundPool:
    def __init__(self):
        ''' A set of bounds. We will keep two bound pools, one for x-axis 
        and the other for y-axis.
        '''
        self.bound_dict = dict()    # Key: a tuple (coord, 'lower'/'upper')
                                    # Value: a list of sinks

    def add_bound(self, sink, coord, bound_type='lower'):
        if __debug__:
            print("Add bound: %s - %d - %s" % (sink, coord, bound_type))
        assert bound_type in ('lower', 'upper')
        
        dict_key = (coord, bound_type)
        if dict_key not in self.bound_dict:
            self.bound_dict[dict_key] = list()

        self.bound_dict[dict_key].append(sink)

    def get_sorted_bounds(self):
        ''' Return a list of bounds, sorted in ascending order of coordinate.
        If there are multiple bounds having the same coordinate, an upper-bound
        will always come first in the list.
        '''
        # Frist, do secondary sort using bound (lower vs upper)
        d = sorted(self.bound_dict.items(), key=lambda t:t[0][1], reverse=True)
        # Second, do primary sort using coordinate
        d = OrderedDict(sorted(d, key=lambda t:t[0][0]))

        return [Bound(v,k[0],k[1]) for k,v in d.items()]

    def __len__(self):
        return len(self.bound_dict)

    def __iter__(self):
        return iter(self.bound_dict.items())


@total_ordering
class Node:
    ''' This class represents a node in a topology search graph. Each node has 
    a unique id, a list of sinks (essentially a map), and the bounding box of 
    its movable region.
    '''
    id_generator = iter_count(0)
    def __init__(self, sink_set, llx=None, urx=None, lly=None, ury=None):
        self.sink_dict = {s.name : s for s in sink_set}

        self.llx, self.urx = llx, urx
        self.lly, self.ury = lly, ury

        self.id = next(Node.id_generator)
    
    def add_sink(self, s):
        ''' Add a sink to the sink_dict. '''
        self.sink_dict[s.name] = s
   
    def remove_sinks(self, sinks):
        ''' Remove sinks from the node. '''
        for s in sinks:
            if s.name in self.sink_dict:
                del self.sink_dict[s.name]
            else:
                pass  # the sink is not included in this node.

    def remove_sinks_by_name_set(self, name_set):
        ''' Remove sinks (given by a set of sink names) from the node. '''
        for name in name_set:
            if name in self.sink_dict:
                del self.sink_dict[name]
            else:
                pass  # the sink is not included in this node.

    def update_movable_region(self, source):
        ''' Update movable region of this node. '''
        llx_list, lly_list = [source.llx], [source.lly]
        urx_list, ury_list = [source.urx], [source.ury]

        llx_list.extend([s.llx for s in self.sink_dict.values()])
        lly_list.extend([s.lly for s in self.sink_dict.values()])
        urx_list.extend([s.urx for s in self.sink_dict.values()])
        ury_list.extend([s.ury for s in self.sink_dict.values()])

        self.llx, self.lly = max(llx_list), max(lly_list)
        self.urx, self.ury = min(urx_list), min(ury_list)

    @property
    def area(self):
        ''' Area of the movable region defined for this Node. '''
        try:
            return (self.urx-self.llx) * (self.ury-self.lly)
        except TypeError:
            return 0 

    @property
    def sink_name_list(self):
        return sorted(list(self.sink_dict.keys()))

    @property
    def sink_set(self):
        return set(self.sink_dict.values())

    @property
    def name(self):
        return '&&'.join(self.sink_name_list)

    def __repr__(self):
        try:
            return "Node(name=%r, box={(%r,%r), (%r,%r)}, area=%r" \
                    % (self.name, self.llx, self.lly, self.urx, self.ury, self.area)
        except TypeError:
            return "Node(name=%r)" % (self.name)

    __str__ = __repr__

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
    
    def __lt__(self, other):
        return self.area < other.area

    def __len__(self):
        return len(self.sink_dict)

    def __iter__(self):
        # return iter(self.sink_dict.items())
        return iter(self.sink_dict.values())


class NodeSet(set):
    ''' A set of nodes (derived from set). '''
    def __init__(self):
        super().__init__()

    def remove_sink_from_nodes(self, s):
        ''' Remove a sink from every node contained in this set. '''
        [n.remove_sinks([s]) for n in self]

        # Eliminate empty nodes
        empty_nodes = {n for n in self if len(n)==0}
        self = self - empty_nodes

    def get_nodes_by_sink(self, s):
        ''' Return every node containing a given sink. '''
        return {n for n in self if s.name in n.sink_dict.keys()}

    def get_nodes_by_sink_name(self, name):
        ''' Return the nodes containing a given sink name. '''
        return [n for n in self \
                if len(name.intersection(n.sink_dict.keys()))!=0]

    def get_nodes_sorted(self):
        ''' Return nodes in descending order of MR area. '''
        return sorted(self, key=lambda t: (len(t.sink_dict), t.area), 
                            reverse=True)


class Partitioner:
    def __init__(self):
        self.source = None
        self.sinks = list()

        self.T_x = IntervalTree()
        self.T_y = IntervalTree()

        self.x_bounds, self.y_bounds = BoundPool(), BoundPool()

        self.nodes = None       # Genearted nodes
        self.selected = None    # Selected nodes

    def initialize_interval_trees(self):
        print("Initializing interval trees.")
        print("#Sinks      : %d" % len(self.sinks))
        print("#X/Y Bounds : %d/%d\n" % (len(self.x_bounds), \
                                         len(self.y_bounds)))
        for s in self.sinks:
            self.T_x[s.llx:s.urx] = s
            self.T_y[s.lly:s.ury] = s

        if __debug__:
            print("Interval tree for X-axis:")
            for i in self.T_x:
                print("\t{}".format(i))
            print("Interval tree for Y-axis:")
            for i in self.T_y:
                print("\t{}".format(i))
            print("")

    def find_node_candidates(self, T, bounds, lb, ub):
        crossed = list()
        node_set = NodeSet()
        node = None

        # Find intersection with the lower bound of source
        for i in T[lb]:
            crossed.append(i.data)

        if len(crossed) > 0:
            node = Node(crossed)
            node_set.add(node)

        # Now, start searching toward upper bound
        for b in bounds.get_sorted_bounds():
            if b.is_lower_bound:
                # We meet a lower bound of a sink; create a new node.
                if node is None:
                    node = Node(b.sinks)
                else:
                    node = deepcopy(node)       # Create copy and update sinks
                    [node.add_sink(s) for s in b.sinks]

                node_set.add(node)

            else:
                # We meet an upper bound of a sink.
                # Create a new node after removing sinks from current node.
                try:
                    assert node is not None
                except AssertionError:
                    sys.stderr.write("node is None... exit.\n")
                    sys.exit(-1)

                node = deepcopy(node)
                node.remove_sinks(b.sinks)

                # If the node do not have a sink any more, make it invalid.
                if len(node) == 0:
                    node = None
                else:
                    node_set.add(node)

        return node_set

    def generate_nodes(self):
        print("Generating nodes.")

        # X-direction
        print("Searching toward x-direction.")
        Nx = self.find_node_candidates(self.T_x, self.x_bounds, 
                                       self.source.llx, self.source.urx)

        for n in Nx:
            print(n)
        print("")

        # Y-direction
        print("Searching toward y-direction.")
        Ny = self.find_node_candidates(self.T_y, self.y_bounds, 
                                       self.source.lly, self.source.ury)
        for n in Ny:
            print(n)
        print("")

        # Final node set
        self.nodes = NodeSet()

        remaining = set(self.sinks)
        
        for nx, ny in iter_product(Nx, Ny):
            sinks_nx = nx.sink_set
            sinks_ny = ny.sink_set

            sinks_new = sinks_nx.intersection(sinks_ny)
            # if sinks_new in [sinks_nx, sinks_ny]:
            if len(sinks_new) > 0:
                node_new = Node(sinks_new)
                self.nodes.add(node_new)
                
                remaining = remaining - sinks_new

        # Update movable region for each node
        [n.update_movable_region(self.source) for n in self.nodes]
        print("%d nodes are found (N^2=%d).\n" \
              % (len(self.nodes), len(self.sinks)**2))

        # if __debug__:
        print("All the generated nodes:")
        [print("\t%d : %s" % (i+1, n)) for i,n in enumerate(self.nodes)]

    def select_nodes(self):
        import heapq

        # TODO: implement Lakshmi's node weighting
        print("Selecting nodes.")

        selected = list()
        sink_names = {s.name for s in self.sinks}
        candidates = {deepcopy(n) for n in self.nodes}

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
                n[-1].remove_sinks_by_name_set(sink_covered)
                if len(n) > 0:
                    candidates.append(n[-1])

            heap = [(-len(n), -n.area, n.id, n) for n in candidates]


if __name__ == '__main__':
    def read_input(partitioner, file_name):
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
            partitioner.sinks.append(Reach(name, llx, lly, urx, ury))

        # Set source
        tokens = lines[-1].split()
        name = tokens[0]
        llx, lly, urx, ury = [float(t) for t in tokens[1:]]
        partitioner.source = Reach(name, llx, lly, urx, ury)

        # Identify all the bounds of sinks
        src_llx, src_lly = partitioner.source.llx, partitioner.source.lly
        src_urx, src_ury = partitioner.source.urx, partitioner.source.ury

        if __debug__:
            print("Generating bounds.")

        for s in partitioner.sinks:
            # I don't need bound coordinates that are either on the left or
            # on the right of the source
            if s.llx > src_llx and s.llx < src_urx:
                partitioner.x_bounds.add_bound(s, s.llx, 'lower')

            if s.urx > src_llx and s.urx < src_urx:
                partitioner.x_bounds.add_bound(s, s.urx, 'upper')

            # Y bounds
            if s.lly > src_lly and s.lly < src_ury:
                partitioner.y_bounds.add_bound(s, s.lly, 'lower')

            if s.ury > src_lly and s.ury < src_ury:
                partitioner.y_bounds.add_bound(s, s.ury, 'upper')

        if __debug__:
            print("")

    def plot_generated_nodes(partitioner):
        import matplotlib.cm as cm
        import matplotlib.pyplot as plt
        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Rectangle
        from numpy import array as np_array

        areas = list()
        
        fig = plt.figure()
        fig.set_size_inches(15,20)
        ax1 = fig.add_subplot(211)

        xs = [(s.llx, s.urx) for s in partitioner.sinks + [partitioner.source]]
        ys = [(s.lly, s.ury) for s in partitioner.sinks + [partitioner.source]]

        x_max, y_max = max([x[1] for x in xs]), max([y[1] for y in ys])
        x_min, y_min = min([x[0] for x in xs]), min([y[0] for y in ys])

        for s in partitioner.sinks:
            x,y = s.llx, s.lly
            w,h = s.width, s.height
            rectangle = Rectangle((x,y), w, h, alpha=0.3)
            ax1.add_patch(rectangle)

        x,y = partitioner.source.llx, partitioner.source.lly
        w,h = partitioner.source.width, partitioner.source.height
        rectangle = Rectangle((x,y), w, h, facecolor='red', alpha=0.3)
        ax1.add_patch(rectangle)

        ax1.set_xlim([x_min,x_max])
        ax1.set_ylim([x_min,y_max])

        patches = list()
        for n in partitioner.nodes:
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

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', action='store', dest='src', required=True)
    opt = parser.parse_args()

    partitioner = Partitioner()
    read_input(partitioner, opt.src)

    partitioner.initialize_interval_trees()

    partitioner.generate_nodes()
    partitioner.select_nodes()
#    # plot_generated_nodes(partitioner)
