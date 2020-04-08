import networkx as nx
import numpy as np
import pandas as pd
import random

def check_measures(time, row, isolated_nodes, delay):
    _is_isolated_node_1 = True if isolated_nodes.get(row[0]) is not None else False
    _is_isolated_node_2 = True if isolated_nodes.get(row[1]) is not None else False
    return (time < delay) or (not _is_isolated_node_1 and not _is_isolated_node_2)

def add_to_incubate_nodes(time, node, incubate_nodes, incubate_delay):
    _incubate_time = time + incubate_delay
    if incubate_nodes.get(_incubate_time) is not None:
        incubate_nodes.get(_incubate_time).update([node])
    else:
        incubate_nodes[_incubate_time] = set({node})
    return incubate_nodes

def add_to_recover_nodes(time, node, recover_nodes, recover_delay):
    _recover_time = time + recover_delay
    if recover_nodes.get(_recover_time) is not None:
        recover_nodes.get(_recover_time).update([node])
    else:
        recover_nodes[_recover_time] = set({node})
    return recover_nodes

def check_incubate_nodes(time, incubate_nodes, isolated_nodes, recover_nodes, recover_delay):
    if incubate_nodes.get(time) is not None:
        for _node in incubate_nodes.get(time):
            recover_nodes = add_to_recover_nodes(time, _node, recover_nodes, recover_delay)
            isolated_nodes[_node] = True
    return isolated_nodes, recover_nodes

def check_recover_nodes(time, recover_nodes, infected_nodes):
    if recover_nodes.get(time) is not None:
        infected_nodes -= recover_nodes.get(time)
    return recover_nodes, infected_nodes

def simulate_infection(seed, data, nodes, isolated_nodes, delay, infection_rate, incubate_delay, recover_delay):
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
    # dict storing nodes that will develop symptoms (after incubation period is over)
    incubate_nodes = dict()
    incubate_nodes[incubate_delay] = set({seed})
    # dict storing nodes that will recover at specific timestamp (given by the key)
    recover_nodes = dict()
    recover_nodes[recover_delay] = set({seed})
    recover_nodes[recover_delay + delay] = set(isolated_nodes)

    # initial starting time
    t = 1
    for row in data:
        # simulation housekeeping when current timestamp is done (identified by t != current new time)
        if row[2] != t:
            time_diff = row[2] - t
            infected_nodes_time.append(len(infected_nodes) * time_diff)
            t = row[2]
            isolated_nodes, recover_nodes = check_incubate_nodes(t, incubate_nodes, isolated_nodes, recover_nodes, recover_delay)
            recover_nodes, infected_nodes = check_recover_nodes(t, recover_nodes, infected_nodes)
            # stop checking for initial infected nodes
            if initial_infections != 0 and not initial_done:
                initial_done = True
        # check if measures are in place (and a connection does occur)
        if check_measures(t, row, isolated_nodes, delay):
            # simulate infection spreading
            if (row[0] in infected_nodes or row[1] in infected_nodes) and random.random() < infection_rate:
                infected_nodes.update([row[0], row[1]])
                if isolated_nodes.get(row[0]) is None:
                    incubate_nodes = add_to_incubate_nodes(t, row[0], incubate_nodes, incubate_delay)
                if isolated_nodes.get(row[1]) is None:
                    incubate_nodes = add_to_incubate_nodes(t, row[1], incubate_nodes, incubate_delay)
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
    isolated_nodes, recover_nodes = check_incubate_nodes(t, incubate_nodes, isolated_nodes, recover_nodes, recover_delay)
    recover_nodes, infected_nodes = check_recover_nodes(t, recover_nodes, infected_nodes)
    return infected_nodes_time, rank, initial_infections, initial_infection_time