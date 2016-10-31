""" Main console scripts entry point. """

import argparse
import copy

from . import core
from . import sim

commands = ['simulate', 'createsim', 'showsim', 'plot']


def simulate(args):
    """run a simulation"""
    s = sim.Sim(args.sim_path)
    df = core.simulate(s)
    if args.reproduce:
        if not hasattr(s, 'results'):
            raise ValueError("No results in {}".format(args.sim_path))
        if all(s.results == df):
            print("*** Simulation reproduced: OK ***")
        else:
            if args.out_path is None:
                args.out_path = args.sim_path + '.fail'
            s2 = copy.copy(s)
            s2.results = df
            s2.dump(args.out_path)
            print("*** Simulation reproduced: FAIL ***")
            print("Results written to: {}".format(args.out_path))
    else:
        s.results = df
        if args.out_path is not None:
            path = args.out_path
        else:
            path = args.sim_path
        s.dump(path)
        print("Results written to: {}".format(path))


def createsim(args):
    """create a new simulation"""
    print("Command not implemented!")


def showsim(args):
    """show simulation details"""
    print("Command not implemented!")


def plot(args):
    """plot simulation results"""
    print("Command not implemented!")


### Parsers

def simulate_parser(parser):
    parser.add_argument('sim_path',
                        metavar='simulation',
                        help='path to simulation file')
    parser.add_argument('-r',
                        '--reproduce',
                        action='store_true',
                        help='re-simulate and check results are the same')
    parser.add_argument('-o',
                        '--output',
                        dest='out_path',
                        metavar='path',
                        help='write simulation to %(metavar)s')


def createsim_parser(parser):
    pass


def showsim_parser(parser):
    pass


def plot_parser(parser):
    pass


def main():
    __globals__ = globals()
    descr = "reproducible simulation for lazy Python programmers"
    parser = argparse.ArgumentParser(description=descr)
    subparsers = parser.add_subparsers()
    for cmd in commands:
        cmdf = __globals__[cmd]
        subp = subparsers.add_parser(cmd, help=cmdf.__doc__)
        __globals__[cmd + '_parser'](subp)
        subp.set_defaults(func=cmdf)
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.error("please specify at least one command")
