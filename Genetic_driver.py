import EasyGA
import numpy as np
import random
import scenario_runner # temporary name for now
import statistics

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
        accuracy_weight = 10

        # Penalty Weights
        death_weight = 50
        completion_speed_weight = 1/2
        
        # 450 is I think the max distance?
        desired_score = 100 * accuracy_weight + 450 * closest_distance_weight
        
        penalty = (score.deaths * death_weight) + (score.mean_eval_time * completion_speed_weight)

        accuracy_score = (score.accuracy * accuracy_weight)
        distance_score = (statistics.mean(ctrl.get_closest_distances()) * closest_distance_weight)

        actual_score = accuracy_score + distance_score - penalty
                        
        error = abs(desired_score - actual_score)
        print(f"Actual score: {actual_score}, Accuracy: {accuracy_score}, Distance: {distance_score}, Penalty: {penalty}")
        print(f"Error: {error}, Desired score: {desired_score}")
        return error

    def gen_chromosome(self):
        """
        
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        """
        variable_value = random.uniform(0, 1)
        # print("\tThis is the value that is generated", variable_value)
        return variable_value

    def export_chromosome(self, ga):
        """
        Returns the best developed chromosome.
        """
        with open("best_chromosome.txt", "w") as file:
            file.write(str(ga.population[0]))
        return self.best_chromosome
    
    def open_run(self, filename = "best_chromosome.txt"):
        import re
        # ga = EasyGA()
        from EasyGA.structure import Chromosome as ga
        with open(filename, 'r') as file:
            chromosome = file.read()
            # print(type(chromosome))
        # Extract numbers using regular expression
        numbers = re.findall(r'\d+\.\d+', chromosome)

        # Convert the list of strings to a list of floats
        float_list = [float(num) for num in numbers]
        print(float_list)
        print("This is the chromosome from the file:\n\t", ga(float_list), len(float_list))
        chromosome = float_list
        g17_controller = G17Controller(float_list)
        
        test = scenario_runner.Test(g17_controller)
        score = test.get_score()
        ctrl = test.get_ctrl()

        # We are going to do weighted fitness functions. We can adjust the weights to specify how important a that affect of that 
        # component is on our model
        closest_distance_weight = 2 
        accuracy_weight = 10

        # Penalty Weights
        death_weight = 50
        completion_speed_weight = 1/2
        
        # 450 is I think the max distance?
        desired_score = 100 * accuracy_weight + 450 * closest_distance_weight
        
        penalty = (score.deaths * death_weight) + (score.mean_eval_time * completion_speed_weight)

        accuracy_score = (score.accuracy * accuracy_weight)
        distance_score = (statistics.mean(ctrl.get_closest_distances()) * closest_distance_weight)

        actual_score = accuracy_score + distance_score - penalty
                        
        error = abs(desired_score - actual_score)
        print(f"Actual score: {actual_score}, Accuracy: {accuracy_score}, Distance: {distance_score}, Penalty: {penalty}")
        print(f"Error: {error}, Desired score: {desired_score}")

        # self.fitness(ga(float_list))

    def run(self):
        """
        Runs the Genetic Algorithm using easyGA
        """
        ga = EasyGA.GA()
        ga.gene_impl = self.gen_chromosome
        # ga.chromosome_impl = self.gen_chromosome
        ga.chromosome_length = 47 # Will vary depending on how important the length is.
        ga.population_size = 1

        ### The target fitness type will have to vary because we are looking 
        ## For max accuracy, distance from nearest asteroid
        ## Min death, distance moveed.
        ga.target_fitness_type = "min"
        ### ------

        ga.generation_goal = 2
        ga.fitness_function_impl = self.fitness
        ga.evolve()
        ga.print_best_chromosome()
        self.best_chromosome = ga.population[0]
        self.export_chromosome(ga)

ctrl = FuzzyGAController()
ctrl.run()