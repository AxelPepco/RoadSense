import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Definirea variabilelor fuzzy
victories = ctrl.Antecedent(np.arange(0, 51, 1), 'victories')
performance = ctrl.Consequent(np.arange(0, 101, 1), 'performance')

# Definirea funcțiilor de apartenență pentru numărul de victorii
victories['few'] = fuzz.trimf(victories.universe, [0, 0, 10])
victories['average'] = fuzz.trimf(victories.universe, [5, 20, 35])
victories['many'] = fuzz.trimf(victories.universe, [30, 50, 50])

# Definirea funcțiilor de apartenență pentru performanță
performance['poor'] = fuzz.trimf(performance.universe, [0, 0, 50])
performance['average'] = fuzz.trimf(performance.universe, [25, 50, 75])
performance['good'] = fuzz.trimf(performance.universe, [50, 100, 100])

# Vizualizarea funcțiilor de apartenență (opțional)
victories.view()
performance.view()

# Definirea regulilor fuzzy
rule1 = ctrl.Rule(victories['few'], performance['poor'])
rule2 = ctrl.Rule(victories['average'], performance['average'])
rule3 = ctrl.Rule(victories['many'], performance['good'])

# Crearea unui sistem de control fuzzy
performance_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
performance_sim = ctrl.ControlSystemSimulation(performance_ctrl)

# Testarea sistemului cu un exemplu de 15 victorii
performance_sim.input['victories'] = 15
performance_sim.compute()

print(f"Performanța estimată: {performance_sim.output['performance']}")

# Vizualizarea rezultatului
performance.view(sim=performance_sim)
