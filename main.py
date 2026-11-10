import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import string
import math

# initial brute force optimization for party arrangement problem
friends = ["mac", "dee", "charlie", "dennis"] # all friends
# relationship matrix
relationships = np.array([
# mac, dee, charlie, dennis    
    [0, 1, -1, -1], #mac
    [1, 0, -1, -1], #dee
    [-1, -1, 0, 1], #charlie
    [-1, -1, 1, 0] #dennis
])
# Create a DataFrame for better visualization
df = pd.DataFrame(relationships, index=friends, columns=friends)
# fitness function to evaluate the happiness of a given party arrangement
def fitness_function1(party_arrangement, relationships):
    happiness = 0

    for party in party_arrangement:
        for i in party:
            for j in party:
                if i != j:
                    happiness += relationships[i][j]

    return happiness
# Parameter sweep function to find the best party arrangement
def party_arrangement_param_sweep():
    best_score = float('-inf')
    best_arrangement = None
    all_results = []

    # Generate all possible arrangements of friends into two parties
    from itertools import combinations

    # Iterate through all combinations of friends to form two parties
    # combinations creates a tuple of indices for the first party, and the second party is formed by the remaining friends
    for party1 in combinations(range(len(friends)), party_size):
        party2 = [i for i in range(len(friends)) if i not in party1]
        arrangement = [list(party1), party2]
        score = fitness_function1(arrangement, relationships)
        all_results.append((arrangement, score))
        # Update the best score and arrangement if the current score is better
        if score > best_score:
            best_score = score
            best_arrangement = arrangement

    return best_arrangement, best_score, all_results
"""
# Run the parameter sweep to find the best arrangement
best_arrangement, best_score, all_results = party_arrangement_param_sweep()
print(f"The best party arrangement is: {best_arrangement}")
print(f"The best fitness score is: {best_score}")
# Print all results
for arrangement, score in all_results:
    print(f"Arrangement: {arrangement}, Fitness Score: {score}")
"""

####################################################################
#      Genetic Algorithm
####################################################################
# building the genetic algorithm for party arrangement problem
#settings
new_or_old = False # change this to false to run original relationship matrix and true to run on generated matrix
#num_friends = 20 this is now set in loop
population_size = 10 # this is now set in the loop
number_of_parties = 2
party_size = 0

num_generations = 50
mutation_rate = 0.1
tournament_size = 2

# number of runs on same relationmship matrix
num_runs = 10


# create an individual by randomly shuffling the friends and splitting them into two parties
def create_individual(num_friends, number_of_parties):
    # Randomly shuffle the friends and split them into two parties
    shuffled_friends = random.sample(range(num_friends), num_friends)
    party_size = num_friends // number_of_parties
    return [shuffled_friends[:party_size], shuffled_friends[party_size:]]

# create a population of individuals
def create_population(size, num_friends, number_of_parties):
    population = []
    for i in range(size):
        individual = create_individual(num_friends, number_of_parties)
        population.append(individual)   
    return population

# fitness function to evaluate the happiness of a given party arrangement
def fitness_function(party_arrangement, relationships):
    happiness = 0

    for party in party_arrangement:
        for i in party:
            for j in party:
                if i != j:
                    happiness += relationships[i][j]

    return happiness

# select an individual from the population using tournament selection
def tournament_selection(population, relationships, tournament_size=2): # can edit the tournament size to change the selection pressure
    # Randomly select individuals for the tournament
    tournament = random.sample(population, tournament_size)
    # Evaluate the fitness of each individual in the tournament
    fitness_scores = [fitness_function(individual, relationships) for individual in tournament]
    # Select the individual with the highest fitness score
    winner_index = np.argmax(fitness_scores)
    return tournament[winner_index]

def crossover(parent1, parent2):
    # Create a child by combining the parties of the two parents
    party_size = len(parent1[0])  # Assuming both parents have the same party size
    child_party1 = [random.choice(parent1[0])]
    # Fill the rest of child_party1 with friends from parent2, ensuring no duplicates
    remaining_friends = [friend for party in parent1 for friend in party if friend not in child_party1]
    parent2_candidates = [friend for friend in parent2[0] if friend in remaining_friends]
    # Fill child_party1 until it reaches the desired party size
    while len(child_party1) < party_size:
        if parent2_candidates:
            selected_friend = random.choice(parent2_candidates)
        else:
            selected_friend = random.choice(remaining_friends)
        child_party1.append(selected_friend)
        remaining_friends.remove(selected_friend)

        if selected_friend in parent2_candidates:
            parent2_candidates.remove(selected_friend)

    child_party2 = remaining_friends
    return [child_party1, child_party2]

def mutation(individual, mutation_rate=0.1):

    # create a copy so we don't change the original parent
    mutated_individual = [party.copy() for party in individual]

    #decide if mutation happens
    if random.random() < mutation_rate:
        #select and swap friends
        friend1 = random.choice(mutated_individual[0])
        friend2 = random.choice(mutated_individual[1])
        mutated_individual[0].remove(friend1)
        mutated_individual[1].remove(friend2)
        mutated_individual[0].append(friend2)
        mutated_individual[1].append(friend1)

    return mutated_individual
# generate a list of friends with alphabetic names that can be used with any sized matrix
def generate_friend_list(num_friends):
    alphabet = string.ascii_uppercase
    pFriends = []

    for i in range(num_friends):
        name = ""
        number = i

        while True:
            name = alphabet[number % 26] + name
            number = number // 26 -1 

            if number < 0:
                break
        pFriends.append(name)
    return pFriends

# function to randomly generate relationship matrix of different sizes for testing
def generate_relationship_matrix(num_friends):
    #generate friends list
    pFriends = generate_friend_list(num_friends)
    #create empty matrix
    pRelationships = np.zeros((num_friends,num_friends), dtype=int)

    #generate relationships
    for i in range(num_friends):
        for j in range(i + 1, num_friends):
            relationship = random.choice([-1,1])
            pRelationships[i][j] = relationship
            pRelationships[j][i] = relationship
    return pFriends, pRelationships

def main_GA(relationships, population_size, num_generations, mutation_rate, tournament_size, number_of_parties):
    num_friends = len(relationships)
    #create initial population
    population = create_population(population_size, num_friends, number_of_parties)

    #keep track of the best fitness scores in each generation
    fitness_history = []
    average_fitness_history = []

    for generation in range(num_generations):
        #find best individual in generation
        fitness_scores = [fitness_function(individual, relationships) for individual in population]
        best_score = max(fitness_scores)
        average_score = np.mean(fitness_scores)

        #best_individual = max(population, key=lambda individual: fitness_function(individual, relationships))
        #best_score = fitness_function(best_individual, relationships)

        # record best score
        fitness_history.append(best_score)
        average_fitness_history.append(average_score)
        best_individual = population[np.argmax(fitness_scores)]

        #start the next generation and preserve best individual
        new_popuation = [[party.copy() for party in best_individual]]
        #generate children until new population is full
        while len(new_popuation) < population_size:
            #select parents
            parent1 = tournament_selection(population, relationships, tournament_size)
            parent2 = tournament_selection(population, relationships, tournament_size)
            #produce child
            child = crossover(parent1, parent2)
            #mutation
            childm = mutation(child,mutation_rate)
            #add to new population
            new_popuation.append(childm)
        #replace old population
        population = new_popuation

    #find the best individual in the final population
    best_individual = max(population, key=lambda individual: fitness_function(individual, relationships))
    best_score = fitness_function(best_individual,relationships)
    return best_individual, best_score, fitness_history, average_fitness_history

# outer loop to number of friends each time to test how size of relationship matrix affects the GA's performance

if new_or_old:
    friend_sizes = [10, 20, 30, 40, 50]
    pop_sizes = [10, 20, 30, 40, 50]
else:
    friend_sizes = [len(friends)]
    pop_sizes = [2, 4, 6, 8, 10]

all_experiments = {}

# run the algorithm
for num_friends in friend_sizes:
    print(f"\n========= Testing {num_friends} friends =======")
    # calculate party size
    if new_or_old:
        #generate friends and matrix
        current_friends, current_relationships = generate_relationship_matrix(num_friends)
    else:
        current_friends = friends
        current_relationships = relationships
    for pop in pop_sizes:
        print(f"\n========== Testing Population Size {pop} ========")
        #set population size to test on each run
        if new_or_old:
            population_size = pop
        else:
            population_size = pop
        
        all_best_scores = []
        all_average_scores = []
        all_final_scores = []

        best_overall_score = float("-inf")
        best_overall_arrangement = None
        #run algorithm
        for run in range(num_runs):
            best_arrangement, best_score, fitness_history, average_fitness_history = main_GA(current_relationships, population_size, num_generations, mutation_rate, tournament_size, number_of_parties)
            all_best_scores.append(fitness_history)
            all_average_scores.append(average_fitness_history)
            all_final_scores.append(best_score)
            # keep track of best score and arrangement
            if best_score > best_overall_score:
                best_overall_score = best_score
                best_overall_arrangement = best_arrangement

        if num_friends not in all_experiments:
            all_experiments[num_friends] = {}
        # adding the experiment to storage
        all_experiments[num_friends][pop] = {
            "best_histories": all_best_scores,
            "average_histories": all_average_scores,
            "final_scores": all_final_scores,
            "best_arrangement": best_overall_arrangement,
            "best_score": best_overall_score
            }
        # print best arrangements and friends in party
        print(f"Best arrengement: {best_overall_arrangement}, \n Best fitness score {best_overall_score}")
        # assign names based on old or random matrix
        for i, party in enumerate(best_arrangement):
            party_names = [current_friends[friend] for friend in party]
            print(f"Party {i + 1}: {party_names}")

        # calculate stats for all runs
        print("Highest: ", max(all_final_scores))
        print("Lowest: ", min(all_final_scores))
        print("Mean: ", np.mean(all_final_scores))
        print("Standard deviation: ", np.std(all_final_scores))

        # plot progress of generations on graph
        # best score graph
        plt.figure(figsize=(10,6))
        for i, history in enumerate(all_experiments[num_friends][pop]["best_histories"]):
            plt.plot(history, label=f"Best Fitness: Run {i + 1}")
        plt.xlabel("Generation")
        plt.ylabel("Best Fitness score")
        plt.title(f"Genetic Algorithm - Best Fitness: {num_friends} Friends : {pop} Population")
        plt.legend()
        plt.grid()
        plt.savefig(f"best_fitness_{num_friends}_friends_{pop}_population.png")
        plt.show()

        # average score graph
        plt.figure(figsize=(10,6))
        for i, history in enumerate(all_experiments[num_friends][pop]["average_histories"]):
            plt.plot(history, linestyle="--", label=f"Average Fitness: Run {i + 1}")
        plt.xlabel("Generation")
        plt.ylabel("Average Fitness score")
        plt.title(f"Genetic Algorithm - Average Fitness: {num_friends} Friends : {pop} Population")
        plt.legend()
        plt.grid()
        plt.savefig(f"average_fitness_{num_friends}_friends_{pop}_population.png")
        plt.show()

# dataframe statistics and visualisation 
summary_data = []

for n in friend_sizes:
    for pop in pop_sizes:
        scores = all_experiments[n][pop]["final_scores"]
        # normalise fitness socres
        max_possible_fitness = 4 * math.comb(n // 2, 2)
        normalised_scores = [score / max_possible_fitness for score in scores]

        summary_data.append({
            "Number of Friends": n,
            "Population Size": pop,
            "Highest Fitness": max(scores),
            "Lowest Fitness": min(scores),
            "Mean Fitness": np.mean(scores),
            "Normalised Fitness": np.mean(normalised_scores),
            "Normalised Standard Deviation": np.std(normalised_scores),
            "Standard Deviation": np.std(scores)
        })

df = pd.DataFrame(summary_data)
print(df)
with open("GA_results.txt", "w") as file:
    file.write(df.to_string(index=False))

# graph to mean fitness against problem size
plt.figure(figsize=(10,6))
plt.plot(
    df["Number of Friends"],
    df["Mean Fitness"],
    marker="o",
    label="Mean Fitness"
)
plt.xlabel("Number of Friends")
plt.ylabel("Mean Final Fitness")
plt.title("Mean GA Fitness Against Problem Size")
plt.legend()
plt.grid()
plt.savefig("mean_fitness_vs_num_friends.png")
plt.show()

#graph to show standard deviation against problem size
plt.figure(figsize=(10,6))
plt.plot(
    df["Number of Friends"],
    df["Standard Deviation"],
    marker="o",
    label="Standard Deviation"
)
plt.xlabel("Number of Friends")
plt.ylabel("Standard Deviation")
plt.title("GA Result Variation Against Problem Size")
plt.legend()
plt.grid()
plt.savefig("std_vs_num_friends.png")
plt.show()

# END
################################
""""
parents = select_parents(create_population(population_size), relationships, num_parents=6, tournament_size=2)
for i, parent in enumerate(parents):
    score = fitness_function(parent, relationships)
    print(f"Parent {i}: {parent}, Fitness Score: {score}")

child = crossover(parents[0],parents[1])

print(f"Child {child}, Child Fitness, {fitness_function(child, relationships)}")


selected_individual = tournament_selection(create_population(population_size), relationships)
# evaluate the fitness of each individual in the population
for i, individual in enumerate(create_population(population_size)):
    score = fitness_function(individual, relationships)
    print(f"Individual {i}: {individual}, Fitness Score: {score}")
"""
