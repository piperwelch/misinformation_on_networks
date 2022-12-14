import gzip 
import shutil 
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import pickle
import sys

seed_val = 1

def extract_data():
    with gzip.open('higgs-social_network.edgelist.gz', 'rb') as f_in:
        with open('edgelist_file.txt', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def make_graph():
    fh = open("edgelist_file.txt", "rb")
    G = nx.read_edgelist(fh)
    for i in G.nodes():
        G.nodes[i]["misinformed"] = False
        G.nodes[i]["informed"] = False
        G.nodes[i]["malicious"] = False
        G.nodes[i]["believe_prob"] = random.uniform(0, 0.1)
        G.nodes[i]["new_status"] = None
        G.nodes[i]["targeted"] = False

    with open("G_{}.p".format(seed_val), 'wb') as f:
        pickle.dump(G, f)
    return G


def read_graph():
    with open("G_{}.p".format(seed_val), 'rb') as f:  # notice the r instead of w
        G = pickle.load(f)
    return G


def make_degree_hist():
    G = make_graph()
    degrees = []
    for node in list(G.nodes):
        degrees.append(G.degree[node])
    
    X = sorted(degrees)
    N = len(degrees)
    Y = 1- 1.0*np.arange(N)/N
    plt.loglog(X,Y,'.-')
    plt.xlabel("Degree Distribution")
    plt.ylabel("$P_>(m)$") # shorthand for P(M < m)
    plt.title("")
    plt.savefig("degree_dist.png")


def seed_disinformation(G, inf_source_percentile = None, mis_source_percentile = None, malicious = True):
    '''sets the source misinformation, if it is malicious and sets the probabilities that it spreads
    '''

    if inf_source_percentile == None and mis_source_percentile == None: #choose random source of misinformation if one is not given 
        mis_source = random.choice(list(G.nodes()))
        inf_source = random.choice(list(G.nodes()))
    else:
        degree_cent = nx.degree_centrality(G)

        inv_degree_cent_dic = {float(v): k for k, v in degree_cent.items()}

        inf_source_cent = np.percentile(list(nx.degree_centrality(G).values()), int(inf_source_percentile), interpolation="lower")
        inf_source = inv_degree_cent_dic[inf_source_cent]

        mis_source_cent = np.percentile(list(nx.degree_centrality(G).values()), int(mis_source_percentile), interpolation='lower')
        mis_source = inv_degree_cent_dic[mis_source_cent]

    G.nodes[mis_source]["misinformed"] = True
    G.nodes[mis_source]["malicious"] = malicious
    G.nodes[mis_source]["targeted"] = True
    G.nodes[inf_source]["informed"] = True



def do_one_gen(G, curr_gen, targeted_reduction, gen, degree_cent, percentile_node):
    '''
    Preforms one time step in our model 
    args: G - the graph to run our model on 
    curr_gen - the current time step 
    targeted_reduction - how much counter information impacts mis. spread 
    gen - the generation to apply counter information 
    degree_cent - the degree centrality dictionary for the nodes 
    percentile_node - which percentile node to targeted
    '''
    for node in G.nodes(): # for each node 
        #count the number of neighbors in different categories
        misinformed_count = 0
        informed_count = 0
        malicious_count = 0
        targeted_count = 0

        neighbors = list(G.neighbors(node))

        for neighbor in neighbors:
            if G.nodes[neighbor]["misinformed"] == True:
                if G.nodes[neighbor]["targeted"]:
                    misinformed_count += 1 - targeted_reduction
                else:
                    misinformed_count += 1
            if G.nodes[neighbor]["malicious"] == True:
                malicious_count+=1
            if G.nodes[neighbor]["informed"] == True:
                informed_count+=1 
            if G.nodes[neighbor]["targeted"] == True:
                targeted_count+=1
        

        if curr_gen > gen and G.nodes[node]["misinformed"] == True and degree_cent[node] >= percentile_node:
            G.nodes[node]["targeted"] = True

        #determine the influence of the neighbors on our given node
        if misinformed_count == 0 or (misinformed_count == targeted_count and curr_gen > gen):
            mis_persuade_prob = 0
        else:
            mis_persuade_prob = misinformed_count/len(neighbors) + G.nodes[node]["believe_prob"] #proportion of neighbors in x category + the node's innate gullability 
            mis_persuade_prob *= (1 + malicious_count/len(neighbors)) #bonus for malicious neighbors
            if curr_gen > gen:
                if targeted_count > 0:
                    mis_persuade_prob *= (1 - (targeted_reduction*targeted_count))
        if mis_persuade_prob < 0: 
            mis_persuade_prob = 0

        if informed_count == 0:
            inf_persuade_prob = 0
        else: 
            inf_persuade_prob = informed_count/len(neighbors) + G.nodes[node]["believe_prob"]
            if curr_gen > gen:
                if targeted_count > 0:
                    redux = targeted_reduction*targeted_count
                    if redux > 1:
                        redux = 0
                    inf_persuade_prob *= (1 + (1 - redux))

        #normalize if the probabilites are greater than 1 
        if inf_persuade_prob+mis_persuade_prob > 1: 
            inf_persuade_prob = inf_persuade_prob/(inf_persuade_prob + mis_persuade_prob)
            mis_persuade_prob = mis_persuade_prob/(inf_persuade_prob + mis_persuade_prob)

        #determine if node is changed into another cateogry 
        rand_prob = random.random()
        if G.nodes[node]["misinformed"] == True: #misinf. nodes can become neutral 
            if rand_prob < inf_persuade_prob:       
                G.nodes[node]["new_status"] = "neutral"

        if G.nodes[node]["informed"] == True: #informed nodes can become neutral 
            if rand_prob < mis_persuade_prob:
                G.nodes[node]["new_status"] = "neutral"

        if G.nodes[node]["informed"] == False and G.nodes[node]["misinformed"] == False: #neutral nodes can switch either way 
            if rand_prob < mis_persuade_prob:  #node switches to being misinformed 
                G.nodes[node]["new_status"] = "misinformed"
            if rand_prob < mis_persuade_prob + inf_persuade_prob and rand_prob > mis_persuade_prob: #node switches to being informed 
                G.nodes[node]["new_status"] = "informed"
            #else: #nothing happens to the node 

        if G.nodes[node]["misinformed"] == True and targeted_count > 0:
            flip_prob = 0.05 * targeted_count 
            if random.random() < flip_prob:
                G.nodes[node]["new_status"] == "informed"

    for node in G.nodes(): #update 
        if G.nodes[node]["new_status"] == "neutral":
            G.nodes[node]["misinformed"] = False
            G.nodes[node]["informed"] = False
            G.nodes[node]["malicious"] = False
            G.nodes[node]["targeted"] = False

        if G.nodes[node]["new_status"] == "misinformed":
            G.nodes[node]["informed"] = False
            G.nodes[node]["misinformed"] = True
            G.nodes[node]["malicious"] = round(random.uniform(0, 0.65)) #15 % chance of becoming malicious

        if G.nodes[node]["new_status"] == "informed":
            G.nodes[node]["informed"] = True
            G.nodes[node]["misinformed"] = False  
            G.nodes[node]["malicious"] = False

        G.nodes[node]["new_status"] = None 
        

def update_tracking(G):
    '''updates information about how much misinformation has spread'''
    mis_count = 0
    inf_count = 0
    neu_count = 0

    for node in G.nodes():
        if G.nodes[node]["misinformed"] == True:
            mis_count+=1
        if G.nodes[node]["informed"] == True:
            inf_count +=1
        if G.nodes[node]["informed"] == False and G.nodes[node]["misinformed"] == False:
            neu_count +=1 
    
    return mis_count, inf_count, neu_count


def run_simulation(G, num_gens, inf_source, mis_source,targeted_reduction, gen):
    degree_cent = nx.degree_centrality(G)
    percentile_node = np.percentile(list(nx.degree_centrality(G).values()), 50, interpolation="lower")
    seed_disinformation(G, inf_source, mis_source)
    mis_counts = [1]
    inf_counts = [1]
    neu_counts = [456254]

    for i in range(num_gens):
        do_one_gen(G, i, targeted_reduction, gen, degree_cent= degree_cent, percentile_node = percentile_node)
        mis, inf, neu = update_tracking(G)
        mis_counts.append(mis)
        inf_counts.append(inf)
        neu_counts.append(neu)
    return mis_counts, inf_counts, neu_counts


def main():
    gen = int(sys.argv[1])
    f = open("inf25_targeted_data_reduction_applied_at_{}.csv".format(gen), "a")
    mis_source = float(sys.argv[2])
    inf_source = float(sys.argv[3])
    targeted_reduction = float(sys.argv[4])


    random.seed(seed_val)

    G = read_graph()
    mis_counts, inf_counts, neu_counts = run_simulation(G, num_gens = 20, mis_source=mis_source*100, inf_source=inf_source*100, targeted_reduction=targeted_reduction, gen = gen)

    f.write("{},{},{},{},{},{}\n".format(targeted_reduction, mis_source, inf_source, mis_counts, inf_counts, neu_counts))
    f.close()

if __name__ == "__main__":
    main()