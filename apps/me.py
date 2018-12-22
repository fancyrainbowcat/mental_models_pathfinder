from __future__ import print_function

# Sabine Kaupp - master's thesis 2018
# Pathfinding for shortest pathes in network from input csv matrix

###############################
### ____ libraries ____ ###
###############################

try:
    import matplotlib.pyplot as plt
except:
    raise
import networkx as nx
from numpy import genfromtxt
import json
import sys

###############################
### ____ functions ____ ###
###############################

# Load file

def load_csv(file):
    return genfromtxt(file, delimiter=';')

# Generate graph from input numpy csv matrix
def generate_graph_csv(input_csv):
    row_length = len(input_csv)
    col_length = len(input_csv[0])

    print('Row length '+str(row_length)+' col length '+str(col_length))
    G = nx.Graph()

    # we skip the main diagonal as nodeX <-> nodeX distance = 0
    for column_offset in range(1, col_length):
        # step through upper right diagonals and add egdes with distance as weight
        for i in range(0, row_length-column_offset):
            G.add_edge(str(i+column_offset), str(i),
                       weight=input_csv[i][i+column_offset])
            print('Adding edge ('+str(i+column_offset)+','+str(i)+') = ' +
                  str(input_csv[i][i+column_offset]))
    return G

# Generate graph from input numpy csv matrix
def generate_graph_json(input_json):
    G = nx.Graph()

    # we skip the main diagonal as nodeX <-> nodeX distance = 0
    for object in input_json:
        print(object, file  = sys.stderr)
        if('src' in object.keys()):
            G.add_edge(str(object['src']), str(object['dst']),
                        weight=float(object['value']))
            print('Adding edge ('+str(object['src'])+','+str(object['dst'])+') = ' +str(object['value']))
    return G

# Generates reduced graph out of full graph


def save_graph_png(file, graph):
    # Draw graph
    # positions for all nodes
    pos = nx.spring_layout(graph)
    # nodes
    nx.draw_networkx_nodes(graph, pos, node_size=700)
    # edges
    nx.draw_networkx_edges(graph, pos=pos)
    # labels
    nx.draw_networkx_labels(graph, pos, font_size=20, font_family='sans-serif')

    plt.axis('off')
    # save as png
    os.mkdir('./try');
    file = './try/'+file
    plt.savefig(file)
    plt.clf()

# export graph to json

def save_graph_json(file, graph):
    os.mkdir('./try');
    file = './try/'+file
    with open(file, 'w') as outfile:
        json.dump(nx.node_link_data(graph), outfile)

def import_graph_json(file):
    with open(file, 'w') as infile:
        data = json.load(infile)
        return nx.node_link_graph(data)

def reduce_graph(G):
    S = nx.Graph()

    # for every node in graph
    for i in range(0, G.number_of_nodes()):
        # determine shortest paths to every other node
        A = nx.single_source_dijkstra_path(G, str(i))
        print(A)
        # for every node in shortest path dictionary
        for i in range(len(A)):
            # step through connected nodes
            prev = A[str(i)][0]
            for node in A[str(i)]:
                # if edge does not exist yet
                if(not S.has_edge(str(prev), str(node))):
                    if(node != prev):
                        # add it
                        S.add_edge(prev, node, weight=float(G[node][prev]['weight']))
                        print(prev+' to '+node+' with weight ' + str(G[node][prev]['weight']))         
                prev = node
    return S


# compute average matrix

def compute_average (input_csv, input_csv2):
    row_length = len(input_csv)
    col_length = len(input_csv[0])
    A = nx.Graph()

    # we skip the main diagonal as nodeX <-> nodeX distance = 0
    for column_offset in range (1, col_length):
        # step through upper right diagonals and add egdes with averaged weights
        for i in range(0, row_length-column_offset):
            G.add_edge(str(i+column_offset), str(i),
                       weight=(input_csv[i][i+column_offset] + input_csv2[i][i+column_offset]) / 2)
            print('Adding edge ('+str(i+column_offset)+','+str(i)+') = ' +
                  str((input_csv[i][i+column_offset] + input_csv2[i][i+column_offset]) / 2))
        return A


# Generate graph from input numpy csv matrix
def generate_graph(input_csv):
    row_length = len(input_csv)
    col_length = len(input_csv[0])

    print('Row length '+str(row_length)+' col length '+str(col_length))
    G = nx.Graph()

    # we skip the main diagonal as nodeX <-> nodeX distance = 0
    for column_offset in range(1, col_length):
        # step through upper right diagonals and add egdes with distance as weight
        for i in range(0, row_length-column_offset):
            G.add_edge(str(i+column_offset), str(i),
                       weight=input_csv[i][i+column_offset])
            print('Adding edge ('+str(i+column_offset)+','+str(i)+') = ' +
                  str(input_csv[i][i+column_offset]))
    return G

###############################
### ____ main function ____ ###
###############################

# Load input matrix
# csv = load_csv('try2.csv')
# print(csv)

# csv2 = load_csv('try2_2.csv')
# print(csv2)
# print csv2[4][7]

# # Generate graph from input csv
# G = generate_graph(csv)

# # Create reduced graph dummy
# S = reduce_graph(G, csv)

# A = compute_average(csv, csv2)

# # Export graphs
# save_graph_png('weighted_graph_S.png', S)
# save_graph_png('weighted_graph_G.png', G)

# # Export jsons
# save_graph_json('weighted_graph_S.json', S)
# save_graph_json('weighted_graph_G.json', G) s