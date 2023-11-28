import time
from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment

class Test():
    ctrl = 0
    asteroids_hit = 0
    deaths = 0
    accuracy = 0
    mean_eval_time = 0
    distance = 0
    time = 0

    def __init__(self, ctrl):
        # self.ctrl = ctrl # This is what we are going to test.
        return

    def test_scenario(self):
        my_test_scenario = Scenario(name='Test Scenario',
                    num_asteroids=5,
                    ship_states=[
                    {'position': (400, 400), 'angle': 90, 'lives': 3, 'team': 1},
                    ],
                    map_size=(1000, 800),
                    time_limit=60,
                    ammo_limit_multiplier=0,
                    stop_if_no_ammo=False)
        
        game_settings = {'perf_tracker': True,
                'graphics_type': GraphicsType.Tkinter,
                'realtime_multiplier': 1,
                'graphics_obj': None}
        
        game = TrainerEnvironment(settings=game_settings) # Use this for max-speed, no-graphics simulation
        score, perf_data = game.run(scenario=my_test_scenario, controllers = [self.ctrl])
        self.time = score.sim_time
        # self.accuracy = team.accuracy for team in score.teams
        self.accuracy = score.teams.accuracy
        self.deaths = score.teams.deaths
        self.mean_eval_time = score.teams.mean_eval_time
        self.asteroids_hit = score.teams.asteroids_hit
        return
