# ECE 449 Group 17

Our submission is broken into three parts

1. Genetic implementation training

This is intended to show our completion of deliverable 2: "Agent optimizes a genetic fuzzy tree".
It requires three files
* Genetic_driver.py
* G17_controller_genetic.py
* scenario_runner.py

Running Genetic_driver.py will begin a fresh optimization with both a population and generation of 5. The best chromosome will be saved to best_chromosome.txt, but it is outputted to terminal as well in addition to a graph showing fitness over time being be shown.


We ran this optimization over populations of 20 for thousands of generations. The best chromosomes were fed back into the optimizer by setting the hard-coded "saved_approach = False" to True, and by setting the hard-coded file path "saved_chromsome = get_prime_chromosome("prime10.txt")" as well.


---
2. Genetic implementation testing

To ensure that you could see the resulting best genetically-trained chromosome, the G17_controller_genetic_best.py and prime.txt files are necessary. The controller can be run in a driver.py framework like the one provided by you, as it fetches and utilizes the chromosome from a hard-coded file path. It is imported and run like your controller


from scott_dick_controller import ScottDickController


from G17_controller_genetic_best import G17Controller

g17_controller = G17Controller()
score, perf_data = game.run(scenario=g17_test_scenario, controllers = [g17_controller])


---
3. Fuzzy logic approach

If for whatever reason the above files fail to run, we've attached our non-genetic fuzzy controller implementation as a backup. It is a standalone file, G17_controller_nongenetic.py, and can be imported and run


from G17_controller_genetic_nongenetic import G17Controller

g17_controller = G17Controller()
score, perf_data = game.run(scenario=g17_test_scenario, controllers = [g17_controller])






