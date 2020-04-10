import networkx as nx
import numpy as np
import pandas as pd
import random

def check_measures(time, row, isolated_nodes, delay):
    _is_isolated_node_1 = True if isolated_nodes.get(row[0]) is not None else False
    _is_isolated_node_2 = True if isolated_nodes.get(row[1]) is not None else False
    return (time < delay) or (not _is_isolated_node_1 and not _is_isolated_node_2)

def add_to_incubate_nodes(time, node, incubate_nodes, incubate_delay):
    # add deviation to incubation time from hardcoded range(-4, 4)
    _dev = random.randrange(-4, 4, 1)
    _incubate_time = time + incubate_delay + _dev
    if incubate_nodes.get(_incubate_time) is not None:
        incubate_nodes.get(_incubate_time).update([node])
    else:
        if isinstance(node, list):
            incubate_nodes[_incubate_time] = set(node)
        else:
            incubate_nodes[_incubate_time] = set({node})
    return incubate_nodes

def add_to_recover_nodes(time, _isolate_time, node, recover_nodes, recover_delay):
    # add deviation to recover time from hardcoded range(-7, 7)
    _dev = random.randrange(-7, 7, 1)
    _recover_time = time + _isolate_time + recover_delay + _dev
    if recover_nodes.get(_recover_time) is not None:
        recover_nodes.get(_recover_time).update([node])
    else:
        recover_nodes[_recover_time] = set({node})
    return recover_nodes

def add_to_isolate_nodes(time, node, isolate_nodes):
    # add deviation to entering isolation from hardcoded range (0, 7, 1)
    _dev = random.randrange(0, 7, 1)
    _isolate_time = time + _dev
    if isolate_nodes.get(_isolate_time) is not None:
        isolate_nodes.get(_isolate_time).update([node])
    else:
        isolate_nodes[_isolate_time] = set({node})
    return isolate_nodes, _isolate_time

def check_incubate_nodes(time, incubate_nodes, isolate_nodes, recover_nodes, recover_delay):
    if incubate_nodes.get(time) is not None:
        for _node in incubate_nodes.get(time):
            isolate_nodes, _isolate_time = add_to_isolate_nodes(time, _node, isolate_nodes)
            recover_nodes = add_to_recover_nodes(time, _isolate_time, _node, recover_nodes, recover_delay)
    return isolate_nodes, recover_nodes

def check_recover_nodes(time, recover_nodes, infected_nodes, recovered_nodes):
    if recover_nodes.get(time) is not None:
        recovered_nodes.update(recover_nodes.get(time))
        infected_nodes -= recover_nodes.get(time)
    return recover_nodes, infected_nodes, recovered_nodes

def check_isolate_nodes(time, isolate_nodes, isolated_nodes):
    if isolate_nodes.get(time) is not None:
        for _node in isolate_nodes.get(time):
            isolated_nodes[_node] = True
    return isolated_nodes

def simulate_infection(seed, data, nodes, isolated_nodes, delay, infection_rate, incubate_delay, recover_delay):
    # set of infected nodes (grows with every new infected node in the network)
    infected_nodes = set({seed})
    # list with number of infected nodes for every timestamp
    infected_nodes_time = list()
    # set of recovered nodes
    recovered_nodes = set()
    # list with number of recovered nodes for every timestamp
    recovered_nodes_time = list()
    # store rank of seed node
    rank = None
    # dict storing nodes that will develop symptoms (after incubation period is over)
    incubate_nodes = dict()
    incubate_nodes = add_to_incubate_nodes(0, seed, incubate_nodes, incubate_delay)
    incubate_nodes = add_to_incubate_nodes(delay, list(isolated_nodes.keys()), incubate_nodes, incubate_delay)
    # dict storing nodes that will recover at specific timestamp (given by the key)
    recover_nodes = dict()
    # dict storing nodes that wil enter isolation at specific timestamp (given by the key)
    isolate_nodes = dict()

    # initial starting time
    t = 1
    for row in data:
        # simulation housekeeping when current timestamp is done (identified by t != current new time)
        if row[2] != t:
            time_diff = row[2] - t
            infected_nodes_time.append(len(infected_nodes) * time_diff)
            recovered_nodes_time.append(len(recovered_nodes) * time_diff)
            t = row[2]
            isolate_nodes, recover_nodes = check_incubate_nodes(t, incubate_nodes, isolate_nodes, recover_nodes, recover_delay)
            recover_nodes, infected_nodes, recovered_nodes = check_recover_nodes(t, recover_nodes, infected_nodes, recovered_nodes)
            isolated_nodes = check_isolate_nodes(t, isolate_nodes, isolated_nodes)
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
    infected_nodes_time.append(len(infected_nodes))
    isolate_nodes, recover_nodes = check_incubate_nodes(t, incubate_nodes, isolated_nodes, recover_nodes, recover_delay)
    recover_nodes, infected_nodes, recovered_nodes = check_recover_nodes(t, recover_nodes, infected_nodes, recovered_nodes)
    isolated_nodes = check_isolate_nodes(t, isolate_nodes, isolated_nodes)
    return infected_nodes_time, recovered_nodes_time, rank