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
3. Create a Cost_estimator instance (example -->) : 
```
c = Cost_estimator({'electrode': [['AC', 17], ['AB', 1], ['GR', 2], ['PVDFHFP', 5], ['NMP', 40]], 'electrolyte': [['BMIMBF4', 1], ['PVDFHFP', 1]]}, [1, 1], 'flexographic', 'Cheap Materials', .0000001/.000001, 1, ['GR'])
```
4. Run the calculation: 
```
c.calculate_costs()
```
