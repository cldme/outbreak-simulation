import networkx as nx
import numpy as np
import pandas as pd

def simulate_infection(seed, data, N_nodes):
    # set of infected nodes (grows with every new infected node in the network)
    infected_nodes = set({seed})
    # list with number of infected nodes for every timestamp
    infected_nodes_time = list()
    # set of edges to be removed after simulation is done for current timestamp
    remove_edges = list()
    # store rank of seed node
    rank = None
    # store number of initial nodes infected by seed node (feature used to later rank nodes)
    initial_infections = 0     # this feature will be used in later questions to rank a node's influence
    initial_done = False
    # time at which seed infected first other node
    initial_infection_time = None

    # generate the graph
    graph = nx.Graph()

    # initial starting time
    t = 1
    for row in data:
        # simulation housekeeping when current timestamp is done (identified by t != current new time)
        if row[2] != t:
            time_diff = row[2] - t
            infected_nodes_time.append(len(infected_nodes) * time_diff)
            t = row[2]
            graph.remove_edges_from(remove_edges)
            remove_edges.clear()
            # stop checking for initial infected nodes
            if initial_infections != 0 and not initial_done:
                initial_done = True
        # build graph by adding edges (simulate infection / info spreading)
        graph.add_edge(row[0], row[1])
        # keep track of edges added at current timestamp (used when moving to next timestamp for removing them)
        remove_edges.append((row[0], row[1]))
        if row[0] in infected_nodes or row[1] in infected_nodes:
            infected_nodes.update([row[0], row[1]])
            # logic for ranking a node's influence
            if len(infected_nodes) > 0.8 * N_nodes and rank is None:
                rank = t
        # check for initial infected nodes
        if (row[0] == seed or row[1] == seed) and not initial_done:
            initial_infections += 1
        # check whether the seed infects the initial node
        if initial_infection_time is None and (row[0] == seed or row[1] == seed):
            initial_infection_time = t
    infected_nodes_time.append(len(infected_nodes))
    
    return infected_nodes_time, rank, initial_infections, initial_infection_time