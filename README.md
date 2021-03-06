# Printed Energy Storage Cost Estimator
Estimating the manufacturing and material cost of printed energy storage devices

## Preparation
Run the following code in command line
```
pip install gspread
pip install --upgrade oauth2client
pip install PyOpenSSL
```

##How to run
1. Open command line (Terminal on a Mac) and go to the same folder these files are saved in.
2. Execute the code in interactive mode: 
```
python -i estimator.py
```
3. Create a Cost_estimator instance. 
The parameters for the Cost_estimator class are:

> Cost_estimator(recipe, dimensions, manufacturing_method, cost_source, power_performance, energy_performance)

>> * RECIPE is a dictionary with user-defined keys that name the layer (must be under 20 characters. ex. 'electrode', 'electrolyte', 'current collector').
 * Each key has a 2D list as its value: the first term is a list of 2D vectors with ingredient information, the second term is the layer thickness in microns
 * ex. {'electrode': [[['AC', mass ratio #, persisting 'p' or not persisting 'np'], ['GR', mass ratio #, 'p']], layer thickness in microns], 'electrolyte':[['BMIMBF4', mass ratio #, 'p'], 250]} 
* DIMENSIONS is a 2D vector of dimension values in meters [length, width]
* MANUFACTURING_METHOD is a string of the name of a manufacturing method ('flexographic', 'screen', 'blade coating')
* COST_SOURCE is a string of the user preference of the cost source. Options are 'Cheap Materials' (from sources like Alibaba) or 'Reliable Materials' (from sources like Argonne NL cost analyses)
* POWER_PERFORMANCE is a value with units kW/m^2
* ENERGY_PERFORMANCE is a value with units kWh/m^2
* FILENAME is an optional argument that is a string that will name the output file

Note: if you want multiple of the same layer, either put the multiple and a * as the first character in the layer name, or repeat the dictionary entry twice. The multiple* trick works for any single-digit number. Example: 
```
c = Cost_estimator({'2* electrode': [[['AC', 17, 'p'], ['AB', 1, 'p'], ['GR', 2, 'p'], ['PVDFHFP', 2.2222, 'p'], ['NMP', 17.7778, 'np'], ['BMIMBF4', 11, 'np']], 54], 'electrolyte': [[['BMIMBF4', 2, 'p'], ['PVDFHFP', 1, 'p'], ['NMP', 3, 'np']], 250], 'current collector': [[['Dupont_5025', 1, 'p']], 35]}, [1, 1], 'flexographic', 'Cheap Materials', .01, .0001, 'recipe1.csv')
```
4. Run the calculation: 
```
c.calculate_costs()
```
