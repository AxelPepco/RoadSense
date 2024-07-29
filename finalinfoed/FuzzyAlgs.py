import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

#Functii de gestionare Fuzzy pentru fiecare tip de intersectie(Ex: intersectie cu 2/3/4/5 drumuri)
def Fuzzy1():
    pass

def Fuzzy2():
    pass

def Fuzzy3():
    pass


def Fuzzy4(north_cars, east_cars, south_cars, west_cars):

    
    # Se declara variabilele fuzzy pentru fiecare drum
    traffic_north_south = ctrl.Antecedent(np.arange(0, 101, 1), 'traffic_north_south')
    traffic_east_west = ctrl.Antecedent(np.arange(0, 101, 1), 'traffic_east_west')
    time_north_south = ctrl.Consequent(np.arange(0, 61, 1), 'time_north_south')
    time_east_west = ctrl.Consequent(np.arange(0, 61, 1), 'time_east_west')
    # Defineste functiile de apartenenta pentru variabilele de intrare
    traffic_north_south['low'] = fuzz.trimf(traffic_north_south.universe, [0, 0, 50])
    traffic_north_south['medium'] = fuzz.trimf(traffic_north_south.universe, [0, 50, 100])
    traffic_north_south['high'] = fuzz.trimf(traffic_north_south.universe, [50, 100, 100])

    traffic_east_west['low'] = fuzz.trimf(traffic_east_west.universe, [0, 0, 50])
    traffic_east_west['medium'] = fuzz.trimf(traffic_east_west.universe, [0, 50, 100])
    traffic_east_west['high'] = fuzz.trimf(traffic_east_west.universe, [50, 100, 100])

    # Defineste functiile de apartenenta pentru variabilele de iesire
    time_north_south['short'] = fuzz.trimf(time_north_south.universe, [0, 0, 30])
    time_north_south['medium'] = fuzz.trimf(time_north_south.universe, [0, 30, 60])
    time_north_south['long'] = fuzz.trimf(time_north_south.universe, [30, 60, 60])

    time_east_west['short'] = fuzz.trimf(time_east_west.universe, [0, 0, 30])
    time_east_west['medium'] = fuzz.trimf(time_east_west.universe, [0, 30, 60])
    time_east_west['long'] = fuzz.trimf(time_east_west.universe, [30, 60, 60])

    # Defineste regulile fuzzy
    rule1 = ctrl.Rule(traffic_north_south['high'] & traffic_east_west['low'], 
                    (time_north_south['long'], time_east_west['short']))
    rule2 = ctrl.Rule(traffic_north_south['medium'] & traffic_east_west['low'], 
                    (time_north_south['medium'], time_east_west['short']))
    rule3 = ctrl.Rule(traffic_north_south['low'] & traffic_east_west['low'], 
                    (time_north_south['short'], time_east_west['short']))
    rule4 = ctrl.Rule(traffic_north_south['low'] & traffic_east_west['medium'], 
                    (time_north_south['short'], time_east_west['medium']))
    rule5 = ctrl.Rule(traffic_north_south['low'] & traffic_east_west['high'], 
                    (time_north_south['short'], time_east_west['long']))
    rule6 = ctrl.Rule(traffic_north_south['medium'] & traffic_east_west['medium'], 
                    (time_north_south['medium'], time_east_west['medium']))
    rule7 = ctrl.Rule(traffic_north_south['high'] & traffic_east_west['high'], 
                    (time_north_south['long'], time_east_west['long']))

    # Creeaza sistemul de control
    traffic_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
    traffic_simulation = ctrl.ControlSystemSimulation(traffic_control)

    def determine_light_and_time(traffic_ns, traffic_ew):
        # Introduce valorile de trafic
        traffic_simulation.input['traffic_north_south'] = traffic_ns
        traffic_simulation.input['traffic_east_west'] = traffic_ew
        # Calculeaza rezultatul
        traffic_simulation.compute()
        
        time_ns = traffic_simulation.output['time_north_south']
        time_ew = traffic_simulation.output['time_east_west']
        
        if time_ns > time_ew:
            return 'North/South', time_ns
        else:
            return 'East/West', time_ew

    traffic_ns = north_cars + south_cars  # Densitatea de trafic pentru North-South
    traffic_ew = east_cars + west_cars  # Densitatea de trafic pentru East-West
    light, time = determine_light_and_time(traffic_ns, traffic_ew)
    return light, time


def Fuzzy5():
    pass

def Fuzzy6():
    pass

global fuzzy_functions
fuzzy_functions = [Fuzzy1, Fuzzy2, Fuzzy3, Fuzzy4, Fuzzy5, Fuzzy6]
#Functiile globale pentru apelarea din alte thread-uri
