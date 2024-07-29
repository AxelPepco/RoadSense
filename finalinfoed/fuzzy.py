import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define fuzzy variables for arriving cars and queue size
arrival = ctrl.Antecedent(np.arange(0, 11, 1), 'arrival')
queue = ctrl.Antecedent(np.arange(0, 11, 1), 'queue')
extension = ctrl.Consequent(np.arange(-5, 10, 1), 'extension')  # extension in seconds

# Define membership functions for arrival and queue variables
arrival['few'] = fuzz.trimf(arrival.universe, [0, 0, 2])
arrival['small'] = fuzz.trimf(arrival.universe, [1, 3, 5])
arrival['medium'] = fuzz.trimf(arrival.universe, [4, 6, 8])
arrival['many'] = fuzz.trimf(arrival.universe, [7, 9, 10])

queue['few'] = fuzz.trimf(queue.universe, [0, 0, 2])
queue['small'] = fuzz.trimf(queue.universe, [1, 3, 5])
queue['medium'] = fuzz.trimf(queue.universe, [4, 6, 8])
queue['many'] = fuzz.trimf(queue.universe, [7, 9, 10])

# Define membership functions for extension variable
extension['negative'] = fuzz.trimf(extension.universe, [-5, -5, -5])
extension['zero'] = fuzz.trimf(extension.universe, [0, 0, 0])
extension['short'] = fuzz.trimf(extension.universe, [0, 0, 0])
extension['medium'] = fuzz.trimf(extension.universe, [4, 4, 4])
extension['long'] = fuzz.trimf(extension.universe, [9, 9, 9])

# Define fuzzy rules
rules = [
    ctrl.Rule(arrival['few'] & queue['few'], extension['negative']),
    ctrl.Rule(arrival['few'] & queue['small'], extension['negative']),
    ctrl.Rule(arrival['few'] & queue['medium'], extension['negative']),
    ctrl.Rule(arrival['few'] & queue['many'], extension['negative']),
    ctrl.Rule(arrival['small'] & queue['few'], extension['zero']),
    ctrl.Rule(arrival['small'] & queue['small'], extension['zero']),
    ctrl.Rule(arrival['small'] & queue['medium'], extension['zero']),
    ctrl.Rule(arrival['small'] & queue['many'], extension['zero']),
    ctrl.Rule(arrival['medium'] & queue['few'], extension['medium']),
    ctrl.Rule(arrival['medium'] & queue['small'], extension['medium']),
    ctrl.Rule(arrival['medium'] & queue['medium'], extension['medium']),
    ctrl.Rule(arrival['medium'] & queue['many'], extension['medium']),
    ctrl.Rule(arrival['many'] & queue['few'], extension['long']),
    ctrl.Rule(arrival['many'] & queue['small'], extension['long']),
    ctrl.Rule(arrival['many'] & queue['medium'], extension['long']),
    ctrl.Rule(arrival['many'] & queue['many'], extension['long']),
]

# Create control system
extension_ctrl = ctrl.ControlSystem(rules)

# Function to determine green light duration for each direction
def get_extension(arrival_count, queue_count):
    extension_simulation = ctrl.ControlSystemSimulation(extension_ctrl)
    extension_simulation.input['arrival'] = arrival_count
    extension_simulation.input['queue'] = queue_count
    try:
        extension_simulation.compute()
        return extension_simulation.output['extension']
    except ValueError as e:
        print(f"Error in calculating extension: {e}")
        return 0  # Return zero extension if calculation fails

# Main function to determine green light order and duration
def traffic_light_management(north_arrival, north_queue, east_arrival, east_queue, south_arrival, south_queue, west_arrival, west_queue, initial_duration=20):
    # Calculate extensions
    north_extension = get_extension(north_arrival, north_queue)
    south_extension = get_extension(south_arrival, south_queue)
    east_extension = get_extension(east_arrival, east_queue)
    west_extension = get_extension(west_arrival, west_queue)

    # Calculate average extensions
    north_south_extension = (north_extension + south_extension) / 2
    east_west_extension = (east_extension + west_extension) / 2
    
    # Calculate green durations
    north_south_duration = initial_duration + north_south_extension
    east_west_duration = initial_duration + east_west_extension
    
    print(f"East-West, Time: {east_west_duration:.2f} seconds")
    print(f"North-South, Time: {north_south_duration:.2f} seconds")

# Get user input for number of cars
def main():
    north_arrival = int(input("Enter number of arriving cars from the North: "))
    north_queue = int(input("Enter number of queued cars from the North: "))
    east_arrival = int(input("Enter number of arriving cars from the East: "))
    east_queue = int(input("Enter number of queued cars from the East: "))
    south_arrival = int(input("Enter number of arriving cars from the South: "))
    south_queue = int(input("Enter number of queued cars from the South: "))
    west_arrival = int(input("Enter number of arriving cars from the West: "))
    west_queue = int(input("Enter number of queued cars from the West: "))

    traffic_light_management(north_arrival, north_queue, east_arrival, east_queue, south_arrival, south_queue, west_arrival, west_queue)

if __name__ == "__main_1_":
    main()