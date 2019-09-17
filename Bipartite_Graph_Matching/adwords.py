## Author - Tushar Dahibhate
## Unity-Id - tdahibh

import sys
import pandas as pd
import math
import random

random.seed(0)

#------------------------------------------------------------------------------------

class Advertiser:
    """ This class represents the Advertiser
            id - Id of the Advertiser
            budget - Budget of the Advertiser
            bids - Dictionary containing all the keywords and their respective bids
    """
    
    def __init__(self, id, budget, bids):
        self.id = id        
        self.budget = budget
        self.bids = bids

#------------------------------------------------------------------------------------

def process_data():    
    """ This function processes the data """
    
    advertiser_budget = dict()
    query_neighbours = dict()
    advertisers = dict()

    df = pd.read_csv('bidder_dataset.csv')

    for index in range(0, df.shape[0]):
                   
        advertiser = int(df.iloc[index]['Advertiser'])

        budget = float(df.iloc[index]['Budget'])

        key_word = df.iloc[index]['Keyword']

        bid_value = float(df.iloc[index]['Bid Value'])
                        
        if advertiser not in advertiser_budget:
            advertiser_budget[advertiser] = budget
        
        if advertiser not in advertisers:
            advertisers[advertiser] = Advertiser(advertiser, advertiser_budget[advertiser], {key_word: bid_value})
        else:
            advertisers[advertiser].bids[key_word] = bid_value
                        
        if key_word not in query_neighbours:
            query_neighbours[key_word] = [advertiser]
        else:
            query_neighbours[key_word].append(advertiser) 
                    
    return advertisers, advertiser_budget, query_neighbours

#------------------------------------------------------------------------------------

def get_queries():
    """ This function returns a list of all the queries """
    
    with open('queries.txt', 'r') as f:
        queries = [line.strip() for line in f]
    return queries

#------------------------------------------------------------------------------------

def greedy(queries, advertisers, advertiser_budget, query_neighbours):
    """ This function implements the greedy algorithm in the documentation"""
    
    total_revenue = 0
    
    for query in queries:
        neighbours = query_neighbours[query]             
                
        if has_sufficient_budget(advertisers, query, neighbours):             
            max_bid = get_highest_bid_greedy(neighbours, advertisers, query)            
            total_revenue += max_bid     
            
    return total_revenue


def get_highest_bid_greedy(neighbours, advertisers, query):
    """ This function returns the highest bid and decrements the bid from the advertiser's balance
        for the greedy algorithm
    """
    
    max_bid = 0
    max_bidder = 0
        
    for neighbour in neighbours:        
        bid = advertisers[neighbour].bids[query]        
        if bid > max_bid and bid <= advertisers[neighbour].budget:
            max_bid = bid
            max_bidder = neighbour
            
    advertisers[max_bidder].budget -= max_bid
    
    return max_bid


def process_cr_greedy():
    """ This function will calculate the competitive ratio for Greedy approach"""
        
    total_revenue = 0.0
    avg_revenue = 0.0
    
    for x in range(0, 100):    

        advertisers, advertiser_budget, query_neighbours = process_data() 
        queries = get_queries()

        random.shuffle(queries)

        total_revenue += greedy(queries, advertisers, advertiser_budget, query_neighbours)        
        
    avg_revenue = total_revenue/100    
    competitive_ratio = avg_revenue/sum(advertiser_budget.values())
    
    return competitive_ratio    


#------------------------------------------------------------------------------------

def has_sufficient_budget(advertisers, query, neighbours):
    """ This function checks if the neighbours have sufficient balance or not"""
    
    for neighbour in neighbours:        
        bid_value = advertisers[neighbour].bids[query]
        
        if advertisers[neighbour].budget >= bid_value:
            return True     
        
    return False    

#------------------------------------------------------------------------------------

def msvv(queries, advertisers, advertiser_budget, query_neighbours):
    """ This function implements the MSVV algorithm in the documentation"""
    
    total_revenue = 0
    
    for query in queries:
        neighbours = query_neighbours[query]             
                
        if has_sufficient_budget(advertisers, query, neighbours):             
            max_bid = get_highest_bid_msvv(neighbours, advertisers, query, advertiser_budget)            
            total_revenue += max_bid     
            
    return total_revenue


def compute_function_X_u(advertisers, advertiser_budget, neighbour):
    """ This function calculates the function(X_u) given in the documentation"""
    
    X_u = (advertiser_budget[neighbour] - advertisers[neighbour].budget)/advertiser_budget[neighbour]    
    e = math.exp(X_u - 1)
    
    return 1 - e


def get_highest_bid_msvv(neighbours, advertisers, query, advertiser_budget):
    """ This function returns the highest bid and decrements the bid from the advertiser's balance 
        for the msvv algorithm
    """
    
    max_bid = 0
    max_bidder = 0
    max_value = -float("inf")
        
    for neighbour in neighbours:        
        
        function_X_u = compute_function_X_u(advertisers, advertiser_budget, neighbour)
        bid = advertisers[neighbour].bids[query]  
                
        if function_X_u * bid > max_value and bid <= advertisers[neighbour].budget:            
            max_bid = bid
            max_bidder = neighbour
            max_value = function_X_u * bid
            
    advertisers[max_bidder].budget -= max_bid
    
    return max_bid


def process_cr_msvv():
    """ This function will calculate the competitive ratio for MSVV approach"""
        
    total_revenue = 0.0
    avg_revenue = 0.0
    
    for x in range(0, 100):        
        advertisers, advertiser_budget, query_neighbours = process_data() 
        queries = get_queries()

        random.shuffle(queries)

        total_revenue += msvv(queries, advertisers, advertiser_budget, query_neighbours)        
        
    avg_revenue = total_revenue/100    
    competitive_ratio = avg_revenue/sum(advertiser_budget.values())
    
    return competitive_ratio    

#------------------------------------------------------------------------------------

def balance(queries, advertisers, advertiser_budget, query_neighbours):
    """ This function implements the balance algorithm in the documentation"""
    
    total_revenue = 0
    
    for query in queries:
        neighbours = query_neighbours[query]             
                
        if has_sufficient_budget(advertisers, query, neighbours):             
            
            max_bid = get_highest_bid_balance(neighbours, advertisers, query, advertiser_budget)            
            total_revenue += max_bid     
            
    return total_revenue

def get_highest_bid_balance(neighbours, advertisers, query, advertiser_budget):
    """ This function returns the highest bid and decrements the bid from the advertiser's balance 
        for the balance algorithm
    """
    
    max_bid = 0
    max_bidder = 0
    max_budget = -float("inf")
        
    for neighbour in neighbours:        
                
        bid = advertisers[neighbour].bids[query]  
                
        if advertisers[neighbour].budget > max_budget and bid <= advertisers[neighbour].budget:            
            max_bid = bid
            max_bidder = neighbour
            max_budget = advertisers[neighbour].budget
            
    advertisers[max_bidder].budget -= max_bid
    
    return max_bid


def process_cr_balance():
    """ This function will calculate the competitive ratio for Balance approach"""
        
    total_revenue = 0.0
    avg_revenue = 0.0
    
    for x in range(0, 100):        
        advertisers, advertiser_budget, query_neighbours = process_data() 
        queries = get_queries()

        random.shuffle(queries)

        total_revenue += balance(queries, advertisers, advertiser_budget, query_neighbours)        
        
    avg_revenue = total_revenue/100    
    competitive_ratio = avg_revenue/sum(advertiser_budget.values())
    
    return competitive_ratio 

#------------------------------------------------------------------------------------

def main(method):
    """ This is where all the action happens"""
    
    queries = get_queries()
    
    advertisers, advertiser_budget, query_neighbours = process_data() 
        
    if method == 'greedy':        
        
        total_revenue = greedy(queries, advertisers, advertiser_budget, query_neighbours)    
        print("{:0.2f}".format(total_revenue))
        competitive_ratio = process_cr_greedy()
        print("{:0.2f}".format(competitive_ratio))
        
    elif method == 'msvv':            
        
        total_revenue = msvv(queries, advertisers, advertiser_budget, query_neighbours)    
        print("{:0.2f}".format(total_revenue))
        competitive_ratio = process_cr_msvv()
        print("{:0.2f}".format(competitive_ratio))
        
    else:
        
        total_revenue = balance(queries, advertisers, advertiser_budget, query_neighbours)
        print("{:0.2f}".format(total_revenue))
        competitive_ratio = process_cr_balance()
        print("{:0.2f}".format(competitive_ratio))

#------------------------------------------------------------------------------------

if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        if sys.argv[1] in ['greedy', 'msvv', 'balance']:
            main(sys.argv[1])
        else:
            print("Please enter a valid input!")
    else:
        print("Please enter a valid input!")
