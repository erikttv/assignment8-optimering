from copy import deepcopy
from Container import Container
class Solution:

	def __init__(self, n_bays, n_stacks, n_tiers):
		self.n_bays = n_bays
		self.n_stacks = n_stacks
		self.n_tiers = n_tiers

		self.flow_x = [[[0 for _ in range(n_tiers)] for _ in range(n_stacks)] for _ in range(n_bays)]
		self.objective = float("inf")
		self.cog = [0, 0]
		self.total_weight_containers = 0

	def copy(self):
		"""
		Make a copy of the Solution object
		:return: Copy of the object
		"""
		new_solution = Solution(self.n_bays, self.n_stacks, self.n_tiers)

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					new_solution.flow_x[bay][stack][tier] = self.flow_x[bay][stack][tier]

		new_solution.objective = self.objective
		new_solution.cog = self.cog
		new_solution.total_weight_containers = self.total_weight_containers

		return new_solution

	def construct(self):
		"""
		Simple construction heuristic.
		Takes the first container in the list, and places it in the
		first location. The next is placed in the second location and
		so on.
		"""

		i = 0

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					self.flow_x[bay][stack][tier] = i
					i += 1

	def calculate_objective(self, containers):
		"""
		Denne metoden regner ut og oppdaterer målfunksjonsverdien til Solution-objektet.
		:param containers: list of Container objects
		"""

		# Her vil vi at cog (centre of gravity) skal ligge
		gravity_goal = [self.n_bays/2.0, self.n_stacks/2.0]

		# Lager en liste som brukes til å regne ut den aktuelle cog-en
		gravity_this = [0.0, 0.0]

		sum_container_weight = 0

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):

				sum_tier = 0

				for tier in range(self.n_tiers):
					container_weight = containers[self.flow_x[bay][stack][tier]].weight
					sum_tier += container_weight
					sum_container_weight += container_weight

				gravity_this[0] += (bay - 0.5) * sum_tier
				gravity_this[1] += (stack - 0.5) * sum_tier

		gravity_this[0] /= sum_container_weight
		gravity_this[1] /= sum_container_weight

		evaluation = (gravity_goal[0] - gravity_this[0])**2 + (gravity_goal[1] - gravity_this[1])**2

		self.objective = evaluation
		self.cog = gravity_this
		self.total_weight_containers = sum_container_weight

	def print_solution(self):
		print("Current solution:")

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					print(f"Bay: {bay}, stack: {stack}, tier: {tier}, container: {self.flow_x[bay][stack][tier]}")

	def construction_improved(self, containers: Container):
		print("Oppgave 1")

		# Want to put them in by largest weight first
		containers = Container.sort_array_weight_ascending(containers)
		i = 0

		new_bays = [i for i in range(self.n_bays)]
		new_bays = self.rearrangeArray(new_bays)
		
		for bay in new_bays:
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					self.flow_x[bay][stack][tier] = containers[i].container_id
					i += 1

	# Helper function for question 2
	def rearrangeArray(self, arr) :
		new_list = []
		if len(arr)%2 ==0:
			for i in range(len(arr)//2):
				new_list.append(arr[i])
				new_list.append(arr[-i-1])
		else:
			j = 0
			for i in range(len(arr)//2):
				new_list.append(arr[j])
				new_list.append(arr[-j-1])
				j += 1
			new_list.append(j)	
		return new_list

	def local_search_two_swap(self, containers):
		print("Oppgave 2a")
		improved = False
		overall_objective = self.calculate_objective(containers)
		while not improved:
			best_local_objective = float('inf')

			best_solution = []

			for bay in range(self.n_bays):
				for stack in range(self.n_stacks):
					for tier in range(self.n_tiers):
						for bay1 in range(self.n_bays):
							for stack1 in range(self.n_stacks):
								for tier1 in range(self.n_tiers):
									alternative_solution = deepcopy(self)
         
									temp = alternative_solution.flow_x[bay][stack][tier]
									alternative_solution.flow_x[bay][stack][tier] = alternative_solution.flow_x[bay1][stack1][tier1]
									alternative_solution.flow_x[bay1][stack1][tier1] = temp
									value = alternative_solution.calculate_objective(containers)
									if value < best_local_objective:
										best_solution = [[bay, stack, tier], [bay1, stack1, tier1]]
										best_local_objective = value
          
			if best_local_objective < overall_objective:
				temp = self.flow_x[best_solution[0][0]][best_solution[0][1]][best_solution[0][2]]
				self.flow_x[best_solution[0][0]][best_solution[0][1]][best_solution[0][2]] = self.flow_x[best_solution[1][0]][best_solution[1][1]][best_solution[1][2]]
				self.flow_x[best_solution[1][0]][best_solution[1][1]][best_solution[1][2]] = temp
			else:
				improved = True

	def local_search_three_swap(self, containers):
		print("Oppgave 2b")

	def tabu_search_heuristic(self, containers, n_iterations):
		print("Oppgave 3")
