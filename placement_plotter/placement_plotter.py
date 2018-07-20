import matplotlib.pyplot as plt
from matplotlib.pyplot import Rectangle
from matplotlib.collections import PatchCollection
from time import gmtime, strftime

def parse_cl():
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--nodes', action="store", dest='src_nodes', required=True)
    parser.add_argument('--pl', action="store", dest='src_pl', required=True)
    parser.add_argument('--scl', action="store", dest='src_scl', required=True)
    parser.add_argument('--out', action="store", dest='out', default='out')

    return parser.parse_args()


class PlaceRegion(object):
    llx = 0
    lly = 0
    urx = 987654321
    ury = 987654321


class Node(object):
    def __init__(self, name, w, h, is_fixed, llx=0, lly=0):
        self.name = name
        self.width, self.height = w, h  # Width and height
        self.llx, self.lly = llx, lly   # Placement
        self.is_fixed = is_fixed

    def draw_gnuplot(self):
        llx, lly = self.llx, self.lly
        urx = self.llx + self.width
        ury = self.lly + self.height

        box="%d %d\n%d %d\n%d %d\n%d %d\n%d %d\n\n" % \
            (llx, lly, urx, lly, urx, ury, llx, ury, llx, lly)
        return box


def parse_bookshelf_nodes(nodes, node_dict):
    with open(nodes, 'r') as f:
        # read lines without blank lines
        lines = [l for l in (line.strip() for line in f) if l]

    # Skip the first line: UCLA nodes ...
    lines_iter = iter(lines[1:])

    for l in lines_iter:
        if l.startswith('#'): continue

        tokens = l.split()
        if tokens[0] == 'NumNodes' or tokens[0] == 'NumTerminals':
            continue

        assert len(tokens) >= 3
        name, w, h = tokens[0], int(tokens[1]), int(tokens[2])

        if (len(tokens) == 4):
            is_fixed = True
            assert tokens[3] == 'terminal' or tokens[3] == 'terminal_NI'
        else:
            is_fixed = False

        node_dict[name] = Node(name, w, h, is_fixed)


def parse_bookshelf_pl(pl, node_dict):
    with open(pl, 'r') as f:
        # read lines without blank lines
        lines = [l for l in (line.strip() for line in f) if l]

    # Skip the first line: UCLA pl ...
    lines_iter = iter(lines[1:])

    for l in lines_iter:
        if l.startswith('#'): continue

        tokens = l.split()
        assert len(tokens) > 3

        name, x, y = tokens[0], int(float(tokens[1])), int(float(tokens[2]))

        n = node_dict[name]
        n.llx, n.lly = x, y


def parse_bookshelf_scl(scl):
    """ Read an scl and determine placement region """

    with open(scl, 'r') as f:
        # read lines without blank lines
        lines = [l for l in (line.strip() for line in f) if l]

    lines_iter = iter(lines[2:])    # skip the first two lines

    urx, ury = (0.0, 0.0)

    for l in lines_iter:
        if l.startswith('#'): continue
        tokens = l.split()

        if tokens[0] == 'CoreRow':
            while True:
                tokens = next(lines_iter).split()
                if tokens[0] == 'End':
                    break

                elif tokens[0] == 'Coordinate':
                    coordinate = int(tokens[2])

                elif tokens[0] == 'Height':
                    height = int(tokens[2])

                elif tokens[0] == 'Sitewidth':
                    site_width = int(tokens[2])

                elif tokens[0] == 'Sitespacing':
                    site_spacing = int(tokens[2])

                elif tokens[0] == 'SubrowOrigin':
                    subrow_origin = int(tokens[2])
                    num_sites = int(tokens[5])

            _urx = subrow_origin + num_sites*site_spacing
            _ury = coordinate + height

            urx = _urx if _urx > urx else urx
            ury = _ury if _ury > ury else ury

    PlaceRegion.urx, PlaceRegion.ury = urx, ury


def make_placement_plot(nodes, pl, scl, dest):
    # Read bookshelf files
    parse_bookshelf_scl(scl)

    node_dict = dict()
    parse_bookshelf_nodes(nodes, node_dict)
    parse_bookshelf_pl(pl, node_dict)

    fig = plt.figure()              # Figure
    ax = fig.add_subplot(1,1,1)     # AxesSubplot

    patches = set()

    for k,v in node_dict.items():
        llx, lly = v.llx, v.lly
        w, h = v.width, v.height
        patches.add(Rectangle((llx, lly), w, h))

    print("Adding collection.")
    ax.add_collection(PatchCollection(patches, alpha=0.4))
    print("Done.")
    fig.show()
    ax.set_xlim([0,1000])
    ax.set_ylim([0,1000])
    fig.savefig('test.png')

if __name__ == '__main__':
    cl_opt = parse_cl()

    nodes = cl_opt.src_nodes
    pl = cl_opt.src_pl
    scl = cl_opt.src_scl
    dest = cl_opt.out

    make_placement_plot(nodes, pl, scl, dest)

