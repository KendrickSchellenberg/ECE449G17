# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.
import time

from kesslergame import Scenario, KesslerGame, GraphicsType
from G17_controller_genetic_best import G17Controller
# from G17_controller_nongenetic import G17Controller

g17_test_scenario = Scenario(name='G17 Scenario',
                    num_asteroids=5,
                    ship_states=[
                    {'position': (400, 400), 'angle': 90, 'lives': 3, 'team': 1}
                    ],
                    map_size=(1000, 800),
                    time_limit=60,
                    ammo_limit_multiplier=0,
                    stop_if_no_ammo=False
)

game_settings = {'perf_tracker': True,
                'graphics_type': GraphicsType.Tkinter,
                'realtime_multiplier': 1,
                'graphics_obj': None}

game = KesslerGame(settings=game_settings) # Use this to visualize the game scenario
# game = TrainerEnvironment(settings=game_settings) # Use this for max-speed, no-graphics simulation
pre = time.perf_counter()

g17_controller = G17Controller()
score, perf_data = game.run(scenario=g17_test_scenario, controllers = [g17_controller])

print('Scenario eval time: '+str(time.perf_counter()-pre))
print(score.stop_reason)
print('Asteroids hit: ' + str([team.asteroids_hit for team in score.teams]))
print('Deaths: ' + str([team.deaths for team in score.teams]))
print('Accuracy: ' + str([team.accuracy for team in score.teams]))
print('Mean eval time: ' + str([team.mean_eval_time for team in score.teams]))
print('Evaluated frames: ' + str([controller.eval_frames for controller in score.final_controllers]))

# Display the distribution of closest distances for fuzzy logic hard-coded optimization purposes
# import matplotlib.pyplot as plt
# plt.hist(g17_controller.get_closest_distances(), bins=20, edgecolor='black')
# plt.title('Distribution of Closest Asteroid Distances')
# plt.xlabel('Distance')
# plt.ylabel('Frequency')
# plt.show()