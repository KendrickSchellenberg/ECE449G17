# Schellenberg Kendrick Mathias
# Nasreddine Adib Marwan
# Datuin Raymart Cabural


# Demonstration of a fuzzy tree-based controller for Kessler Game.
# Please see the Kessler Game Development Guide by Dr. Scott Dick for a
#   detailed discussion of this source code.

from kesslergame import KesslerController # In Eclipse, the name of the library is kesslergame, not src.kesslergame
from typing import Dict, Tuple, List
from cmath import sqrt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import math
import numpy as np
import matplotlib as plt
import re

class G17Controller(KesslerController):
    def scale_min_max(self, min, max, rng):
        cv = self.chromosome
        sublist = cv[rng[0] : rng[1]]

        # Sorted in ascending order
        sublist = sorted(sublist)
        index = 0
        for i in range(rng[0], rng[1]):
            self.chromosome[i] = sublist[index]
            index += 1
        
        index = 0
        for val in sublist:
            sublist[index] = val*(max-min) + min
            index += 1
        return sublist

    def __init__(self, filename = "prime10.txt"):
        self.eval_frames = 0 #What is this?

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
        chromosome = float_list

        self.chromosome = chromosome

        self.closest_distances = []
        self.ship_approaching_list = []

        # bullet_time_bounds = [0, 1.0] # preferably would do [0, 0.1]
        bullet_time_bounds = [0, 0.1] 
        theta_delta_fire_bounds_large = [-1*math.pi, math.pi]
        theta_delta_fire_bounds_small = [-1*math.pi/3, math.pi/3]
        theta_delta_fire_bounds_smaller = [-1*math.pi/6, math.pi/6]
        ship_turn_bounds = [-180,180]
        ship_turn_bounds_small = [-90,90]

        bullet_time_vals = self.scale_min_max(bullet_time_bounds[0], bullet_time_bounds[1], [0, 5])
        delta_fire_vals = self.scale_min_max(theta_delta_fire_bounds_small[0], theta_delta_fire_bounds_small[1], [5, 10])
        delta_fire_small_vals = self.scale_min_max(theta_delta_fire_bounds_smaller[0], theta_delta_fire_bounds_smaller[1], [10, 13])
        ship_turn_vals = self.scale_min_max(ship_turn_bounds[0], ship_turn_bounds[1], [13, 18])
        ship_turn_small_vals = self.scale_min_max(ship_turn_bounds_small[0], ship_turn_bounds_small[1], [18, 21])

        # self.targeting_control is the targeting rulebase, which is static in this controller.      
        # Declare variables
        bullet_time = ctrl.Antecedent(np.arange(0,1.0,0.002), 'bullet_time')
        theta_delta_fire = ctrl.Antecedent(np.arange(-1*math.pi, math.pi, 0.1), 'theta_delta_fire') # Radians due to Python
        ship_turn = ctrl.Consequent(np.arange(-180,180,1), 'ship_turn') # Degrees due to Kessler
        ship_fire = ctrl.Consequent(np.arange(-1,1,0.1), 'ship_fire') 

        bullet_time['S'] = fuzz.trimf(bullet_time.universe, [0, bullet_time_vals[0], bullet_time_vals[1]])
        bullet_time['M'] = fuzz.trimf(bullet_time.universe, [bullet_time_vals[1],bullet_time_vals[2],bullet_time_vals[3]])
        bullet_time['L'] = fuzz.trimf(bullet_time.universe, [bullet_time_vals[3], bullet_time_vals[4], 1.0])
        
        #Declare fuzzy sets for theta_delta (degrees of turn needed to reach the calculated firing angle)
        # [-1*math.pi, math.pi]
        theta_delta_fire['NL'] = fuzz.zmf(theta_delta_fire.universe, delta_fire_vals[0], delta_fire_vals[1])
        theta_delta_fire['NS'] = fuzz.trimf(theta_delta_fire.universe, [-1*math.pi/3, delta_fire_small_vals[0], delta_fire_small_vals[1]])
        theta_delta_fire['Z'] = fuzz.trimf(theta_delta_fire.universe, [delta_fire_vals[1], delta_fire_vals[2], delta_fire_vals[3]])
        theta_delta_fire['PS'] = fuzz.trimf(theta_delta_fire.universe, [delta_fire_small_vals[1], delta_fire_small_vals[2], math.pi/3])
        theta_delta_fire['PL'] = fuzz.smf(theta_delta_fire.universe, delta_fire_vals[3], delta_fire_vals[4])

        #Declare fuzzy sets for the ship_turn consequent; this will be returned as turn_rate.
        # [-180,180] 
        ship_turn['NL'] = fuzz.trimf(ship_turn.universe, [-180, ship_turn_vals[0], ship_turn_vals[1]])
        ship_turn['NS'] = fuzz.trimf(ship_turn.universe, [-90, ship_turn_small_vals[0], ship_turn_small_vals[1]])
        ship_turn['Z'] = fuzz.trimf(ship_turn.universe, [ship_turn_vals[1], ship_turn_vals[2], ship_turn_vals[3]])
        ship_turn['PS'] = fuzz.trimf(ship_turn.universe, [ship_turn_small_vals[1], ship_turn_small_vals[2], 90])
        ship_turn['PL'] = fuzz.trimf(ship_turn.universe, [ship_turn_vals[3], ship_turn_vals[4], 180])
        
        #Declare singleton fuzzy sets for the ship_fire consequent; -1 -> don't fire, +1 -> fire; this will be  thresholded
        #   and returned as the boolean 'fire'
        ship_fire['N'] = fuzz.trimf(ship_fire.universe, [-1,-1,0.0])
        ship_fire['Y'] = fuzz.trimf(ship_fire.universe, [0.0,1,1])         
                
        #Declare each fuzzy rule
        rule1 = ctrl.Rule(bullet_time['L'] & theta_delta_fire['NL'], (ship_turn['NL'], ship_fire['N']))
        rule2 = ctrl.Rule(bullet_time['L'] & theta_delta_fire['NS'], (ship_turn['NS'], ship_fire['N']))
        rule3 = ctrl.Rule(bullet_time['L'] & theta_delta_fire['Z'], (ship_turn['Z'], ship_fire['Y']))
        rule4 = ctrl.Rule(bullet_time['L'] & theta_delta_fire['PS'], (ship_turn['PS'], ship_fire['N']))
        rule5 = ctrl.Rule(bullet_time['L'] & theta_delta_fire['PL'], (ship_turn['PL'], ship_fire['N']))

        rule6 = ctrl.Rule(bullet_time['M'] & theta_delta_fire['NL'], (ship_turn['NL'], ship_fire['N']))
        rule7 = ctrl.Rule(bullet_time['M'] & theta_delta_fire['NS'], (ship_turn['NS'], ship_fire['Y']))
        rule8 = ctrl.Rule(bullet_time['M'] & theta_delta_fire['Z'], (ship_turn['Z'], ship_fire['Y']))    
        rule9 = ctrl.Rule(bullet_time['M'] & theta_delta_fire['PS'], (ship_turn['PS'], ship_fire['Y']))
        rule10 = ctrl.Rule(bullet_time['M'] & theta_delta_fire['PL'], (ship_turn['PL'], ship_fire['N']))

        rule11 = ctrl.Rule(bullet_time['S'] & theta_delta_fire['NL'], (ship_turn['NL'], ship_fire['Y']))
        rule12 = ctrl.Rule(bullet_time['S'] & theta_delta_fire['NS'], (ship_turn['NS'], ship_fire['Y']))
        rule13 = ctrl.Rule(bullet_time['S'] & theta_delta_fire['Z'], (ship_turn['Z'], ship_fire['Y']))
        rule14 = ctrl.Rule(bullet_time['S'] & theta_delta_fire['PS'], (ship_turn['PS'], ship_fire['Y']))
        rule15 = ctrl.Rule(bullet_time['S'] & theta_delta_fire['PL'], (ship_turn['PL'], ship_fire['Y']))
     
        #DEBUG
        # bullet_time.view()
        # theta_delta_fire.view()
        # ship_turn.view()
        # ship_fire.view()
     
     
        
        # Declare the fuzzy controller, add the rules 
        # This is an instance variable, and thus available for other methods in the same object. See notes.                         
        # self.targeting_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15])
             
        self.targeting_control = ctrl.ControlSystem()
        self.targeting_control.addrule(rule1)
        self.targeting_control.addrule(rule2)
        self.targeting_control.addrule(rule3)
        self.targeting_control.addrule(rule4)
        self.targeting_control.addrule(rule5)
        self.targeting_control.addrule(rule6)
        self.targeting_control.addrule(rule7)
        self.targeting_control.addrule(rule8)
        self.targeting_control.addrule(rule9)
        self.targeting_control.addrule(rule10)
        self.targeting_control.addrule(rule11)
        self.targeting_control.addrule(rule12)
        self.targeting_control.addrule(rule13)
        self.targeting_control.addrule(rule14)
        self.targeting_control.addrule(rule15)

        #################################################################
        # self.thrust_range = (-480.0, 480.0)  # m/s^2
        # self.max_speed = 240  # Meters per second
        # Map size of 1000, so small from 0-200, medium from 200-400, large > 400
        # Declare fuzzy sets for the ship_thrust consequent; this will be returned

        
        # Declare variables
        closest_asteroid_distance = ctrl.Antecedent(np.arange(0, 1000, 1), 'closest_asteroid_distance')
        ship_speed = ctrl.Antecedent(np.arange(0, 240, 1), 'ship_speed')
        theta_delta_turn = ctrl.Antecedent(np.arange(-1*math.pi, math.pi, 0.1), 'theta_delta_turn')
        ship_thrust = ctrl.Consequent(np.arange(-480, 480, 1), 'ship_thrust')

        # distance        
        closest_asteroid_values = self.scale_min_max(0, 1000, (21,26))
        closest_asteroid_distance['S'] = fuzz.trimf(closest_asteroid_distance.universe,[0,closest_asteroid_values[0],closest_asteroid_values[1]])
        closest_asteroid_distance['M'] = fuzz.trimf(closest_asteroid_distance.universe, [closest_asteroid_values[1],closest_asteroid_values[2],closest_asteroid_values[3]])
        closest_asteroid_distance['L'] = fuzz.smf(closest_asteroid_distance.universe, closest_asteroid_values[3],closest_asteroid_values[4])

        # speed
        ship_speed_values =self.scale_min_max(0, 240, (26,31))
        ship_speed['S'] = fuzz.zmf(ship_speed.universe, ship_speed_values[0], ship_speed_values[1])
        ship_speed['M'] = fuzz.trimf(ship_speed.universe, [ship_speed_values[1],ship_speed_values[2],ship_speed_values[3]])
        ship_speed['L'] = fuzz.smf(ship_speed.universe, ship_speed_values[3], ship_speed_values[4])

        #Declare fuzzy sets for theta_delta (degrees of turn needed to reach the calculated firing angle)
        turn_values =self.scale_min_max(-1*math.pi/3, math.pi/3, (31, 36))
        turn_values_big = self.scale_min_max(-1*math.pi/6, math.pi/6, (36, 39))

        theta_delta_turn['NL'] = fuzz.zmf(theta_delta_turn.universe, turn_values[0], turn_values[1])
        theta_delta_turn['NS'] = fuzz.trimf(theta_delta_turn.universe, [-1*math.pi/6, turn_values_big[0], turn_values_big[1]])
        theta_delta_turn['Z'] = fuzz.trimf(theta_delta_turn.universe, [turn_values[1], turn_values[2], turn_values[3]])
        theta_delta_turn['PS'] = fuzz.trimf(theta_delta_turn.universe, [turn_values_big[1], turn_values_big[2], math.pi/6])
        theta_delta_turn['PL'] = fuzz.smf(theta_delta_turn.universe, turn_values[3], turn_values[4])
        
        # Declare fuzzy sets for the ship_thrust consequent; this will be returned as ship_thrust.
        ship_thrust_values = self.scale_min_max(-150, 150, (39,44))
        ship_thrust_values_small = self.scale_min_max(-480, 480, (44,47))

        # ship_thrust['NL'] = fuzz.zmf(ship_thrust.universe, ship_thrust_values[0], ship_thrust_values[1])
        ship_thrust['NL'] = fuzz.trimf(ship_thrust.universe, [-480,ship_thrust_values[0],ship_thrust_values[1]])
        ship_thrust['NS'] = fuzz.trimf(ship_thrust.universe, [-480,ship_thrust_values_small[0],ship_thrust_values_small[1]])
        ship_thrust['Z'] = fuzz.trimf(ship_thrust.universe, [ship_thrust_values[1],ship_thrust_values[2],ship_thrust_values[3]])
        ship_thrust['PS'] = fuzz.trimf(ship_thrust.universe, [ship_thrust_values_small[1],ship_thrust_values_small[2], 480])
        ship_thrust['PL'] = fuzz.trimf(ship_thrust.universe, [ship_thrust_values[3],ship_thrust_values[4],480])

        #Declare each fuzzy rule
        rule16 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['L'] & theta_delta_turn['NL'], (ship_thrust['Z']))
        rule17 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['L'] & theta_delta_turn['NS'], (ship_thrust['Z']))
        rule18 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['L'] & theta_delta_turn['Z'], (ship_thrust['Z']))
        rule19 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['L'] & theta_delta_turn['PS'], (ship_thrust['Z']))
        rule20 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['L'] & theta_delta_turn['PL'], (ship_thrust['Z']))
        
        rule21 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['M'] & theta_delta_turn['NL'], (ship_thrust['Z']))
        rule22 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['M'] & theta_delta_turn['NS'], (ship_thrust['PS']))
        rule23 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['M'] & theta_delta_turn['Z'], (ship_thrust['PS']))
        rule24 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['M'] & theta_delta_turn['PS'], (ship_thrust['PS']))
        rule25 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['M'] & theta_delta_turn['PL'], (ship_thrust['Z']))

        rule26 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['S'] & theta_delta_turn['NL'], (ship_thrust['PS']))
        rule27 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['S'] & theta_delta_turn['NS'], (ship_thrust['PS']))
        rule28 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['S'] & theta_delta_turn['Z'], (ship_thrust['PL']))
        rule29 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['S'] & theta_delta_turn['PS'], (ship_thrust['PS']))
        rule30 = ctrl.Rule(closest_asteroid_distance['L'] & ship_speed['S'] & theta_delta_turn['PL'], (ship_thrust['PS']))

        rule31 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['L'] & theta_delta_turn['NL'], (ship_thrust['PS']))
        rule32 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['L'] & theta_delta_turn['NS'], (ship_thrust['PS']))
        rule33 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['L'] & theta_delta_turn['Z'], (ship_thrust['PS']))
        rule34 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['L'] & theta_delta_turn['PS'], (ship_thrust['PS']))
        rule35 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['L'] & theta_delta_turn['PL'], (ship_thrust['PS']))
        
        rule36 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['M'] & theta_delta_turn['NL'], (ship_thrust['PS']))
        rule37 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['M'] & theta_delta_turn['NS'], (ship_thrust['PS']))
        rule38 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['M'] & theta_delta_turn['Z'], (ship_thrust['PL']))
        rule39 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['M'] & theta_delta_turn['PS'], (ship_thrust['PS']))
        rule40 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['M'] & theta_delta_turn['PL'], (ship_thrust['PS']))

        rule41 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['S'] & theta_delta_turn['NL'], (ship_thrust['PS']))
        rule42 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['S'] & theta_delta_turn['NS'], (ship_thrust['PS']))
        rule43 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['S'] & theta_delta_turn['Z'], (ship_thrust['PL']))
        rule44 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['S'] & theta_delta_turn['PS'], (ship_thrust['PS']))
        rule45 = ctrl.Rule(closest_asteroid_distance['M'] & ship_speed['S'] & theta_delta_turn['PL'], (ship_thrust['PS']))

        rule46 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['L'] & theta_delta_turn['NL'], (ship_thrust['NS']))
        rule47 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['L'] & theta_delta_turn['NS'], (ship_thrust['NS']))
        rule48 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['L'] & theta_delta_turn['Z'], (ship_thrust['NL']))
        rule49 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['L'] & theta_delta_turn['PS'], (ship_thrust['NS']))
        rule50 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['L'] & theta_delta_turn['PL'], (ship_thrust['NS']))
        
        rule51 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['M'] & theta_delta_turn['NL'], (ship_thrust['NS']))
        rule52 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['M'] & theta_delta_turn['NS'], (ship_thrust['NS']))
        rule53 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['M'] & theta_delta_turn['Z'], (ship_thrust['NS']))
        rule54 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['M'] & theta_delta_turn['PS'], (ship_thrust['NS']))
        rule55 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['M'] & theta_delta_turn['PL'], (ship_thrust['NS']))

        rule56 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['S'] & theta_delta_turn['NL'], (ship_thrust['NS']))
        rule57 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['S'] & theta_delta_turn['NS'], (ship_thrust['NL']))
        rule58 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['S'] & theta_delta_turn['Z'], (ship_thrust['NL']))
        rule59 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['S'] & theta_delta_turn['PS'], (ship_thrust['NL']))
        rule60 = ctrl.Rule(closest_asteroid_distance['S'] & ship_speed['S'] & theta_delta_turn['PL'], (ship_thrust['NS']))
        

        # Declare the fuzzy controller, add the rules 
        # This is an instance variable, and thus available for other methods in the same object. See notes.           
        self.ship_control = ctrl.ControlSystem()
        self.ship_control.addrule(rule16)
        self.ship_control.addrule(rule17)
        self.ship_control.addrule(rule18)
        self.ship_control.addrule(rule19)
        self.ship_control.addrule(rule20)
        self.ship_control.addrule(rule21)
        self.ship_control.addrule(rule22)
        self.ship_control.addrule(rule23)
        self.ship_control.addrule(rule24)
        self.ship_control.addrule(rule25)
        self.ship_control.addrule(rule26)
        self.ship_control.addrule(rule27)
        self.ship_control.addrule(rule28)
        self.ship_control.addrule(rule29)
        self.ship_control.addrule(rule30)
        self.ship_control.addrule(rule31)
        self.ship_control.addrule(rule32)
        self.ship_control.addrule(rule33)
        self.ship_control.addrule(rule34)
        self.ship_control.addrule(rule35)
        self.ship_control.addrule(rule36)
        self.ship_control.addrule(rule37)
        self.ship_control.addrule(rule38)
        self.ship_control.addrule(rule39)
        self.ship_control.addrule(rule40)
        self.ship_control.addrule(rule41)
        self.ship_control.addrule(rule42)
        self.ship_control.addrule(rule43)
        self.ship_control.addrule(rule44)
        self.ship_control.addrule(rule45)
        self.ship_control.addrule(rule46)
        self.ship_control.addrule(rule47)
        self.ship_control.addrule(rule48)
        self.ship_control.addrule(rule49)
        self.ship_control.addrule(rule50)
        self.ship_control.addrule(rule51)
        self.ship_control.addrule(rule52)
        self.ship_control.addrule(rule53)
        self.ship_control.addrule(rule54)
        self.ship_control.addrule(rule55)
        self.ship_control.addrule(rule56)
        self.ship_control.addrule(rule57)
        self.ship_control.addrule(rule58)
        self.ship_control.addrule(rule59)
        self.ship_control.addrule(rule60)

        # closest_asteroid_distance.view()
        # ship_speed.view()
        # theta_delta_turn.view()
        # ship_thrust.view()


    def actions(self, ship_state: Dict, game_state: Dict) -> Tuple[float, float, bool]:
        """
        Method processed each time step by this controller.
        """
        # These were the constant actions in the basic demo, just spinning and shooting.
        #thrust = 0 <- How do the values scale with asteroid velocity vector?
        #turn_rate = 90 <- How do the values scale with asteroid velocity vector?
        
        # Answers: Asteroid position and velocity are split into their x,y components in a 2-element ?array each.
        # So are the ship position and velocity, and bullet position and velocity. 
        # Units appear to be meters relative to origin (where?), m/sec, m/sec^2 for thrust.
        # Everything happens in a time increment: delta_time, which appears to be 1/30 sec; this is hardcoded in many places.
        # So, position is updated by multiplying velocity by delta_time, and adding that to position.
        # Ship velocity is updated by multiplying thrust by delta time.
        # Ship position for this time increment is updated after the the thrust was applied.
        

        # My demonstration controller does not move the ship, only rotates it to shoot the nearest asteroid.
        # Goal: demonstrate processing of game state, fuzzy controller, intercept computation 
        # Intercept-point calculation derived from the Law of Cosines, see notes for details and citation.

        # Find the closest asteroid (disregards asteroid velocity)
        ship_pos_x = ship_state["position"][0]     # See src/kesslergame/ship.py in the KesslerGame Github
        ship_pos_y = ship_state["position"][1]       
        closest_asteroid = None
        
        for a in game_state["asteroids"]:
            #Loop through all asteroids, find minimum Eudlidean distance
            curr_dist = math.sqrt((ship_pos_x - a["position"][0])**2 + (ship_pos_y - a["position"][1])**2)
            if closest_asteroid is None :
                # Does not yet exist, so initialize first asteroid as the minimum. Ugh, how to do?
                closest_asteroid = dict(aster = a, dist = curr_dist)
                
            else:    
                # closest_asteroid exists, and is thus initialized. 
                if closest_asteroid["dist"] > curr_dist:
                    # New minimum found
                    closest_asteroid["aster"] = a
                    closest_asteroid["dist"] = curr_dist

        # closest_asteroid is now the nearest asteroid object. 
        # Calculate intercept time given ship & asteroid position, asteroid velocity vector, bullet speed (not direction).
        # Based on Law of Cosines calculation, see notes.
        
        # Side D of the triangle is given by closest_asteroid.dist. Need to get the asteroid-ship direction
        #    and the angle of the asteroid's current movement.
        # REMEMBER TRIG FUNCTIONS ARE ALL IN RADAINS!!!
        
        
        asteroid_ship_x = ship_pos_x - closest_asteroid["aster"]["position"][0]
        asteroid_ship_y = ship_pos_y - closest_asteroid["aster"]["position"][1]
        
        asteroid_ship_theta = math.atan2(asteroid_ship_y,asteroid_ship_x)
        
        asteroid_direction = math.atan2(closest_asteroid["aster"]["velocity"][1], closest_asteroid["aster"]["velocity"][0]) # Velocity is a 2-element array [vx,vy].
        my_theta2 = asteroid_ship_theta - asteroid_direction
        cos_my_theta2 = math.cos(my_theta2)
        # Need the speeds of the asteroid and bullet. speed * time is distance to the intercept point
        asteroid_vel = math.sqrt(closest_asteroid["aster"]["velocity"][0]**2 + closest_asteroid["aster"]["velocity"][1]**2)
        bullet_speed = 800 # Hard-coded bullet speed from bullet.py
        
        # Determinant of the quadratic formula b^2-4ac
        targ_det = (-2 * closest_asteroid["dist"] * asteroid_vel * cos_my_theta2)**2 - (4*(asteroid_vel**2 - bullet_speed**2) * closest_asteroid["dist"])
        
        # Combine the Law of Cosines with the quadratic formula for solve for intercept time. Remember, there are two values produced.
        intrcpt1 = ((2 * closest_asteroid["dist"] * asteroid_vel * cos_my_theta2) + math.sqrt(targ_det)) / (2 * (asteroid_vel**2 -bullet_speed**2))
        intrcpt2 = ((2 * closest_asteroid["dist"] * asteroid_vel * cos_my_theta2) - math.sqrt(targ_det)) / (2 * (asteroid_vel**2-bullet_speed**2))
        
        # Take the smaller intercept time, as long as it is positive; if not, take the larger one.
        if intrcpt1 > intrcpt2:
            if intrcpt2 >= 0:
                bullet_t = intrcpt2
            else:
                bullet_t = intrcpt1
        else:
            if intrcpt1 >= 0:
                bullet_t = intrcpt1
            else:
                bullet_t = intrcpt2
                
        # Calculate the intercept point. The work backwards to find the ship's firing angle my_theta1.
        intrcpt_x = closest_asteroid["aster"]["position"][0] + closest_asteroid["aster"]["velocity"][0] * bullet_t
        intrcpt_y = closest_asteroid["aster"]["position"][1] + closest_asteroid["aster"]["velocity"][1] * bullet_t
        
        my_theta1 = math.atan2((intrcpt_y - ship_pos_y),(intrcpt_x - ship_pos_x))
        
        # Lastly, find the difference betwwen firing angle and the ship's current orientation. BUT THE SHIP HEADING IS IN DEGREES.
        shooting_theta = my_theta1 - ((math.pi/180)*ship_state["heading"])
        
        # Wrap all angles to (-pi, pi)
        shooting_theta = (shooting_theta + math.pi) % (2 * math.pi) - math.pi
        
        # Pass the inputs to the rulebase and fire it
        shooting = ctrl.ControlSystemSimulation(self.targeting_control,flush_after_run=1)
        
        shooting.input['bullet_time'] = bullet_t
        shooting.input['theta_delta_fire'] = shooting_theta
        
        shooting.compute()
        
        # Get the defuzzified outputs
        turn_rate = shooting.output['ship_turn']
        
        if shooting.output['ship_fire'] >= 0:
            fire = True
        else:
            fire = False

        # Pass the inputs to the thrust rulebase
        impetus = ctrl.ControlSystemSimulation(self.ship_control,flush_after_run=1)
        impetus.input['closest_asteroid_distance'] = closest_asteroid["dist"]
        impetus.input['theta_delta_turn'] = shooting_theta
        impetus.input['ship_speed'] = ship_state["speed"]

        impetus.compute()
        
        # Get the defuzzified outputs
        thrust = impetus.output['ship_thrust']
    
        self.eval_frames +=1
        
        #DEBUG
        # print(thrust, bullet_t, shooting_theta, turn_rate, fire, closest_asteroid["dist"])
        
        # Store the closest distance in the list
        self.closest_distances.append(closest_asteroid["dist"])

        # And return your three outputs to the game simulation. Controller algorithm complete.
        return thrust, turn_rate, fire
    
    def get_closest_distances(self) -> List[float]:
        """Returns the list of closest asteroid distances."""
        return self.closest_distances

    @property
    def name(self) -> str:
        return "G17 Controller"