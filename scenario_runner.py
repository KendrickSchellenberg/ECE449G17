import time
from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment

class Test():
    """
    Plan is that this class is mainly for testing the FuzzyGA model that we have 
    created with the chromosome parameters that we have randomly generated.
    This functions the same way as drivers.py but without the gui and this is mainly
    for simulating how our model will do and collect data and score from it.
    """
    __score = None 
    __ctrl = None
    asteroids_hit = 0
    deaths = 0
    accuracy = 0
    mean_eval_time = 0
    distance = 0
    time = 0

    # Has everything we would need
    score = 0

    def __init__(self, ctrl):
        # self.ctrl = ctrl # This is what we are going to test.
        self.__ctrl = ctrl
        self.test_scenario()
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
        
        game = KesslerGame(settings=game_settings) # Use this to visualize the game scenario
        #game = TrainerEnvironment(settings=game_settings) # Use this for max-speed, no-graphics simulation
        score, perf_data = game.run(scenario=my_test_scenario, controllers = [self.__ctrl])
        self.__score = score
        # print("This is the score", score)
        # print("Is there a score[0]?", score[0])
        # print("Is there a score.teams?", score.teams)
        # print("Is there a score.teams[0]?", score.teams[0])


        self.time = score.sim_time
        # self.accuracy = team.accuracy for team in score.teams
        self.accuracy = score.teams[0].accuracy
        self.deaths = score.teams[0].deaths
        self.mean_eval_time = score.teams[0].mean_eval_time
        self.asteroids_hit = score.teams[0].asteroids_hit
        return

    def get_ctrl(self):
        return self.__ctrl
    
    def get_score(self):
        return self.__score.teams[0]
    
    def print_graph(self):
        import matplotlib.pyplot as plt
        plt.hist(self.ctrl.get_closest_distances(), bins=20, edgecolor='black')
        plt.title('Distribution of Closest Asteroid Distances')
        plt.xlabel('Distance')
        plt.ylabel('Frequency')
        plt.show()