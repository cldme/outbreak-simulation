import networkx as nx
import numpy as np
import pandas as pd
import random

def check_measures(time, row, isolated_nodes, delay):
    _is_isolated_node_1 = True if isolated_nodes.get(row[0]) is not None else False
    _is_isolated_node_2 = True if isolated_nodes.get(row[1]) is not None else False
    return (time < delay) or (not _is_isolated_node_1 and not _is_isolated_node_2)

def simulate_infection(seed, data, nodes, isolated_nodes, delay, infection_rate, recover_time):
    # set of infected nodes (grows with every new infected node in the network)
    infected_nodes = set({seed})
    # list with number of infected nodes for every timestamp
    infected_nodes_time = list()
    # store rank of seed node
    rank = None
    # store number of initial nodes infected by seed node (feature used to later rank nodes)
    initial_infections = 0     # this feature will be used in later questions to rank a node's influence
    initial_done = False
    # time at which seed infected first other node
    initial_infection_time = None
    # dict storing initial infection times
    infection_time = dict()
    infection_time[seed] = 1

    # initial starting time
    t = 1
    for row in data:
        # simulation housekeeping when current timestamp is done (identified by t != current new time)
        if row[2] != t:
            time_diff = row[2] - t
            infected_nodes_time.append(len(infected_nodes) * time_diff)
            t = row[2]
            _remove = set()
            for _node in infected_nodes:
                if infection_time[_node] + recover_time < t:
                    _remove.update([_node])
                    isolated_nodes[_node] = True
            infected_nodes -= _remove
            # stop checking for initial infected nodes
            if initial_infections != 0 and not initial_done:
                initial_done = True
        # check if measures are in place (and a connection does occur)
        if check_measures(t, row, isolated_nodes, delay):
            # simulate infection spreading
            if (row[0] in infected_nodes or row[1] in infected_nodes) and random.random() < infection_rate:
                infected_nodes.update([row[0], row[1]])
                if infection_time.get(row[0]) is None:
                    infection_time[row[0]] = t
                if infection_time.get(row[1]) is None:
                    infection_time[row[1]] = t
                # logic for ranking a node's influence
                if len(infected_nodes) > 0.8 * nodes and rank is None:
                    rank = t
            # check for initial infected nodes
            if (row[0] == seed or row[1] == seed) and not initial_done:
                initial_infections += 1
            # check whether the seed infects the initial node
            if initial_infection_time is None and (row[0] == seed or row[1] == seed):
                initial_infection_time = t
    infected_nodes_time.append(len(infected_nodes))
    
    return infected_nodes_time, rank, initial_infections, initial_infection_time