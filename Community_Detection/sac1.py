# Author : Tushar Himmat Dahibhate
# Unity Id: tdahibh

import pandas as pd
import numpy as np
import csv
from igraph import *
from scipy import spatial


def simA(i, j, g):
    """ This function simulates the simA(i, j) from the reference.
        Reference: Section 4 A from Community Detection based on Structural and Attribute Similarities paper"""
    
    vertex1_attr_values = list(g.vs[i].attributes().values())
    vertex2_attr_values = list(g.vs[j].attributes().values())      
    
    return 1 - spatial.distance.cosine(vertex1_attr_values, vertex2_attr_values)


def compute_similarity_matrix(g):
    """ This function calculates the similarity matrix using cosine function """   
    
    v_count = len(g.vs)    
    for i in range(v_count):
        for j in range(v_count):              
            similarity_matrix[i][j] = simA(i, j, g)
    
    return similarity_matrix  


def composite_modularity_gain(g, v_x, community, alpha, current_community, communities):
    """ This function computes the modularity gain """
    
    # Get the delta Q Newman modularity
    delta_Q_newman = compute_delta_Q_newman(g,v_x, community, current_community, communities)
    
    # Get the delta attr modularity
    delta_Q_attr = compute_delta_Q_attr(g, v_x, community)
    
    # Compute delta Q which is the composite modularity gain
    delta_Q = alpha * delta_Q_newman + (1 - alpha) * delta_Q_attr
    
    return delta_Q


def compute_delta_Q_newman(g ,v_x, new_community, current_community, communities):   
    """ This function calculates the delta_Q_newman: It simulates the Delta_Q_Newman from the Reference.
        Reference: Section 4 A from Community Detection based on Structural and Attribute Similarities paper"""

    # Get Vertex to community mapping
    vertex_community_mapping = get_vertex_to_community_map(g, communities)    
    
    # Get the old modularity
    old_mod = g.modularity(vertex_community_mapping)
    
    # Get index of the new community
    index = communities.index(new_community)    

    # Update the community of the vertex to the new community(index) that we get in the previous step
    vertex_community_mapping[v_x] = index   
    
    # Get the new modularity
    new_mod = g.modularity(vertex_community_mapping)
            
    return new_mod - old_mod        

def compute_delta_Q_attr(g, v_x, community):
    """ This function calculates the delta_Q_attr. It simulates the Delta_Q_Attr from the Reference.
        Reference: Section 4 A from Community Detection based on Structural and Attribute Similarities paper """
    
    summation = 0.0    
    for v_i in community:        
        summation += similarity_matrix[v_x][v_i]
        
    return summation/len(community)


def get_community(g, communities, v_x):
    """ This function finds out the community of a given vertex """
    
    comm = []
    for community in communities:
        if v_x in community:
            comm = community
            break
    return comm


def get_vertex_to_community_map(g, communities):
    """ This function assigns the respective community to each vertex thus creating a mapping """
    
    vertex_to_community_mapping = [0] * g.vcount()
    
    for i, community in enumerate(communities):
        for vertex in community:
            vertex_to_community_mapping[vertex] = i
    
    return vertex_to_community_mapping


def is_similar(community1, community2):
    """ This function checks if the 2 communities are similar """
        
    c1 = set(community1)
    c2 = set(community2)
    
    if c1 == c2:
        return True
    else:
        return False


def phase1(g, alpha, communities):
    """ This function simulate the phase 1 of the SAC Algorithm
        Reference: Section 4 A from Community Detection based on Structural and Attribute Similarities paper """

    i = 0
        
    while(i < 15):
        
        for v_x in range(g.vcount()):
            
            # Get the community to which v_x belongs
            current_community = get_community(g, communities, v_x)
            new_community = []
            max_gain = -1
            
            for community in communities:
                
                if not is_similar(current_community, community):
                    
                    # Compute composite modularity gain
                    delta_Q = composite_modularity_gain(g, v_x, community, alpha, current_community, communities)
                    
                    # Selecting community with maximum gain for a given vertex
                    if(delta_Q > max_gain and delta_Q > 0):
                        max_gain = delta_Q
                        new_community = community
            
            # If maximum gain is present for a given vertex, add that vertex to the new community
            if max_gain > 0:            
                current_community.remove(v_x)
                new_community.append(v_x)
            
            # Remove the empty community
            if len(current_community) == 0 :
                communities.remove(current_community)                            
        i += 1
        
    return communities

def phase2(g, alpha, communities):
    """ This function emulates the phase 2 of the SAC1 Algorithm from the reference.
        Reference: Section 4 A from Community Detection based on Structural and Attribute Similarities paper """
    
    # Get a mapping of vertex-community
    vertex_map = get_vertex_to_community_map(g, communities)
  
    # Contract vertices. Here each community will be considered a new node
    g.contract_vertices(vertex_map, combine_attrs = "mean")
    
    # Combine the egdes
    g.simplify(combine_edges = sum)        
    
    return g


def output(communities, alpha):
    """ This function writes the communities into the file according to alpha values """
    
    a = 0    
    if alpha == 0:
        a = 0
    elif alpha == 0.5:
        a = 5
    else:
        a = 1
        
    file = open("communities_" + str(a) + ".txt", 'w+')
    for community in communities:
        for i in range(len(community) - 1):
            file.write("%s," % community[i])
        file.write(str(community[-1]))
        file.write('\n')            
    file.close()


def main(alpha):
    """ This is where the action happens """
    
    g = Graph()

   
    # Add vertices
    dataset = pd.read_csv('data/fb_caltech_small_attrlist.csv')
    
    V = len(dataset)
    
    g.add_vertices(V)
    
    for attribute in dataset.columns.tolist():
        g.vs[attribute] = dataset[attribute]

        
    # Add edges
    with open('data/fb_caltech_small_edgelist.txt') as f:
        edges = [tuple(x.split()) for x in f.readlines()]
    
    edges = [(int(edge[0]), int(edge[1])) for edge in edges]
    
    g.add_edges(edges)
    

    
    # Similarity Matrix
    global similarity_matrix
    similarity_matrix = np.zeros((V,V))
    
    
    # Phase 1
    communities = [[int(x)] for x in range(V)]
    compute_similarity_matrix(g)
    
    C1 = phase1(g, alpha, communities)
    print("Community Count for Phase 1: {}".format(len(C1)))
    
    P1_mod = g.modularity(get_vertex_to_community_map(g, C1))
    print("Modularity for Phase 1: {}".format(P1_mod))
    
    
    # Phase 2
    g = phase2(g, alpha, C1)
    
    communities = [[int(x)] for x in range(g.vcount())]
    compute_similarity_matrix(g)
  
    
    # Reapplying phase 1
    C2 = phase1(g, alpha, communities)    
    print("Community Count for Phase 2: {}".format(len(C2)))
    
    P2_mod = g.modularity(get_vertex_to_community_map(g, C2))
    print("Modularity for Phase 2: {}".format(P2_mod))
    
    
    # Write the communities to the file    
    if (P1_mod > P2_mod):
        output(C1, alpha)
        print ('Phase 1 communities have been written as they have a high modularity')
        
    else:
        output(C2, alpha)
        print ('Phase 2 communities have been written as they have a high modularity')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("INVALID! Please enter the alpha value")
    else:
        main(float(sys.argv[1]))
