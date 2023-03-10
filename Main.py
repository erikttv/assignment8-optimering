from Container import Container
from Solution import Solution
from Vessel import Vessel

if __name__ == '__main__':
	# Set data file
	#filename = "instance1.txt"
	filename = "instance2.txt"

	# Read from data file
	with open(filename, "r") as datafile:
		data = datafile.readlines()

		vessel_dimensions = list(map(int, data[:3]))

		weights = list(map(int, data[3:]))

	containers = []

	# dette er det samme som Vessel(vessel_dimensions[0], vessel_dimensions[1], vessel_dimensions[2])
	vessel = Vessel(*vessel_dimensions)

	for container_id in range(len(weights)):
		containers.append(Container(container_id, weights[container_id]))

	# containers is an array of Container objects
	# vessel is a Vessel object

	# Create a Solution object for the initial solution
	initial_solution = Solution(vessel.n_bays, vessel.n_stacks, vessel.n_tiers)

	# Construct an initial solution
	initial_solution.construct()

	# OPPGAVE 1
	initial_solution.construction_improved(containers)
	# Implementer denne i Solution.py

	# Sortere containere etter vekt slik:
	# containers_descending = Container.sort_array_weight_descending(containers)
	# containers_ascending = Container.sort_array_weight_ascending(containers)
	###########################################################################

	# Print the initial solution to command window
	initial_solution.print_solution()

	# Evaluate the initial solution
	initial_solution.calculate_objective(containers)
	print(initial_solution.objective)

	# Improvement phase

	# Create a copy of the initial solution
	new_solution = initial_solution.copy()

	# OPPGAVE 2A
	new_solution.local_search_two_swap(containers)
	# Implementer denne i Solution.py
	print(new_solution.objective)

	# OPPGAVE 2B
	new_solution.local_search_three_swap(containers)
	# Implementer denne i Solution.py
	print(new_solution.objective)

	# OPPGAVE 3
	n_iterations = 100
	new_solution.tabu_search_heuristic(containers, n_iterations)
	# Implementer denne i Solution.py
	print(new_solution.objective)
