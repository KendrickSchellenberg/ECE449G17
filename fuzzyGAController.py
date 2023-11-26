from G17_controller import G17Controller

class FuzzyGAController(G17Controller):
    """
    
    """
    def make_fuzzy_controller(self, chromosome):
        pass

    def fitness(self, chromosome):
        pass

    # We are going to test on scenario
    def execute_fuzzy_inference(self, thrust_sim, fire_sim):
        pass

    def gen_chromosome(self):
        pass

    def run(self):
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
