import EasyGA
import numpy as np
import random
import scenario_runner # temporary name for now
import statistics
import re

from G17_controller import G17Controller
        
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
        which has the test scenario defined and the Score collected will be used to define the error of the 
        Genetic Algorithm model.

        Scoring Criteria:
        Accuracy = 100
        Death = 0
        Closest_Distance = square function?
        Speed_of_completion = we could use like a square root function? - min
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        error (int) : Total error of the geenrated fuzzy GA controller model.
        """
        error = 0
        # target_control, ship_control = self.setup_fuzzy_system(chromosome) # Could just also be done by Controller_Maker
        g17_controller = G17Controller(chromosome)

        test = scenario_runner.Test(g17_controller)
        score = test.get_score()
        ctrl = test.get_ctrl()

        # We are going to do weighted fitness functions. We can adjust the weights to specify how important a that affect of that 
        # component is on our model
        closest_distance_weight = 2 
        accuracy_weight = 200

        # Penalty Weight
        death_weight = 50        
        penalty = (score.deaths * death_weight) 

        # Maximize accuracy
        accuracy_score = (score.accuracy * accuracy_weight)

        # Minimize distance
        distance_score = (statistics.mean(ctrl.get_closest_distances()) * closest_distance_weight)

        actual_score = accuracy_score - distance_score - penalty
                        
        print(f"Actual score: {actual_score}, Accuracy: {accuracy_score}, Distance: {distance_score}, Penalty: {penalty}")
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
        with open("best_chromosome.txt", "w") as file:
            file.write(result_string)
    

    def run(self):
        """
        Runs the Genetic Algorithm using easyGA
        """
        ga = EasyGA.GA()
        ga.gene_impl = self.gen_chromosome

        ga.chromosome_length = 47 # Will vary depending on how important the length is.
        ga.population_size = 2

        ### The target fitness type will have to vary because we are looking 
        ## For max accuracy, distance from nearest asteroid
        ## Min death, distance moveed.
        ga.target_fitness_type = "max"
        ### ------
        saved_chromsome = get_prime_chromosome("prime.txt")
        print(saved_chromsome)
        ga.make_population(saved_chromsome)

        ga.generation_goal = 400

        ga.fitness_function_impl = self.fitness
        ga.evolve()

        ga.graph.highest_value_chromosome()

        ga.print_best_chromosome()

        self.best_chromosome = ga.population[0]

        self.export_chromosome()
        # Now what do i do with the best chromosome?
        #### Reference Kendrick's Lab on Test Dataset Evaluation

def get_prime_chromosome(filename):

    with open(filename, 'r') as file:
        raw_chromosome = file.read()
        # chromosome = chromosome.astype(float)
        # print(type(chromosome))
    # Extract numbers using regular expression
    numbers = re.findall(r'\d+\.\d+', raw_chromosome)

    # Convert the list of strings to a list of floats
    float_list = [float(num) for num in numbers]
    print(float_list)
    print("This is the chromosome from the file:\n\t", (float_list), len(float_list))

    return float_list

ctrl = FuzzyGAController()
ctrl.run()