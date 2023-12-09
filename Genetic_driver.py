import EasyGA
import numpy as np
import random
import scenario_runner # temporary name for now
import statistics
import re

from G17_controller_genetic import G17Controller
        
class FuzzyGAController():
    """
    This is only supposed to implement Fuzzy Logic - Genetic Algorithm
    To improve the performance of the AI model created to beat the Asteroid game

    ...
    Methods
    ```````

    fitness:
        Evalautes the fuzzy controller with given chromosome on a test scenario.
        Evaluated based on a criteria.
    gen_chromosome:
        From Kendrick's code, literally just random...
    run:
        Run the genetic algorithm
    test:
        Test the genetic algorithm on the drivers.py
    """

    def fitness(self, chromosome):
        """
        This fitness function will create a Controller class instance and that will be tested by the Test class
        which has the test scenario defined and the Score collected will be used to define the fitness of the 
        Genetic Algorithm model.

        Scoring Criteria:
        Asteroids hit = max
        Accuracy = 100
        Death = 0
        Closest_Distance = average of all distances
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        actual_score (int) : Total fitness of the generated fuzzy GA controller model.
        """
        g17_controller = G17Controller(chromosome)

        test = scenario_runner.Test(g17_controller)
        score = test.get_score()
        ctrl = test.get_ctrl()

        ## Weighted fitness functions. Adjust the weights to specify how important the effect of that component is on our model
        # Penalty Weight
        death_weight = 75        
        penalty = (score.deaths * death_weight) 

        # Maximize asteroids hit and accuracy
        accuracy_weight = 100
        hit_weight = 2
        hit_score = (score.asteroids_hit * hit_weight)
        accuracy_score = (score.accuracy * accuracy_weight)

        # Minimize distance
        closest_distance_weight = 2 
        distance_score = (statistics.mean(ctrl.get_closest_distances()) * closest_distance_weight)

        # Fitness calculation
        actual_score = hit_score + accuracy_score - distance_score - penalty
                        
        print(f"Actual score: {actual_score}, Hit: {hit_score},Accuracy: {accuracy_score}, Distance: {distance_score}, Penalty: {penalty}")
        return actual_score

    def gen_chromosome(self):
        """
        
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        """
        variable_value = random.uniform(0, 1)
        return variable_value

    def export_chromosome(self):
        """
        Returns the best developed chromosome.
        """

        # Assuming self.best_chromosome.gene_value_list contains floats
        float_list = self.best_chromosome.gene_value_list

        # Convert float values to strings
        str_list = [str(value) for value in float_list]

        # Join the string values with a separator (e.g., ', ')
        result_string = ', '.join(str_list)

        print("Writing to file the best result")
        with open("train_chromosome.txt", "w") as file:
            file.write(result_string)
    

    def run(self):
        """
        Runs the Genetic Algorithm using easyGA
        """
        ga = EasyGA.GA()
        ga.gene_impl = self.gen_chromosome

        ga.chromosome_length = 47 # 47 genes as per membership functions
        ga.population_size = 5

        """
        The target fitness type is set to max because we are looking 
        For max accuracy and asteroid count, less a death and asteroid nearness
        """
        ga.target_fitness_type = "max"

        # Used to prepopulate 1st generation with more ideal parameters from past runs
        saved_approach = False
        if saved_approach:
            saved_chromsome = get_prime_chromosome("train_chromosome.txt")
            ga.population = ga.make_population([saved_chromsome])

        ga.generation_goal = 5
        ga.fitness_function_impl = self.fitness

        # Run through generations
        ga.evolve()

        # Save best chromosome
        ga.graph.highest_value_chromosome()
        ga.print_best_chromosome()

        self.best_chromosome = ga.population[0]

        self.export_chromosome()

        # Show fitness increase
        ga.graph.show()

def get_prime_chromosome(filename):
    with open(filename, 'r') as file:
        raw_chromosome = file.read()

    # Extract numbers using regular expression
    numbers = re.findall(r'\d+\.\d+', raw_chromosome)

    # Convert the list of strings to a list of floats
    float_list = [float(num) for num in numbers]

    print("This is the chromosome from the file:\n\t", (float_list), len(float_list))    
    return float_list

ctrl = FuzzyGAController()
ctrl.run()