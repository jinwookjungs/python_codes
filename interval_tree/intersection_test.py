'''
    File name      : intersection_test.py
    Author         : Jinwook Jung
    Created on     : Fri Feb 24 20:27:42 2017
    Last modified  : 2017-02-24 22:55:56
    Python version : 
'''

from intervaltree import Interval, IntervalTree

class Rectangle(object):
    def __init__(self, name, llx, lly, urx, ury):
        self.name = name
        self.llx, self.lly = llx, lly
        self.urx, self.ury = urx, ury


class Checker(object):
    def __init__(self):
        self.source = None
        self.sinks = list()

        self.T_x = IntervalTree()
        self.T_y = IntervalTree()


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

        print("#Sinks : %d" % len(self.sinks))


    def initialize_interval_trees(self):
        for s in self.sinks:
            self.T_x[s.llx:s.urx] = s
            self.T_y[s.lly:s.ury] = s
            
        print(self.T_x)

    
    def generate_nodes(self):
        # 1. Search toward x-direction
        for i in self.T_x[11]:
            print(i)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', action='store', dest='src', required=True)
    opt = parser.parse_args()

    checker = Checker()
    checker.read_input(opt.src)
    checker.initialize_interval_trees()

    checker.generate_nodes()

