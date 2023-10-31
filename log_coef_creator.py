import json
import numpy as np

multiple = 1

basic_coefficient = 5
power = 50

new_list = []

for i in range (0, 55):
    one_cf = np.log2(pow(1+basic_coefficient/100,multiple))*(1+power/100)+0.15
    multiple+=1
    print(one_cf)
    new_list.append(one_cf)
print (new_list)
with open('logarithmic_coefficients.json', 'w') as cf:
    json.dump(new_list, cf)
