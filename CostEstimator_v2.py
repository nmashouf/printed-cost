### COST ESTIMATOR FOR PRINTED ENERGY STORAGE ###
### By Neeka Mashouf ###
### nmashouf [at] berkeley [dot] edu ###

"""
What you need to run this:
Python 3
Command line interface for your operating system (Terminal on a Mac)
GSpread --> you can download this by entering "pip install gspread" into the command line

How to run:
1. Open command line (Terminal on a Mac) and go to the same folder this file is saved in.
2. Execute the code in interactive mode: python -i CostEstimator.py
3. Create a Cost_estimator instance (example -->) : 
c = Cost_estimator({'electrode': [['AC', 17], ['AB', 1], ['GR', 2], ['PVDFHFP', 5], ['NMP', 40]], 'electrolyte': [['BMIMBF4', 11]]}, [1, 1], 'flexographic', 'Cheap Materials')
4. Run the calculation: c.calculate_costs()

"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Cost Estimator-86291a3a7939.json', scope)
gc = gspread.authorize(credentials)

#Initialize library of components and their details
database = gc.open("Printed Energy Storage Costs and Properties")
# Database and sources here: https://docs.google.com/spreadsheets/d/1mUYFqidkvMZirKhc2jpdz5QB0OMoLIjFWDUVO9FMF5A/edit?usp=sharing

class Cost_estimator:
	"""Estimates the cost of a specific recipe with lxwxt dimensions using manufacturing_method.

	RECIPE is a dictionary with keys 'electrode' (separate 'anode' and 'cathode' for batteries) and 'electrolyte', with values that are lists of 2D vectors with ingredient information
		ex. {'electrode': [['AC', mass ratio #], ['GR', mass ratio #]], 'electrolyte':['BMIMBF4': mass ratio #]}. Names are AC, AB, GR, PVDFHFP, NMP, BMIMBF4, ZN, MNO2
	DIMENSIONS is a 2D vector of dimension values in meters [length, width]
	MANUFACTURING_METHOD is a string of the name of a manufacturing method ('flexographic', 'screen', 'blade coating')
	COST_SOURCE is a string of the user preference of the cost source. Options are 'Cheap Materials' (from sources like Alibaba) or 'Reliable Materials' (from sources like Argonne NL cost analyses)
	PERFORMANCE is a value with units kW/m^2
	"""
	
	def __init__(self, recipe, dimensions, manufacturing_method, cost_source, performance):
		self.recipe = recipe
		self.dimensions = dimensions
		self.manufacturing_method = manufacturing_method
		self.performance = performance
		self.electrode_vol_in_ml = 0
		self.electrolyte_vol_in_ml = 0
		self.total_cost = 0
		self.user_specified_materials_worksheet = database.worksheet(cost_source)
		self.manufacturing_worksheet = database.worksheet("Manufacturing Method")
		self.log_worksheet = database.worksheet("Log")

	def get_ratio(self, component):
		return component[1]

	def get_name(self, component):
		return component[0]

	def get_density(self, name):
		cell = self.user_specified_materials_worksheet.find(name)
		row_number = cell.row
		density = float(self.user_specified_materials_worksheet.acell('E'+str(row_number)).value)
		return density

	def get_material_cost(self, name):
		cell = self.user_specified_materials_worksheet.find(name)
		row_number = cell.row
		mat_cost = float(self.user_specified_materials_worksheet.acell('C'+str(row_number)).value)
		return mat_cost

	def get_manu_cost(self, manu_method, print_2D_dim):
		cell = self.manufacturing_worksheet.find(manu_method)
		row_number = cell.row
		manu_cost = float(self.manufacturing_worksheet.acell('C'+str(row_number)).value)
		return manu_cost*print_2D_dim

	def get_manu_thickness(self, manu_method):
		cell = self.manufacturing_worksheet.find(manu_method)
		row_number = cell.row
		manu_thickness = float(self.manufacturing_worksheet.acell('E'+str(row_number)).value)
		return manu_thickness

	def spaces(self, n):
		if n == 0:
			return ''
		return ' ' + self.spaces(n-1)


### Abstraction Barrier ###


	def calc_layer_cost(self, key):
		layer_total_cost = 0
		if key == 'electrode':
			volume = self.electrode_vol_in_ml
		elif key == 'cathode' or key == 'anode':
			volume = self.electrode_vol_in_ml/2
		elif key == 'electrolyte':
			volume = self.electrolyte_vol_in_ml
		else:
			return 'layer not recognized!'
		layer_recipe = self.recipe[key]
		print('INGREDIENT          LAYER          COST')
		for ingredient_pair in layer_recipe:
			ingredient_name = self.get_name(ingredient_pair)
			volume_contribution = self.get_ratio(ingredient_pair)*volume
			mass_contribution = volume_contribution*self.get_density(ingredient_name)
			cost_contribution = mass_contribution*self.get_material_cost(ingredient_name)
			print(str(ingredient_name) + self.spaces(20-len(ingredient_name)) + key + self.spaces(15-len(key)) + str(cost_contribution)[:6])
			layer_total_cost += cost_contribution
		return layer_total_cost

	def calculate_costs(self):
		self.convert_to_vol_ratio()
		_2D_dim = self.dimensions[0]*self.dimensions[1]
		self.manufacturing_thickness = self.get_manu_thickness(self.manufacturing_method)
		self.electrode_vol_in_ml = _2D_dim*self.manufacturing_thickness*1000000*2 # 2 is for 2 electrodes
		self.electrolyte_vol_in_ml = .00017*_2D_dim*1000000
		manufacturing_cost = self.get_manu_cost(self.manufacturing_method, _2D_dim)
		print(' ')
		print ('Assuming an electrolyte thickness of 170 micrometers and a manufacturing-method-dependent electrode thickness of ' + str(self.manufacturing_thickness*100000) + ' meters')
		print('MANUFACTURING COST for ' + self.manufacturing_method + ' = ' + str(manufacturing_cost))
		self.total_cost = manufacturing_cost
		print(' ')
		print('MATERIAL COSTS:')
		for key in self.recipe:
			self.total_cost += self.calc_layer_cost(key)
		print(' ')
		print('TOTAL COST = $' + str(self.total_cost)[:4] + ' for ' + str(_2D_dim) + ' square meter(s)')
		print(' ')
		print('PERFORMANCE = $' + str(self.total_cost/self.performance)[:4] + '/kW') # total cost times user-defined m^2/kW value

	def convert_to_vol_ratio(self):
		"""Retrieves the mass ratio of each component in the recipe, calculates
		the volume ratio using component_properties, and then replaces the mass
		ratio in recipe with the volume ratio"""
		for key in self.recipe: # iterate through each layer
			total_vol = 0
			vol_dict = {}
			layer_recipe = self.recipe[key]
			for i in range(len(layer_recipe)): # iterate through each ingredient
				ingredient_pair = layer_recipe[i]
				mass_ratio = self.get_ratio(ingredient_pair) #get mass ratio from component_recipe in format ['name', mass ratio]
				ingredient_name = self.get_name(ingredient_pair)
				volume = mass_ratio/self.get_density(ingredient_name) #mass_ratio times bulk density
				vol_dict[ingredient_name] = volume
				total_vol += volume
			for i in range(len(layer_recipe)):
				ingredient_name = self.get_name(self.recipe[key][i])
				new_vol_frac = vol_dict[ingredient_name]/total_vol
				self.recipe[key][i][1] = new_vol_frac





