from G17_controller import G17Controller

class FuzzyGAController(G17Controller):
    """
    Child of G17Controller. This is only supposed to implement Fuzzy Logic - Genetic Algorithm
    To improve the performance of the AI model created to beat the Asteroid game

    ...
    Methods
    ```````
    make_fuzzy_controller:
        creates a fuzzy controller with generated chromosome
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
    
    def make_fuzzy_controller(self, chromosome):
        """

        Parameters
        ``````````
        chromosome (Gene) : 

        
        Returns
        ```````
        """
        pass

    def fitness(self, chromosome):
        """
        
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        """
        pass

    # We are going to test on scenario
    def execute_fuzzy_inference(self, thrust_sim, fire_sim):
        """
        
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        """
        pass

    def gen_chromosome(self):
        """
        
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        """
        
        pass

    def run(self):
        """
        
        Parameters
        ``````````
        chromosome (Gene) : 

        Returns
        ```````
        """
        ga = EasyGA.GA()
        # ga.gene_impl = self 
        ga.chromosome_impl = self.gen_chromosome
        ga.chromosome_length = 6 # Will vary depending on how important the length is.
        ga.population_size = 100

        ### The target fitness type will have to vary because we are looking 
        ## For max accuracy, distance from nearest asteroid
        ## Min death, distance moveed.
        ga.target_fitness_type = "min"
        ### ------

        ga.generation_goal = 20
        ga.fitness_function_impl = self.fitness
        ga.evolve()
        ga.print_best_chromosome()
        # Now what do i do with the best chromosome?
        #### Reference Kendrick's Lab on Test Dataset Evaluation